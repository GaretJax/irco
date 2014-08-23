import csv
import re
import urlparse

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
            yield l

    def get(self):
        return self.value.strip()


class Tokenizer(base.Tokenizer):
    FORMAT = 'scopus-csv'

    def __init__(self, encoding='utf8'):
        self.encoding = encoding

    def tokenize(self, stream):
        self.stream = stream
        self.line = 2
        self.header_row = next(self.stream)
        self.stream.seek(0)
        self.lines = LineGetter(self.stream)
        self.reader = csv.DictReader(self.lines)
        self.reader.fieldnames = [self._get_key(f) for f in
                                  self.reader.fieldnames]
        return self

    def __iter__(self):
        return self

    def next(self):
        row = next(self.reader)
        record = base.Record(
            self.FORMAT,
            unicode(self.header_row + self.lines.get(), self.encoding)
        )
        record.source = (self.stream.name, self.line)
        record.update(row)
        self.line += 1

        return record

    def _get_key(self, k):
        k = fix_text(unicode(k, self.encoding))
        k = k.lower()
        k = re.sub(r'[\s.-]+', '_', k).strip('_')
        return str(k)


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
    def process_record(self, record):
        params = urlparse.parse_qs(urlparse.urlparse(record['link']).query)
        record.unique_source_id = 'scopus/' + params['eid'][0]
        return record


class AffiliationsProcessor(base.Processor):
    def process_record(self, record):
        affiliations = record['authors_with_affiliations'].split('; ')

        institutions = {}
        authors = []

        i = 0

        for a in affiliations:
            chunks = a.split(', ', 2)

            if len(chunks) > 2:
                institution = chunks[2]
                if institution not in institutions:
                    institutions[institution] = i
                    i += 1

                affiliation = institutions[institution]
            else:
                affiliation = None

            author = Author(', '.join(chunks[:2]))
            authors.append((author, affiliation))

        record['institutions'] = {v: k for k, v in institutions.iteritems()}
        record['authors'] = authors
        return record


def pipeline(encoding, **kwargs):
    return base.Pipeline(
        Tokenizer(),
        Parser(),
        [
            BaseValuesProcessor(),
            AffiliationsProcessor(),
        ]
    )
