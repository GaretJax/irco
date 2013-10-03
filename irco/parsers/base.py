import abc


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

    def _apply_processor(self, processor, records):
        return (processor.process_record(r) for r in records)

    def process(self, stream):
        records = self.tokenizer.tokenize(stream)
        records = (self.parser.parse_record(r) for r in records)
        for p in self.processors:
            records = self._apply_processor(p, records)
        return records


class Record(dict):
    def __init__(self, value_format, raw_value):
        self.format = value_format
        self.raw_value = raw_value
