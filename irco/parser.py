import re


class IgnoreField(Exception):
    pass


class Parser(object):

    KEY_MAPPING = {}

    def __init__(self, value_parser):
        self.value_parser = value_parser

    def get_key(self, k):
        k = k.lower()
        k = re.sub(r'[\s-]+', '_', k)
        return self.KEY_MAPPING.get(k, k)

    def get_value(self, k, v):
        func = getattr(self.value_parser, k, lambda x: x)
        return func(v)

    def parse_line(self, line):
        k, v = line.split(':', 1)
        k = self.get_key(k)
        v = self.get_value(k, v)
        return k, v

    def parse_record(self, record_id, record_lines):
        record = {
            'id': record_id,
        }

        for line in record_lines:
            try:
                k, v = self.parse_line(line)
            except ValueError:
                print 'Error in line: {!r}'.format(line)
                continue
            except IgnoreField:
                continue
            record[k] = v

        return record

    def get_records(self, fh):
        record = None
        record_id = None

        for line in fh:
            match = re.match(r'<RECORD (\d+)>', line)
            if match is not None:
                next_record_id = int(match.group(1))
                if next_record_id > 1:
                    yield self.parse_record(record_id, record)
                record = []
                record_id = next_record_id
            else:
                line = line.strip()
                if line:
                    record.append(line)

        if record:
            yield self.parse_record(record_id, record)

    def parse(self, fh):
        return self.get_records(fh)


class ValueParser(object):
    def authors(self, v):
        v = v.split('; ')
        authors = (re.search('^(.*) \((\d+)\)$', a).groups() for a in v)
        authors = ((a[0], int(a[1])) for a in authors)
        return list(authors)

    def author_affiliation(self, v):
        v = v.split('; ')
        affiliations = (re.search('^\((\d+)\) (.*)$', a).groups() for a in v)
        affiliations = {int(k): v for k, v in affiliations}
        return affiliations

    def publication_year(self, v):
        return int(v)

    def abstract(self, v):
        raise IgnoreField()


def parse(fh):
    return Parser(ValueParser()).parse(fh)
