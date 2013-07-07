import tablib

from collections import OrderedDict


class Table(object):

    def __init__(self, notset=None):
        self.headers = OrderedDict()
        self.data = []
        self.notset = notset

    def get_header_id(self, k):
        try:
            return self.headers[k]
        except KeyError:
            header_id = self.headers[k] = len(self.headers)
            return header_id

    def add(self, data):
        row = {}
        for k, v in data.iteritems():
            row[self.get_header_id(k)] = v
        self.data.append(row)

    def rows(self):
        for row in self.data:
            l = []
            for index in self.headers.itervalues():
                l.append(row.get(index, self.notset))
            yield tuple(l)

    def dataset(self):
        dataset = tablib.Dataset(headers=self.headers.keys())
        for row in self.rows():
            dataset.append(row)
        return dataset
