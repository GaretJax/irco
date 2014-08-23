import pycountry
from irco import logging


_cache = {}
log = logging.get_logger()

NAMES = {c.name.lower(): c for c in pycountry.countries.objects}
SUBDIVISIONS = {s.name.lower(): s for s in pycountry.subdivisions.objects}

PREFIXES = set([
    'Republic of',
])

REPLACEMENTS = {
    'South Korea': 'Korea, Republic of',
    'U Arab Emirates': 'United Arab Emirates',
    'Vietnam': 'Viet Nam',
    'Bosnia & Herceg': 'Bosnia and Herzegovina',
    'Byelarus': 'Belarus',
    'Neth Antilles': 'Netherlands Antilles',
    'USA': 'United States',
}


class CountryNotFound(Exception):
    def __init__(self, token, text):
        self.token = token
        self.text = text

    def __unicode__(self):
        return (u'Fuzzy search for "{}" returned no results (complete record: '
                '"{}")'.format(self.token, self.text))


def get_institution_country(institution_name):
    tokens = institution_name.strip('., ').split(', ')
    country_token = tokens[-1]

    if country_token in REPLACEMENTS:
        country_token = REPLACEMENTS[country_token]

    if country_token in PREFIXES:
        country_token = tokens[-2] + ', ' + tokens[-1]

    if country_token not in _cache:
        country = None
        cl = country_token.lower()

        try:
            country = pycountry.countries.get(name=country_token)
        except KeyError:
            country = None

        if country is None:
            for k, country in NAMES.iteritems():
                if (
                    cl in k or k in cl or
                    country.alpha3 in country_token.split(' ') or
                    country.alpha2 in country_token.split(' ')
                ):
                    log.warning(u'Fuzzy search for "{}" matched "{}"'.format(
                        country_token, country.name))
                    break
            else:
                country = None

        if country is None:
            for k, sub in SUBDIVISIONS.iteritems():
                if cl in k or k in cl:
                    country = sub.country
                    log.warning('Fuzzy search for "{}" matched subdivision '
                                '"{}" of country "{}"'.format(
                                    country_token, sub.name, country.name))
                    break

        if country is None:
            raise CountryNotFound(country_token, institution_name)

        _cache[country_token] = country.name

    return _cache[country_token]
