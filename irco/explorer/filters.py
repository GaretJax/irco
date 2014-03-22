import csv
import collections
from StringIO import StringIO

from flask import render_template
from jinja2 import Markup


def init_app(app):
    @app.template_filter('format_record')
    def format_record(record):
        val = record.unparsed_record_value

        fmt_csv = 'csv' in record.unparsed_record_format
        fmt_tsv = 'tsv' in record.unparsed_record_format

        if fmt_csv or fmt_tsv:
            delimiter = ','
            if fmt_tsv:
                delimiter = '\t'
            data = csv.DictReader(StringIO(val.encode('utf-8')), delimiter=delimiter)
            data = next(data)
            data = [(unicode(k, 'utf-8'), unicode(v, 'utf-8')) for k, v in data.iteritems()]
            val = collections.OrderedDict(data)
            val = Markup(render_template('dict-table.html', table=val))
        return val
