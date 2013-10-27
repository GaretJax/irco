import argparse

from irco.explorer import app, database


def main():
    argparser = argparse.ArgumentParser('irco-explorer')
    argparser.add_argument('-p', '--port', default=8000, type=int)
    argparser.add_argument('-i', '--interface', default='127.0.0.1')
    argparser.add_argument('-d', '--debug', action='store_true')
    argparser.add_argument('database')

    args = argparser.parse_args()

    app.config['DATABASE'] = args.database
    database.init_app(app)

    app.run(
        host=args.interface,
        port=args.port,
        debug=args.debug,
    )
