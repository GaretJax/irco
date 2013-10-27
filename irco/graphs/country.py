import sys
import itertools
import collections

import pycountry
import networkx as nx

from irco import models, logging

log = logging.get_logger()

_countries = {}


PREFIXES = set(['Republic of', ])
NAMES = {c.name.lower(): c for c in pycountry.countries.objects}
REPLACEMENTS = {
    'South Korea': 'Korea, Republic of'
}


class CountryNotFound(Exception):
    def __init__(self, token, text):
        self.token = token
        self.text = text

    def __unicode__(self):
        return (u'Fuzzy search for "{}" returned no results (complete record: '
                '"{}")'.format(self.token, self.text))


_countries = {}


def get_country(institution):
    text = institution.name
    tokens = text.split(', ')

    country_token = tokens[-1]

    if country_token in REPLACEMENTS:
        country_token = REPLACEMENTS[country_token]

    if country_token in PREFIXES:
        country_token = tokens[-2] + ', ' + tokens[-1]

    if country_token not in _countries:
        country = None
        try:
            country = pycountry.countries.get(name=country_token)
        except KeyError:
            try:
                country = pycountry.countries.get(name=country_token)
            except KeyError:
                cl = country_token.lower()
                for k, country in NAMES.iteritems():
                    v = country.name.lower()
                    if cl in v or v in cl:
                        break
                    if country.alpha3 in country_token.split(' '):
                        break
                    if country.alpha2 in country_token.split(' '):
                        break
                else:
                    country = None
            if country:
                print >>sys.stderr, 'Fuzzy search for "{}" matched "{}"'.format(
                    country_token, country.name)
            else:
                raise CountryNotFound(country_token, text)

        _countries[country_token] = country.name

    return _countries[country_token]


def get_countries(publication):
    countries = set()

    for institution in publication.institutions:
        try:
            countries.add(get_country(institution))
        except CountryNotFound as e:
            print >>sys.stderr, unicode(e)

    return countries


def create(session):
    g = nx.Graph()

    papers_count = collections.Counter()
    collaborations_count = collections.Counter()

    for publication in session.query(models.Publication):
        countries = get_countries(publication)
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
