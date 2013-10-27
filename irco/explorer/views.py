from flask import render_template

from irco.explorer.application import app
from irco.explorer import database as db
from irco import models


@app.route('/')
def index():
    context = {}
    return render_template('index.html', **context)


@app.route('/authors/')
def authors():
    session = db.Session()
    objects = session.query(models.Person).order_by(models.Person.name)

    context = {
        'authors': objects,
    }
    return render_template('authors/index.html', **context)


@app.route('/authors/<int:author_id>/')
def author(author_id):
    session = db.Session()
    author = session.query(models.Person).get(author_id)

    context = {
        'author': author
    }
    return render_template('authors/single.html', **context)


@app.route('/institutions/')
def institutions():
    session = db.Session()
    objects = (session.query(models.Institution)
               .order_by(models.Institution.name))

    context = {
        'institutions': objects
    }
    return render_template('institutions/index.html', **context)

@app.route('/institutions/<int:institution_id>/')
def institution(institution_id):
    session = db.Session()
    institution = session.query(models.Institution).get(institution_id)

    context = {
        'institution': institution,
    }
    return render_template('institutions/single.html', **context)


@app.route('/publications/')
def publications():
    session = db.Session()
    objects = (session.query(models.Publication)
               .order_by(models.Publication.title))

    context = {
        'publications': objects,
    }
    return render_template('publications/index.html', **context)


@app.route('/publications/<int:publication_id>/')
def publication(publication_id):
    session = db.Session()
    object = session.query(models.Publication).get(publication_id)

    context = {
        'publication': object
    }
    return render_template('publications/single.html', **context)
