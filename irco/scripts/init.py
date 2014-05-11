import argparse
from sqlalchemy import create_engine
from irco import models
from irco.logging import sentry


def main():
    argparser = argparse.ArgumentParser('irco-init')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('database')

    args = argparser.parse_args()

    sentry.context.merge({
        'tags': {'command': 'irco-init'},
        'extra': {'parsed_arguments': args.__dict__}
    })

    engine = create_engine(args.database, echo=args.verbose)
    models.Base.metadata.create_all(engine)
