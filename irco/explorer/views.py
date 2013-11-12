from flask import render_template, request

from irco.explorer.application import app
from irco.explorer.paginator import Paginator
from irco.explorer import database as db
from irco import models


def context_from_query(query):
    page = int(request.args.get('page', 1)) - 1
    per_page = int(request.args.get('per_page', 50))
    count = query.count()
    objects = query.offset(page * per_page).limit(per_page)
    paginator = Paginator(count, per_page, page)
    context = {
        'objects': objects,
        'paginator': paginator,
    }
    return context


@app.route('/')
def index():
    return render_template('index.html', **{})


@app.route('/authors/')
def authors():
    objects = db.Session().query(models.Person).order_by(models.Person.name)
    context = context_from_query(objects)
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
    objects = (db.Session().query(models.Institution)
               .order_by(models.Institution.name))
    context = context_from_query(objects)
    return render_template('institutions/index.html', **context)


@app.route('/institutions/<int:institution_id>/')
def institution(institution_id):
    institution = db.Session().query(models.Institution).get(institution_id)

    context = {
        'institution': institution,
    }
    return render_template('institutions/single.html', **context)


@app.route('/publications/')
def publications():
    objects = (db.Session().query(models.Publication)
               .order_by(models.Publication.title))
    context = context_from_query(objects)
    return render_template('publications/index.html', **context)


@app.route('/publications/<int:publication_id>/')
def publication(publication_id):
    object = db.Session().query(models.Publication).get(publication_id)

    context = {
        'publication': object
    }
    return render_template('publications/single.html', **context)
