import re
import htmlentitydefs

from irco.authors import Author
from irco import errors


class IgnoreField(Exception):
    pass


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, unicode(text))


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
        v = unescape(v)
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

    def get_records(self, fh, records=None):
        record = None
        record_id = None

        if records:
            records = set(records)

        for line in fh:
            match = re.match(r'<RECORD (\d+)>', line)
            if match is not None:
                next_record_id = int(match.group(1))
                if next_record_id > 1:
                    record = self.process_record(records, record_id, record)
                    if record:
                        yield record
                record = []
                record_id = next_record_id
            else:
                line = line.strip()
                if line:
                    record.append(line)

        if record:
            record = self.parse_record(record_id, record)
            if record:
                yield record

    def process_record(self, records, record_id, record):

        if not records or record_id in records:
            try:
                record = self.parse_record(record_id, record)
            except:
                raise
                print 'Could not parse record', record_id
            else:
                return self.postprocess_record(record)

    def parse(self, fh, records=None):
        return self.get_records(fh, records)


class AuthorList(list):
    def __unicode__(self):
        return u'; '.join([u'{0.name} ({1})'.format(*a) for a in self])


class Affiliations(dict):
    def __unicode__(self):
        affiliations = [u'({}) {}'.format(k, v) for k, v in self.iteritems()]
        return u'; '.join(affiliations)


class ValueParser(object):
    def authors(self, v):
        v = v.split('; ')
        authors = (re.search(r'^(.*) \((\d+)\)$', a).groups() for a in v)
        authors = ((Author(a[0]), int(a[1])) for a in authors)
        return AuthorList(authors)

    def author_affiliation(self, v):
        v = v.split('; ')
        affiliations = []
        for a in v:
            match = re.search(r'^\((\d+)\) (.*)$', a)
            if match is None:
                continue
            affiliations.append(match.groups())
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
        try:
            record['corresponding_author'] = unicode(
                self.get_affiliation(record))
        except (errors.NoCorrespondingAuthor, errors.NoAffiliationField,
                errors.NoAffiliationMatch):
            pass

        return record

    def get_affiliation(self, record):
        try:
            corresponding_author = record['corresponding_author']
        except KeyError:
            raise errors.NoCorrespondingAuthor(record)

        try:
            affiliations = record['author_affiliation']
        except KeyError:
            raise errors.NoAffiliationField(record)

        for author, affiliation in record['authors']:
            if corresponding_author == author:
                if affiliation == 0:
                    continue
                affiliation = affiliations[affiliation]
                break
        else:
            p = max(len(corresponding_author) + 5, 50)
            print '=' * 80
            print 'No affiliation for record {}, ignoring'.format(record['id'])
            print ' Corresponding author:'
            print u'    {0:{1}s} {0!r}'.format(corresponding_author, p)
            print ' Possible candidates:'
            for a in record['authors']:
                print u'    {0:{1}s} {0!r}'.format(a[0], p)
            print '=' * 80
            raise errors.NoAffiliationMatch(record)

        return affiliation


def parse(fh, records=None):
    return Parser(ValueParser(), RecordProcessor()).parse(fh, records)
