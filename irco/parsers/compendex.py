import re
from ftfy import fix_text

from . import base
from irco.authors import Author


class Tokenizer(base.Tokenizer):
    FORMAT = 'compendex-ascii'

    def _make_record(self, stream, line, lines):
        value = '\n'.join(lines)
        record = base.Record(self.FORMAT, value)
        record.source = (stream.name, line)
        return record

    def tokenize(self, stream):
        record = []

        for i, line in enumerate(stream):
            if re.match(r'<RECORD (\d+)>', line) is not None:
                if record:
                    yield self._make_record(stream, i, record)
                record = []
            else:
                line = line.strip()
                if line:
                    record.append(line)

        if record:
            yield self._make_record(stream, i, record)


class Parser(base.Parser):
    def __init__(self, encoding='utf8'):
        self.encoding = encoding

    def parse_record(self, record):
        for line in record.raw_value.split('\n'):
            if line.startswith('Compilation and indexing terms'):
                continue

            k, v = line.split(':', 1)
            k, v = self._get_key(k), self._get_value(v)
            record[k] = v

        return record

    def _get_value(self, v):
        v = unicode(v, self.encoding)
        return fix_text(v)

    def _get_key(self, k):
        k = k.lower()
        k = re.sub(r'[\s-]+', '_', k)
        return k


class BaseValuesProcessor(base.Processor):
    def process_record(self, record):
        record.unique_source_id = 'evillage/' + record['accession_number']

        record['year'] = int(record['publication_year'])
        del record['publication_year']

        return record


class AuthorsProcessor(base.ValueProcessor):
    key = 'authors'

    def process_value(self, authors):
        authors = authors.split('; ')
        authors = (re.search(r'^(.*) \((\d+)\)$', a).groups() for a in authors)
        authors = ((Author(a[0]), int(a[1])) for a in authors)
        return list(authors)


class InstitutionsProcessor(base.ValueProcessor):
    key = ('author_affiliation', 'institutions')

    def process_value(self, institutions):
        regex = re.compile(r'^\((\d+)\) (.*)$')
        institutions = institutions.split('; ')
        institutions = (regex.search(i) for i in institutions)
        institutions = (i.groups() for i in institutions if i is not None)
        return {int(k): v for k, v in institutions}


def pipeline(encoding):
    return base.Pipeline(
        Tokenizer(),
        Parser(),
        [
            BaseValuesProcessor(),
            AuthorsProcessor(),
            InstitutionsProcessor(),
        ]
    )
