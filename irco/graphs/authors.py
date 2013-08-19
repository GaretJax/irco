import collections
from itertools import izip, combinations

import networkx as nx


def get_country(text):
    return text.rsplit(', ')[-1]


def get_countries(affiliations):
    return set(get_country(a) for a in affiliations)


def create(dataset):
    g = nx.Graph()

    coauthors = dataset['authors']
    affiliation_sets = dataset['author_affiliation']

    countries = set()

    papers_count = collections.Counter()
    collaborations_count = collections.Counter()

    for authors, affiliations in izip(coauthors, affiliation_sets):
        if affiliations is None:
            continue

        author_names = []
        for author, affiliation_id in authors:
            if affiliation_id == 0:
                continue
            affiliation = affiliations[str(affiliation_id)]
            country = get_country(affiliation)
            countries.add(country)
            papers_count[author] += 1
            g.add_node(author, affiliation_country=country)
            author_names.append(author)

        collaborations = list(combinations(author_names, 2))
        collaborations_count.update(collaborations)
        g.add_edges_from(collaborations)

    countries = {c: i for i, c in enumerate(countries)}

    # Set papers count
    for author, count in papers_count.iteritems():
        n = g.node[author]
        n['papers'] = count
        n['affiliation_country_id'] = countries[n['affiliation_country']]

    # Set edge weight
    for (c1, c2), count in collaborations_count.iteritems():
        g[c1][c2]['weight'] = count

    return g
