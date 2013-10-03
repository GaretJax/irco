from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Unicode, ForeignKey
from sqlalchemy import UnicodeText
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


class Institution(Base):
    __tablename__ = 'institution'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(120), nullable=False)
    country = Column(Unicode(100))


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(60), nullable=False)


class AffiliatedAuthor(Base):
    __tablename__ = 'affiliated_author'

    id = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=False)

    unparsed_institution_name = Column(Unicode(120))
    institution_id = Column(Integer, ForeignKey('institution.id'),
                            nullable=False)
    affiliation = relationship(Institution)

    unparsed_person_name = Column(Unicode(60), nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    author = relationship(Person)

    publication_id = Column(Integer, ForeignKey('publication.id'),
                            nullable=False)


class Publication(Base):
    __tablename__ = 'publication'

    id = Column(Integer, primary_key=True)
    title = Column(Unicode(120), nullable=False)
    year = Column(Integer)

    unparsed_record_type = Column(String(20))
    unparsed_record = Column(UnicodeText())

    authors = relationship(
        AffiliatedAuthor,
        backref=backref('publication', order_by=AffiliatedAuthor.order)
    )
