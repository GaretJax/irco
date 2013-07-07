import argparse
import os
import glob
import sys
from tablib import formats

from irco import parser, tabular


def get_file_list(sources):
    for source in sources:
        if os.path.isdir(source):
            for path in glob.glob(os.path.join(source, '*.txt')):
                yield path
        elif os.path.isfile(source):
            yield source


def get_format(args, choices):
    format = args.format
    if not format:
        # Guess it from file extension
        try:
            format = args.output.rsplit('.', 1)[1]
        except IndexError:
            if args.output != '-':
                print 'Could not guess output format from filename.'
            else:
                print 'Cannot guess output format when writing to stdout.'
            print 'Please use the -f/--format option to specify it.'
            sys.exit(1)
        else:
            if format not in choices:
                print ('Could not guess output format from filename ({}).'
                       .format(format))
                print 'Please use the -f/--format option to specify it.'
                sys.exit(1)
    return format


def get_dataset(source):
    table = tabular.Table('')
    for path in get_file_list(source):
        with open(path) as fh:
            for record in parser.parse(fh):
                table.add(record)
    return table.dataset()


def write(fh, dataset, format):
    fh.write(getattr(dataset, format))


def main():
    format_choices = [fmt.title for fmt in formats.available]
    argparser = argparse.ArgumentParser('irco-convert')
    argparser.add_argument('-o', '--output', default='-')
    argparser.add_argument('-f', '--format', choices=format_choices)
    argparser.add_argument('source', nargs='+')

    args = argparser.parse_args()

    format = get_format(args, format_choices)
    dataset = get_dataset(args.source)

    if args.output == '-':
        write(sys.stdout, dataset, format)
    else:
        with open(args.output, 'wb') as fh:
            write(fh, dataset, format)
