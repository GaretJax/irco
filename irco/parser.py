import re
from irco.authors import Author


class IgnoreField(Exception):
    pass


class Parser(object):

    KEY_MAPPING = {}

    def __init__(self, value_parser, record_processor):
        self.value_parser = value_parser
        self.record_processor = record_processor

    def get_key(self, k):
        k = k.lower()
        k = re.sub(r'[\s-]+', '_', k)
        return self.KEY_MAPPING.get(k, k)

    def get_value(self, k, v):
        func = getattr(self.value_parser, k, lambda x: x)
        return func(v)

    def parse_line(self, line):
        if line.startswith('Compilation and indexing terms'):
            raise IgnoreField()
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

    def postprocess_record(self, record):
        try:
            return self.record_processor.process(record)
        except Exception as e:
            import pprint
            print
            print '---'
            print 'Error while postprocessing record'
            print
            print e
            print
            pprint.pprint(record)
            print
            raise

    def get_records(self, fh):
        record = None
        record_id = None

        for line in fh:
            match = re.match(r'<RECORD (\d+)>', line)
            if match is not None:
                next_record_id = int(match.group(1))
                if next_record_id > 1:
                    record = self.parse_record(record_id, record)
                    yield self.postprocess_record(record)
                record = []
                record_id = next_record_id
            else:
                line = line.strip()
                if line:
                    record.append(line)

        if record:
            record = self.parse_record(record_id, record)
            yield self.postprocess_record(record)

    def parse(self, fh):
        return self.get_records(fh)


class AuthorList(list):
    def __str__(self):
        return '; '.join(['{0.name} ({1})'.format(*a) for a in self])


class Affiliations(dict):
    def __str__(self):
        return '; '.join(['({}) {}'.format(k, v) for k, v in self.iteritems()])


class ValueParser(object):
    def authors(self, v):
        v = v.split('; ')
        authors = (re.search('^(.*) \((\d+)\)$', a).groups() for a in v)
        authors = ((Author(a[0]), int(a[1])) for a in authors)
        return AuthorList(authors)

    def author_affiliation(self, v):
        v = v.split('; ')
        affiliations = (re.search('^\((\d+)\) (.*)$', a).groups() for a in v)
        affiliations = {int(k): v for k, v in affiliations}
        return Affiliations(affiliations)

    def corresponding_author(self, v):
        return Author(v)

    def publication_year(self, v):
        return int(v)

    def abstract(self, v):
        raise IgnoreField()


class RecordProcessor(object):
    def process(self, record):
        if 'corresponding_author' in record:
            self.get_affiliation(record)

        # Convert back to strings
        record['authors'] = record['authors']
        record['author_affiliation'] = record['author_affiliation']
        record['corresponding_author'] = str(record['corresponding_author'])

        return record

    def get_affiliation(self, record):
        corresponding_author = record['corresponding_author']

        for author, affiliation in record['authors']:
            if corresponding_author == author:
                affiliation = record['author_affiliation'][affiliation]
                break
        else:
            raise ValueError('Could not find the corresponding author '
                             'affiliation in record {}'.format(record['id']))

        record['corresponding_author_affiliation'] = affiliation


def parse(fh):
    return Parser(ValueParser(), RecordProcessor()).parse(fh)
