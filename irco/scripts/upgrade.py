import argparse

from alembic import command
from alembic.config import Config

from irco.logging import get_logger, sentry


def main():
    log = get_logger()

    argparser = argparse.ArgumentParser('irco-import')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('database')

    args = argparser.parse_args()

    sentry.context.merge({
        'tags': {
            'command': 'irco-upgrade',
        },
        'extra': {
            'parsed_arguments': args.__dict__,
        }
    })

    log.info('arguments_parsed', args=args)

    config = Config()
    config.set_main_option('script_location', 'irco:migrations')
    config.set_main_option('sqlalchemy.url', args.database)

    command.upgrade(config, 'head', sql=False, tag=None)
