import os

from irco import parser, tabular


def get_file_list(sources):
    for source in sources:
        if os.path.isdir(source):
            for path in sorted(os.listdir(source)):
                _, ext = os.path.splitext(path)
                if ext not in ('.txt', '.csv', '.tsv'):
                    continue
                path = os.path.join(source, path)
                yield path
        elif os.path.isfile(source):
            yield source


def get_dataset(source, records=None):
    table = tabular.Table(notset=None)
    for path in get_file_list(source):
        with open(path) as fh:
            for record in parser.parse(fh, records):
                table.add(record)
    return table.dataset()
