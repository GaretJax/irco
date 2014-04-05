import csv
import re
import codecs

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
        k = str(k)
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

    def initialize(self, pipeline):
        self.pipeline = pipeline
        pipeline.add_metric('corresponding_author_unmatched',
                            'Records with unmatched corr. auth.')
        pipeline.add_metric('corresponding_author_undefined',
                            'Records with undefined corr. auth.')

    def process_record(self, record):
        record['institutions'] = {}
        record['authors'] = []

        affiliations = self.splitter.findall(
            record['authors_with_affiliations'].strip())

        if not affiliations:
            affiliations = [
                (record['AF'], record['authors_with_affiliations'])
            ]

        # TODO: Some authors could have two affiliations! This should be
        # checked here and a warning raised.

        for i, (authors, institution) in enumerate(affiliations):
            record['institutions'][i] = institution

            for a in authors.split('; '):
                author = Author(a)
                record['authors'].append((author, i))

        corresponding = record['RP']

        if corresponding:
            corresponding = corresponding[:corresponding.find(' (reprint author)')]
            corresponding = Author(corresponding.strip())

            match = corresponding.find_best_match([a for a, _ in record['authors']])
            if not match:
                self.pipeline.inc_metric('corresponding_author_unmatched')
                print 'No corresponding author match found for:'
                print repr(record['title'])
            else:
                for i, (a, _) in enumerate(record['authors']):
                    if a is match:
                        record['corresponding_author'] = i
                        break
        else:
            self.pipeline.inc_metric('corresponding_author_undefined')
            print 'No corresponding author defined for:'
            print repr(record['title'])
        return record


class Pipeline(base.Pipeline):
    def open(self, path):
        self._opened_files += 1
        return codecs.open(path, 'rb', encoding='utf_16')


pipeline = Pipeline(
    Tokenizer(),
    Parser(),
    [
        BaseValuesProcessor(),
        AffiliationsProcessor(),
    ]
)
