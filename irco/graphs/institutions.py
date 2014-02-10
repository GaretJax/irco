import sys
import itertools
import collections

import networkx as nx

from irco import models, logging

log = logging.get_logger()


def get_institutions(publication):
    institutions = set()

    for institution in publication.institutions:
        institutions.add(institution.name)

    return institutions


def create(session, criteria):
    g = nx.Graph()

    papers_count = collections.Counter()
    collaborations_count = collections.Counter()

    for publication in session.query(models.Publication).filter(criteria):
        institutions = get_institutions(publication)
        g.add_nodes_from(institutions)
        papers_count.update(institutions)

        collaborations = list(itertools.combinations(institutions, 2))
        collaborations_count.update(collaborations)
        g.add_edges_from(collaborations)

    # Set papers count
    for institution, count in papers_count.iteritems():
        g.node[institution]['papers'] = count

    # Set edge weight
    for (i1, i2), count in collaborations_count.iteritems():
        g[i1][i2]['weight'] = count

    return g
