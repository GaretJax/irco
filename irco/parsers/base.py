import abc
import inspect


class IgnoreRecord(Exception):
    pass


class Tokenizer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def tokenize(self, stream):
        pass


class Parser(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse_record(self, record):
        pass


class Processor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process_record(self, record):
        pass


class ValueProcessor(Processor):

    @abc.abstractproperty
    def key(self):
        pass

    @abc.abstractmethod
    def process_value(self, value):
        pass

    def process_record(self, record):
        if isinstance(self.key, basestring):
            oldkey = newkey = self.key
        else:
            oldkey, newkey = self.key
        record[newkey] = self.process_value(record[oldkey])

        if newkey != oldkey:
            del record[oldkey]

        return record


class Pipeline(object):
    def __init__(self, tokenizer, parser, processors):
        self.tokenizer = tokenizer
        self.parser = parser
        self.processors = processors

    def _format_error(self, record, e, processor=None):
        frm = inspect.trace()[-1]
        mod = inspect.getmodule(frm[0])
        line = inspect.getsourcelines(frm[0])[1] + 1
        title = record.get('title', '')
        if len(title) > 50:
            title = title[:50] + '...'
        if processor:
            print '=== ERROR WHILE PROCESSING RECORD =============================================='
            print ' Processor class: {}'.format(processor.__class__.__name__)
        else:
            print '=== ERROR WHILE PARSING RECORD ================================================='
        print '          Module: {}:{}'.format(mod.__name__, line)
        print '       Exception: {}'.format(type(e).__name__)
        print '         Message: {}'.format(e)
        print '     Source file: {0[0]}:{0[1]}'.format(record.source)
        print '    Record title: {}'.format(title)
        print '-' * 80

    def _apply_processor(self, p, records):
        return (self._process_record(p, r) for r in records if r is not None)

    def _process_record(self, processor, record):
        try:
            return processor.process_record(record)
        except Exception as e:
            self._format_error(record, e, processor=processor)

    def _parse_record(self, record):
        try:
            return self.parser.parse_record(record)
        except Exception as e:
            self._format_error(record, e)

    def process(self, stream):
        records = self.tokenizer.tokenize(stream)
        records = (self._parse_record(r) for r in records)
        for p in self.processors:
            records = self._apply_processor(p, records)
        return (r for r in records if r is not None)


class Record(dict):
    def __init__(self, value_format, raw_value):
        self.format = value_format
        self.raw_value = raw_value
