import math

from jinja2 import Markup


class Page(object):
    def __init__(self, paginator, num, label=None):
        self.num = num
        self.paginator = paginator
        self.label = label if label else num + 1

    @property
    def is_current(self):
        return self.num == self.paginator.current_page

    def __html__(self):
        if 0 <= self.num < self.paginator.pages:
            link = '<a href="?page={}">{}</a>'.format(self.num + 1, self.label)
            class_ = 'active' if self.is_current else ''
        else:
            link = '<span>{}</span>'.format(self.label)
            class_ = 'disabled'

        return '<li class="{}">{}</li>'.format(class_, link)


class Paginator(object):
    block_size = 7
    limit_size = 2

    def __init__(self, count, per_page, current_page=0):
        self.count = count
        self.per_page = per_page
        self.current_page = current_page
        self.pages = int(math.ceil(1. * count / per_page))

    def next(self):
        return Page(self, self.current_page + 1, 'Next &rarr;')

    def prev(self):
        return Page(self, self.current_page - 1, '&larr; Prev')

    def ellipsis(self):
        return Markup(u'<li class="ellipsis disabled"><span>&hellip;</span></li>')

    def __iter__(self):
        side_size = int(math.ceil(self.block_size / 2))
        start = self.current_page - side_size
        end = self.current_page + side_size

        if start < 0:
            end -= start
        elif end > self.pages:
            start -= end - self.pages

        if start > self.limit_size + 1:
            yield Page(self, 0)
            yield Page(self, 1)
            yield self.ellipsis()
        else:
            start = 0

        for i in range(max(0, start), min(self.pages, end + 1)):
            yield Page(self, i)

        if end < self.pages - self.limit_size - 2:
            yield self.ellipsis()
            yield Page(self, self.pages - 2)
            yield Page(self, self.pages - 1)
        else:
            for i in range(end + 1, self.pages):
                yield Page(self, i)
