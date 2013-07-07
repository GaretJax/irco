import argparse
import tablib
import sys

from irco import graphs


def write(fh, graph, format=None):
    from networkx.readwrite import gexf
    gexf.write_gexf(graph, fh)


def main():
    format_choices = []
    graph_choices = graphs.get_graphs()
    argparser = argparse.ArgumentParser('irco-graph')
    argparser.add_argument('-f', '--format', choices=format_choices)
    argparser.add_argument('graph_type', choices=graph_choices)
    argparser.add_argument('source')
    argparser.add_argument('output', default='-', nargs='?')

    args = argparser.parse_args()

    with open(args.source, 'r') as fh:
        dataset = tablib.import_set(fh)

    graph_factory = graphs.get_graph(args.graph_type)
    graph = graph_factory.create(dataset)

    if args.output == '-':
        write(sys.stdout, graph)
    else:
        with open(args.output, 'wb') as fh:
            write(fh, graph)
