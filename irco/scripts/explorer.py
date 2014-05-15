import argparse

from irco.explorer import app, database, filters
#from irco.logging import sentry


def main():
    argparser = argparse.ArgumentParser('irco-explorer')
    argparser.add_argument('-p', '--port', default=8000, type=int)
    argparser.add_argument('-i', '--interface', default='127.0.0.1')
    argparser.add_argument('-d', '--debug', action='store_true')
    argparser.add_argument('database')

    args = argparser.parse_args()

    #sentry.context.merge({
    #    'tags': {'command': 'irco-explorer'},
    #    'extra': {'parsed_arguments': args.__dict__}
    #})

    app.config['DATABASE'] = args.database
    database.init_app(app)
    filters.init_app(app)

    app.run(
        host=args.interface,
        port=args.port,
        debug=args.debug,
    )
