from __future__ import print_function

import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from irco import models, utils, countries
from irco.parsers import scopus, compendex, wos
from irco.logging import get_logger, sentry


def get_records(source, pipeline):
    for path in utils.get_file_list(source):
        sentry.extra_context({
            'input_file': path,
        })
        with pipeline.open(path) as fh:
            for record in pipeline.process(fh):
                yield record
        del sentry.context['extra']['input_file']


def import_records(engine, records):
    Session = sessionmaker(bind=engine)
    imported = 0
    ignored = 0
    for record in records:
        session = Session()

        publication = (session.query(models.Publication)
                       .filter_by(unique_source_id=record.unique_source_id)
                       .first())

        if publication:
            session.close()
            ignored += 1
            continue

        ambiguous = record.get('has_ambiguous_affiliations', False)

        publication = models.Publication(
            year=record['year'],
            title=record['title'],
            type=record.get('type', None),
            times_cited=record.get('times_cited', None),
            unique_source_id=record.unique_source_id,
            unparsed_record_format=record.format,
            unparsed_record_value=record.raw_value,
            has_ambiguous_affiliations=ambiguous,
        )
        session.add(publication)

        institutions = {}

        for k, v in enumerate(record['institutions']):
            try:
                country = countries.get_institution_country(v)
            except countries.CountryNotFound:
                country = None

            instance, _ = models.get_or_create(
                session, models.Institution, defaults={'country': country},
                name=v
            )
            institutions[k] = (instance, v)

        for i, (name, affiliation) in enumerate(record['authors']):
            author = models.Person(name=name)

            if affiliation is not None:
                institution, raw = institutions[affiliation]
            else:
                institution, raw = None, None

            affiliated_author = models.AffiliatedAuthor(
                order=1,
                is_corresponding=(
                    record.get('corresponding_author', None) == i),
                unparsed_institution_name=raw,
                institution=institution,
                unparsed_person_name=name,
                author=author,
                publication=publication,
            )
            session.add(affiliated_author)

        session.commit()
        session.close()
        imported += 1

    return imported, ignored


def main():
    log = get_logger()

    pipelines = {
        'compendex': compendex.pipeline,
        'scopus': scopus.pipeline,
        'wos': wos.pipeline,
    }

    argparser = argparse.ArgumentParser('irco-import')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-i', '--input-format', choices=pipelines, required=True)
    argparser.add_argument('-e', '--encoding', default='utf8')
    argparser.add_argument('-a', '--include-ambiguous-affiliations',
                           action='store_true', dest='ambiguous')
    argparser.add_argument('source', nargs='+')
    argparser.add_argument('database')

    args = argparser.parse_args()

    sentry.context.merge({
        'tags': {
            'command': 'irco-import',
            'input_format': args.input_format,
        },
        'extra': {
            'parsed_arguments': args.__dict__,
        }
    })

    log.info('arguments_parsed', args=args)

    pipeline = pipelines[args.input_format](encoding=args.encoding,
                                            include_ambiguous=args.ambiguous)
    engine = create_engine(args.database, echo=args.verbose)
    Session = sessionmaker(bind=engine)

    count_before = Session().query(models.Publication).count()
    records = get_records(args.source, pipeline)
    imported, ignored = import_records(engine, records)
    count_after = Session().query(models.Publication).count()

    pipeline.add_metric('imported_records', 'Records added to the database',
                        imported)
    pipeline.add_metric('ignored_records',
                        'Ignored records (already imported)', ignored)
    pipeline.add_metric('before_import', 'Records count before import',
                        count_before)
    pipeline.add_metric('after_import', 'Records count after import',
                        count_after)
    print()
    print(pipeline.report())
