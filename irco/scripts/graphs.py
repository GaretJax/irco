import argparse
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import true, false

from irco import graphs, models


def write(fh, graph, format=None):
    from networkx.readwrite import gexf
    gexf.write_gexf(graph, fh)


def main():
    graph_choices = graphs.get_graphs()
    argparser = argparse.ArgumentParser('irco-graph')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-y', '--years')
    argparser.add_argument('graph_type', choices=graph_choices)
    argparser.add_argument('database')
    argparser.add_argument('output', default='-', nargs='?')

    args = argparser.parse_args()

    engine = create_engine(args.database, echo=args.verbose)

    graph_factory = graphs.get_graph(args.graph_type)

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
    else:
        criteria = true()

    Session = sessionmaker(bind=engine)
    graph = graph_factory.create(Session(), criteria)

    if args.output == '-':
        write(sys.stdout, graph)
    else:
        with open(args.output, 'wb') as fh:
            write(fh, graph)
