

class RecordException(Exception):
    def __init__(self, record):
        self.record = record


class NoCorrespondingAuthor(RecordException):
    pass


class NoAffiliationField(RecordException):
    pass


class NoAffiliationMatch(RecordException):
    pass
