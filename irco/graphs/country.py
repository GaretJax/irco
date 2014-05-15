import sys
import itertools
import collections

import networkx as nx


from irco import logging

log = logging.get_logger()


def get_countries(publication):
    publication_countries = set()

    for affiliation in publication.affiliations:
        country = affiliation.institution.country
        if country is None:
            print >>sys.stderr, 'Undefined country for "{}"'.format(
                affiliation.institution.name)
        else:
            publication_countries.add(country)

    return publication_countries


def create(session, publications):
    g = nx.Graph()

    papers_count = collections.Counter()
    collaborations_count = collections.Counter()

    for publication in publications:
        publication_countries = get_countries(publication)
        g.add_nodes_from(publication_countries)
        papers_count.update(publication_countries)

        collaborations = list(itertools.combinations(
            sorted(publication_countries), 2))
        collaborations_count.update(collaborations)
        g.add_edges_from(collaborations)

    # Set papers count
    for country, count in papers_count.iteritems():
        g.node[country]['papers'] = count

    # Set edge weight
    for (c1, c2), count in collaborations_count.iteritems():
        g[c1][c2]['weight'] = count

    return g
