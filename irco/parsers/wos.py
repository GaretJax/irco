from __future__ import print_function

import csv
import re
import pprint

from ftfy import fix_text

from irco.authors import Author
from . import base


class LineGetter(object):
    def __init__(self, stream):
        self.value = ''
        self.stream = stream

    def __iter__(self):
        for l in self.stream:
            self.value = l
            l = l.encode('utf-8').rstrip('\r')
            if l.endswith('\t'):
                l = l[:-1]
            yield l

    def get(self):
        return self.value.strip()


class Tokenizer(base.Tokenizer):
    FORMAT = 'webofscience-tsv'
    FIELDS = {
        'TI': 'title',
        'PY': 'year',
        'PT': 'type',
        'C1': 'authors_with_affiliations',
        'TC': 'times_cited'
    }

    def __init__(self, encoding='utf8'):
        self.encoding = encoding

    def tokenize(self, stream):
        self.stream = stream
        self.line = 2
        self.header_row = next(self.stream).rstrip('\r') + '\n'
        self.stream.seek(0)
        self.lines = LineGetter(self.stream)
        self.reader = csv.DictReader(self.lines, delimiter='\t')
        self.reader.fieldnames = [self._get_key(f) for f in
                                  self.reader.fieldnames]
        return self

    def __iter__(self):
        return self

    def next(self):
        row = next(self.reader)
        record = base.Record(
            self.FORMAT,
            self.header_row + self.lines.get()
        )
        record.source = (self.stream.name, self.line)
        record.update(row)
        self.line += 1

        return record

    def _get_key(self, k):
        k = fix_text(unicode(k, self.encoding))
        k = str(k.encode('ascii', 'ignore'))
        k = self.FIELDS.get(k, k)
        return k


class Parser(base.Parser):
    def __init__(self, encoding='utf8'):
        self.encoding = encoding

    def parse_record(self, record):
        for k, v in record.iteritems():
            if k is None:
                raise ValueError('Incorrectly parsed row')
            record[k] = self._get_value(v)
        return record

    def _get_value(self, v):
        v = unicode(v, self.encoding)
        return fix_text(v)


class BaseValuesProcessor(base.Processor):
    pubtypes = {
        'J': 'journal',
        'C': 'conference',
        'B': 'book',
        'P': 'patent',
        'S': 'book in series',
    }

    def process_record(self, record):
        try:
            record['type'] = self.pubtypes[record['type']]
        except KeyError:
            raise ValueError('Unknown publication type: {}'.format(
                record['type']))
        record['times_cited'] = int(record['times_cited'])
        unique_id = record.pop('UT')
        record.unique_source_id = 'wos/' + unique_id.split(':', 1)[1]
        return record


class AffiliationsProcessor(base.Processor):
    splitter = re.compile(r'\[([^\]]+)] ([^;]+)(?:; |$)')

    def __init__(self, include_ambiguous):
        self.include_ambiguous_affiliations = include_ambiguous

    def initialize(self, pipeline):
        self.pipeline = pipeline
        self.unmatched_authors = open('unmatched_authors.log', 'w')
        pipeline.add_metric('corresponding_author_unmatched',
                            'Records wixth unmatched corr. auth.')
        pipeline.add_metric('corresponding_author_undefined',
                            'Records with undefined corr. auth.')
        pipeline.add_metric('ambiguous_author_affiliations',
                            'Records with ambiguous auth. aff.')

    def process_record(self, record):
        record['institutions'] = []
        record['authors'] = []

        affiliations = self.splitter.findall(
            record['authors_with_affiliations'].strip())

        if not affiliations:
            aut = record['AF'].split('; ')
            aff = record['authors_with_affiliations'].split('; ')
            if len(aut) == len(aff):
                affiliations = list(zip(aut, aff))
            elif len(aff) == 1:
                affiliations = [(a, aff[0]) for a in aut]
            else:
                self.pipeline.inc_metric('ambiguous_author_affiliations')
                print('-' * 80)
                print(u'Ambiguous author affiliations for "{title}":'.format(
                    **record))
                print(' Authors:')
                for a in aut:
                    print('  * {}'.format(a))
                print(' Affiliations:')
                for a in aff:
                    print('  * {}'.format(a))
                print('-' * 80)
                if self.include_ambiguous_affiliations:
                    # Set all author affiliations to the first institution in
                    # the list, and set the ambiguous flag...
                    record['ambiguous_affiliations'] = True
                    affiliations = [(a, aff[0]) for a in aut]
                else:
                    return None

        # TODO: Some authors could have two affiliations! This should be
        # checked here and a warning raised.

        for i, (authors, institution) in enumerate(affiliations):
            record['institutions'].append(institution)

            for a in authors.split('; '):
                author = Author(a)
                record['authors'].append((author, i))

        if record['RP']:
            t = ' (reprint author)'
            corresponding = record['RP'][:record['RP'].find(t)]
            corresponding = Author(corresponding.strip())
            t += ', '
            institution = record['RP'][record['RP'].find(t) + len(t):]

            match = corresponding.find_best_match(
                [a[0] for a in record['authors']])
            if not match:
                self.pipeline.inc_metric('corresponding_author_unmatched')
                print('-' * 80)
                print('No corresponding author match found for:')
                print('  {!r}/{!r}'.format(record['title'],
                                           corresponding.name))
                names = (a[0].name for a in record['authors'])
                pprint.pprint((corresponding.name, 0, tuple(names)),
                              self.unmatched_authors)
                print('-' * 80)
                return None
            else:
                for i, (a, institution_id) in enumerate(record['authors']):
                    if a is match:
                        record['corresponding_author'] = i
                        curr_inst = record['institutions'][institution_id]
                        if institution != curr_inst:
                            record['institutions'].append(institution)
                            record['authors'][i] = (
                                a, len(record['institutions']) - 1)
                        break
        else:
            self.pipeline.inc_metric('corresponding_author_undefined')
            record['corresponding_author'] = 0
            print (u'Undefined corresponding author for "{}", selecting "{}"'
                   .format(record['title'], record['authors'][0][0].name))
        return record


def pipeline(encoding, **kwargs):
    include_ambiguous = kwargs.pop('include_ambiguous', False)
    return base.Pipeline(
        Tokenizer(encoding),
        Parser(encoding),
        [
            BaseValuesProcessor(),
            AffiliationsProcessor(include_ambiguous=include_ambiguous),
        ],
        encoding,
    )
