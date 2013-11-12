News for IRCO 0.6
=================

Upgrade
-------

You can install the latest version of the irco tool by issuing the following
command::

    pip install --upgrade irco

At the time of writing the latest version is 0.6. There are some major news for
this release, as better described below.

.. toctree::
   :maxdepth: 2


Database
--------

The new database system is in place. This will complicate things initially, but
will be a good choice for the future.

I have some more work to do before giving you access to a centralized database.
For the moment you can use a local SQLite database. This means that in all
places where a database connection string is required, you can use the
following::

    sqlite:///<name-of-the-database.db>

or::

    sqlite:///</absolute/path/to/name-of-the-database.db>

In the first case, the path is relative to your working directory, while in the
second, it is absolute to the root of the hard disk. You can place the database
wherever you want and even using more than one database (e.g., to keep records
separated). I think that a sane default is::

    sqlite:///irco.db

Before running any other command, you have to initialize the database::

    irco-init sqlite:///irco.db

Then you can import files from different sources::

    irco-import -i scopus scopus.csv sqlite:///irco.db

or, to import a file in compendex format::

    irco-import -i compendex compendex.txt sqlite:///irco.db

When you have imported a bunch of files, you can still generate the authors or
country graphs by replacing the path to the source file with the database::

    irco-graph authors sqlite:///irco.db out.gexf

or, to generate the *country* graph::

    irco-graph country sqlite:///irco.db out.gexf

The old ``irco-convert`` command is deprecated and should not be used anymore.


Documentation
-------------

I started to write the documentation for the tool. It does not contain anything
yet (except this page), but that's the next task on my todo list.

You can always find it at this address: http://irco.readthedocs.org/


.. _irco-explorer-news:

IRCO Explorer
-------------

*IRCO Explorer* is an interactive record explorer that allows to browse the
database from a web browser. You can run it locally by issuing this command::

    irco-explorer sqlite:///irco.db

and then navigating to the following page from you preferred web browser:

    http://localhost:8000/

When you are done exploring the dataset, hitting ``Control + C`` in the
terminal windows where you executed the ``irco-explorer`` command terminates
the server.
