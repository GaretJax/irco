import abc
import inspect
import collections
import codecs


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

    def initialize(self, pipeline):
        self.pipeline = pipeline

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
    def __init__(self, tokenizer, parser, processors, encoding='utf8'):
        self.tokenizer = tokenizer
        self.parser = parser
        self.processors = processors
        self.encoding = encoding
        self._opened_files = 0
        self._records = 0
        self._processed = 0
        self._metrics = collections.OrderedDict()

        for p in processors:
            p.initialize(self)

    def _format_error(self, record, e, processor=None):
        frm = inspect.trace()[-1]
        mod = inspect.getmodule(frm[0])
        line = inspect.getsourcelines(frm[0])[1] + 1
        title = record.get('title', '')
        if len(title) > 50:
            title = title[:50] + '...'
        if processor:
            print '=== ERROR WHILE PROCESSING RECORD ' + '=' * 45
            print ' Processor class: {}'.format(processor.__class__.__name__)
        else:
            print '=== ERROR WHILE PARSING RECORD ===' + '=' * 45
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
        self._records += 1
        try:
            return self.parser.parse_record(record)
        except Exception as e:
            self._format_error(record, e)

    def add_metric(self, key, name, val=0):
        self._metrics[key] = [name, val]

    def inc_metric(self, key):
        self._metrics[key][1] += 1

    def open(self, path):
        self._opened_files += 1
        return codecs.open(path, 'rb', encoding=self.encoding)

    def report(self):
        fields = [
            ('Processed files', self._opened_files),
            ('Total records found', self._records),
            ('Records ignored due to errors', self._records - self._processed),
            ('Successfully processed records', self._processed),
        ] + self._metrics.values()

        l = max(len(f[0]) for f in fields)
        s = ''
        s += '-' * 80 + '\n'
        for k, v in fields:
            s += '{:>{}s}: {}\n'.format(k, l+1, v)
        s += '-' * 80
        return s

    def process(self, stream):
        records = self.tokenizer.tokenize(stream)
        records = (self._parse_record(r) for r in records)
        for p in self.processors:
            records = self._apply_processor(p, records)
        for r in records:
            if r is not None:
                self._processed += 1
                yield r


class Record(dict):
    def __init__(self, value_format, raw_value):
        self.format = value_format
        self.raw_value = raw_value
