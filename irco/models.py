from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Unicode, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.sql.expression import ClauseElement


Base = declarative_base()


def get_or_create(session, model, defaults={}, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = {k: v for k, v in kwargs.iteritems()
                  if not isinstance(v, ClauseElement)}
        params.update(defaults)
        instance = model(**params)
        session.add(instance)
        return instance, True


class Institution(Base):
    __tablename__ = 'institution'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(1024), nullable=False)
    country = Column(Unicode(100))

    def get_authors(self, session):
        return (session.query(Person)
                .join(AffiliatedAuthor)
                .filter(AffiliatedAuthor.institution == self))

    def get_publications(self, session):
        return (session.query(Publication)
                .join(AffiliatedAuthor)
                .filter(AffiliatedAuthor.institution == self))

    @property
    def authors(self):
        return self.get_authors(object_session(self))

    @property
    def publications(self):
        return self.get_publications(object_session(self))


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(60), nullable=False)

    def get_institutions(self, session):
        return (session.query(Institution)
                .join(AffiliatedAuthor)
                .filter(AffiliatedAuthor.author == self))

    def get_publications(self, session):
        return (session.query(Publication)
                .join(AffiliatedAuthor)
                .filter(AffiliatedAuthor.author == self))

    @property
    def institutions(self):
        return self.get_institutions(object_session(self))

    @property
    def publications(self):
        return self.get_authors(object_session(self))


class Publication(Base):
    __tablename__ = 'publication'

    # Basic attributes
    id = Column(Integer, primary_key=True)
    type = Column(String(32), nullable=True)
    title = Column(Unicode(1024), nullable=False)
    year = Column(Integer)
    times_cited = Column(Integer, nullable=True)

    # Relationships
    def get_institutions(self, session):
        return (session.query(Institution)
                .join(AffiliatedAuthor)
                .filter(AffiliatedAuthor.publication == self))

    @property
    def institutions(self):
        return self.get_institutions(object_session(self))

    def get_authors(self, session):
        return (session.query(Person)
                .join(AffiliatedAuthor)
                .filter(AffiliatedAuthor.publication == self))

    @property
    def authors(self):
        return self.get_authors(object_session(self))

    # Bookkeping metadata
    unique_source_id = Column(String(64), nullable=False, unique=True)
    unparsed_record_format = Column(String(20))
    unparsed_record_value = Column(Text())


class AffiliatedAuthor(Base):
    __tablename__ = 'affiliated_author'

    id = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=False)

    unparsed_institution_name = Column(Unicode(1024))
    institution_id = Column(Integer, ForeignKey('institution.id'))
    institution = relationship(Institution, backref='affiliations')

    unparsed_person_name = Column(Unicode(60), nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    author = relationship(Person, backref='affiliations')

    publication_id = Column(Integer, ForeignKey('publication.id'),
                            nullable=False)
    publication = relationship(Publication, backref='affiliations')

    is_corresponding = Column(Boolean, default=False)
