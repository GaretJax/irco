import argparse
import sys
from tablib import formats

from irco import utils


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


def write(fh, dataset, format):
    fh.write(getattr(dataset, format))


def main():
    format_choices = [fmt.title for fmt in formats.available]
    argparser = argparse.ArgumentParser('irco-convert')
    argparser.add_argument('-f', '--format', choices=format_choices)
    argparser.add_argument('-r', '--records')
    argparser.add_argument('source', nargs='+')
    argparser.add_argument('output')

    args = argparser.parse_args()

    if args.records:
        records = [int(r.strip()) for r in args.records.split(',')]
    else:
        records = None
    format = get_format(args, format_choices)
    dataset = utils.get_dataset(args.source, records)

    if args.output == '-':
        write(sys.stdout, dataset, format)
    else:
        with open(args.output, 'wb') as fh:
            write(fh, dataset, format)
