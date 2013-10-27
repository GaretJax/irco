from __future__ import absolute_import
import logging
import os


logging.basicConfig(
    filename=os.environ.get('IRCO_LOGFILE', 'irco.log'),
    level=logging.INFO,
)


from structlog import get_logger, configure
from structlog.stdlib import LoggerFactory


__all__ = ['get_logger']


configure(logger_factory=LoggerFactory())
