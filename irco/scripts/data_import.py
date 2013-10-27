import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from irco import models, utils
from irco.parsers import scopus


def get_records(source, pipeline):
    for path in utils.get_file_list(source):
        with open(path) as fh:
            for record in pipeline.process(fh):
                yield record


def import_records(engine, records):
    Session = sessionmaker(bind=engine)
    for record in records:
        session = Session()

        publication = (session.query(models.Publication)
                       .filter_by(unique_source_id=record.unique_source_id)
                       .first())

        if publication:
            continue

        publication = models.Publication(
            year=record['year'],
            title=record['title'],
            unique_source_id=record.unique_source_id,
            unparsed_record_format=record.format,
            unparsed_record_value=record.raw_value,
        )
        session.add(publication)

        institutions = {}

        for k, v in record['institutions'].iteritems():
            instance = models.Institution(name=v)
            institutions[k] = (instance, v)
            session.add(instance)

        for i, (name, affiliation) in enumerate(record['authors']):
            author = models.Person(name=name)

            if affiliation is not None:
                institution, raw = institutions[affiliation]
            else:
                institution, raw = None, None

            affiliated_author = models.AffiliatedAuthor(
                order=1,
                unparsed_institution_name=raw,
                institution=institution,
                unparsed_person_name=name,
                author=author,
                publication=publication,
            )
            session.add(affiliated_author)

        session.commit()


def main():
    argparser = argparse.ArgumentParser('irco-import')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-i', '--input-format')
    argparser.add_argument('source', nargs='+')
    argparser.add_argument('database')

    args = argparser.parse_args()
    engine = create_engine(args.database, echo=args.verbose)

    records = get_records(args.source, scopus.pipeline)
    import_records(engine, records)

    models.Base.metadata.create_all(engine)
