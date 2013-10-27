import argparse
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from irco import graphs


def write(fh, graph, format=None):
    from networkx.readwrite import gexf
    gexf.write_gexf(graph, fh)


def main():
    graph_choices = graphs.get_graphs()
    argparser = argparse.ArgumentParser('irco-graph')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('graph_type', choices=graph_choices)
    argparser.add_argument('database')
    argparser.add_argument('output', default='-', nargs='?')

    args = argparser.parse_args()

    engine = create_engine(args.database, echo=args.verbose)

    graph_factory = graphs.get_graph(args.graph_type)

    Session = sessionmaker(bind=engine)
    graph = graph_factory.create(Session())

    if args.output == '-':
        write(sys.stdout, graph)
    else:
        with open(args.output, 'wb') as fh:
            write(fh, graph)
