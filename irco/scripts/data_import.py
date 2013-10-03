import argparse

from sqlalchemy import create_engine

from irco import models, utils, parser


def get_records(source):
    for path in utils.get_file_list(source):
        with open(path) as fh:
            for record in parser.parse(fh):
                yield record


def import_records(engine, records):
    for record in records:
        print record


def main():
    argparser = argparse.ArgumentParser('irco-import')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-i', '--input-format')
    argparser.add_argument('source', nargs='+')
    argparser.add_argument('database')

    args = argparser.parse_args()

    args = argparser.parse_args()
    engine = create_engine(args.database, echo=args.verbose)

    records = get_records(args.source)
    import_records(engine, records)

    models.Base.metadata.create_all(engine)
