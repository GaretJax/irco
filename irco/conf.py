"""
Configuration management for the different module components.
"""


import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


MODULE = __name__.split('.', 1)[0]

DEFAULT_FILES = [
    os.path.join(os.path.dirname(__file__), 'default-settings.ini'),
    '/etc/{0}/{0}.ini'.format(MODULE),
    os.path.expanduser('~/.{}.ini'.format(MODULE)),
    os.path.join(os.path.realpath('.'), '{}.ini'.format(MODULE)),
]


def load_config(path=None, defaults=None):
    """
    Loads and parses an INI style configuration file using Python's built-in
    ConfigParser module.

    If path is specified, load it.

    If ``defaults`` (a list of strings) is given, try to load each entry as a
    file, without throwing any error if the operation fails.

    If ``defaults`` is not given, the following locations listed in the
    DEFAULT_FILES constant are tried.

    To completely disable defaults loading, pass in an empty list or ``False``.

    Returns the SafeConfigParser instance used to load and parse the files.
    """

    if defaults is None:
        defaults = DEFAULT_FILES

    config = configparser.SafeConfigParser(allow_no_value=True)

    if defaults:
        config.read(defaults)

    if path:
        with open(path) as fh:
            config.readfp(fh)

    return config


settings = load_config()
