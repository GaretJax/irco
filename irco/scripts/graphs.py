import argparse
import sys

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, aliased, joinedload
from sqlalchemy.sql.expression import true, false

from irco import graphs, models
from irco.logging import sentry


def write(fh, graph, format=None):
    from networkx.readwrite import gexf
    gexf.write_gexf(graph, fh)


def main():
    graph_choices = graphs.get_graphs()
    argparser = argparse.ArgumentParser('irco-graph')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-y', '--years')
    argparser.add_argument('-c', '--ca-country', action='append',
                           dest='ca_countries')
    argparser.add_argument('-t', '--type', action='append',
                           dest='types')
    argparser.add_argument('graph_type', choices=graph_choices)
    argparser.add_argument('database')
    argparser.add_argument('output', default='-', nargs='?')

    args = argparser.parse_args()

    sentry.context.merge({
        'tags': {
            'command': 'irco-graph',
            'graph_type': args.graph_type,
        },
        'extra': {'parsed_arguments': args.__dict__}
    })

    graph_factory = graphs.get_graph(args.graph_type)

    engine = create_engine(args.database, echo=args.verbose)
    Session = sessionmaker(bind=engine)
    session = Session()

    publications = (session
                    .query(models.Publication)
                    .options(
                        joinedload('affiliations').joinedload('author'),
                        joinedload('affiliations').joinedload('institution'),
                    ))

    if args.years:
        criteria = false()
        for y in args.years.split(','):
            if '-' in y:
                start, end = y.split('-')
                if start:
                    c = models.Publication.year >= int(start)
                else:
                    c = true()

                if end:
                    c = c & (models.Publication.year <= int(end))
            else:
                c = models.Publication.year == int(y)
            criteria = criteria | c

        publications = publications.filter(criteria)

    if args.ca_countries:
        c_author = aliased(models.AffiliatedAuthor)
        c_institution = aliased(models.Institution)

        criteria = false()

        for country in args.ca_countries:
            criteria = criteria | (
                func.lower(c_institution.country) == func.lower(country)
            )

        publications = (publications
                        .join(c_author)
                        .join(c_institution)
                        .filter(c_author.is_corresponding == True)
                        .filter(criteria))

    if args.types:
        criteria = false()

        for type in args.types:
            criteria = criteria | (models.Publication.type == type)

        publications = publications.filter(criteria)

    graph = graph_factory.create(session, publications)

    if args.output == '-':
        write(sys.stdout, graph)
    else:
        with open(args.output, 'wb') as fh:
            write(fh, graph)
