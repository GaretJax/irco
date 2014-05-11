from __future__ import absolute_import, print_function
import logging
import os
import sys


logging.basicConfig(
    filename=os.environ.get('IRCO_LOGFILE', 'irco.log'),
    level=logging.INFO,
)


from structlog import get_logger, configure
from structlog.stdlib import LoggerFactory


__all__ = ['get_logger']


configure(logger_factory=LoggerFactory())


from raven import Client
from irco.conf import settings
from irco import __version__


def make_excepthook(client):
    def excepthook(*exc_info):
        ident = client.get_ident(client.captureException(exc_info))
        r = sys.__excepthook__(*exc_info)
        print('-' * 80)
        print('  This exception was logged remotely. Please use the following'
              ' ID when\n  seeking support:', ident)
        print('-' * 80)
        return r
    return excepthook

enabled = settings.getboolean('logging', 'sentry')
dsn = settings.get('logging', 'sentry_dsn')

if enabled:
    sentry = Client(dsn)
    sentry.tags_context({
        'version': __version__,
    })
    if dsn:
        sys.excepthook = make_excepthook(sentry)
else:
    # Hide disabled sentry reporting
    logging.getLogger('raven.base.Client').setLevel(logging.WARNING)
    sentry = Client('')
