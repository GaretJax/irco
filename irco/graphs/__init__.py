import os
import glob
import importlib


def get_graphs():
    graphs = []
    for path in glob.glob(os.path.join(os.path.dirname(__file__), '*.py')):
        name = os.path.basename(path[:-3])
        if not name.startswith('_'):
            graphs.append(name)
    return tuple(graphs)


def get_graph(name):
    return importlib.import_module('irco.graphs.{}'.format(name))
