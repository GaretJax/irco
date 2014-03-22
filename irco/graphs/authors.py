import collections
from itertools import combinations
from sqlalchemy.orm import joinedload

import networkx as nx

from irco import models


NO_COUNTRY = '<no country>'


def get_country(author):
    countries = [a.institution.country for a in author.affiliations]

    if len(countries) == 1:
        country = countries[0]
    elif countries:
        countries = collections.Counter(countries)
        country = countries.most_common(1)[0]
    else:
        country = NO_COUNTRY

    return country


def create(session, publications):
    g = nx.Graph()

    countries = set()
    papers_count = collections.Counter()
    collaborations_count = collections.Counter()

    authors = (session.query(models.Person).options(
        joinedload('affiliations').joinedload('institution')
    ))

    for author in authors:
        country = get_country(author)
        countries.add(country)
        g.add_node(author.name, affiliation_country=country, papers=0)

    for publication in publications:
        author_names = []

        for affiliation in publication.affiliations:
            author = affiliation.author
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

    # Remove authors with no papers
    for a, d in g.nodes_iter(data=True):
        if not d['papers']:
            g.remove_node(a)

    # Set edge weight
    for (c1, c2), count in collaborations_count.iteritems():
        g[c1][c2]['weight'] = count

    return g
