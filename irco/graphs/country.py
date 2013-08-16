import itertools
import collections

import networkx as nx


def get_country(text):
    return text.rsplit(', ')[-1]


def get_countries(affiliations):
    return set(get_country(a) for a in affiliations)


def create(dataset):
    g = nx.Graph()

    affiliation_sets = dataset['author_affiliation']

    papers_count = collections.Counter()
    collaborations_count = collections.Counter()

    # Create graph
    for paper in affiliation_sets:
        if paper is None:
            continue
        countries = get_countries(paper.itervalues())
        g.add_nodes_from(countries)
        papers_count.update(countries)

        collaborations = list(itertools.combinations(countries, 2))
        collaborations_count.update(collaborations)
        g.add_edges_from(collaborations)

    # Set papers count
    for country, count in papers_count.iteritems():
        g.node[country]['papers'] = count

    # Set edge weight
    for (c1, c2), count in collaborations_count.iteritems():
        g[c1][c2]['weight'] = count

    return g
