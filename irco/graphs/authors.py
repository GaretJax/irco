import collections
from itertools import combinations

import networkx as nx

from irco import models


NO_COUNTRY = '<no country>'


def get_country(author):
    def extract_country(institution):
        return institution.name.rsplit(',', 1)[-1].strip().lower()

    countries = [extract_country(i) for i in author.institutions]

    if len(countries) == 1:
        country = countries[0]
    elif countries:
        countries = collections.Counter(countries)
        country = countries.most_common(1)[0]
    else:
        country = NO_COUNTRY

    return country


def create(session):
    g = nx.Graph()

    countries = set()
    papers_count = collections.Counter()
    collaborations_count = collections.Counter()

    for author in session.query(models.Person):
        country = get_country(author)
        countries.add(country)
        g.add_node(author.name, affiliation_country=country)

    for publication in session.query(models.Publication):
        author_names = []

        for author in publication.authors:
            papers_count[author.name] += 1
            author_names.append(author.name)

        collaborations = list(combinations(author_names, 2))
        collaborations_count.update(collaborations)
        g.add_edges_from(collaborations)

    countries = {c: i for i, c in enumerate(countries)}

    # Set papers count and country index
    for author, count in papers_count.iteritems():
        n = g.node[author]
        n['papers'] = count
        n['affiliation_country_id'] = countries[n['affiliation_country']]

    # Set edge weight
    for (c1, c2), count in collaborations_count.iteritems():
        g[c1][c2]['weight'] = count

    return g
