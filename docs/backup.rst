Backing up the database
=======================

When working on the whole data set using possibly destructive IRCO commands, it
is strongly suggested to back up the database to be able to restore the data in
case something goes wrong.

As IRCO does not provide a built-in, cross-platform utility to back up the data
easily, the following page describes how such a backup can be created for
specific database management systems.

.. toctree::
   :maxdepth: 2


SQLite 3
--------

SQLite 3 provides an easy to use tool to backup a database. To create the
backup, issue the following command::

    sqlite3 path/to/the/database.db .dump > path/to/the/backup.bak

If you ever need to restore the data from a backup, use the following command::

    mv path/to/the/database.db path/to/the/database.db.old
    sqlite3 path/to/the/database.db < path/to/the/backup.bak

Additional references:
 * http://www.sqlite.org/backup.html
 * http://www.ibiblio.org/elemental/howto/sqlite-backup.html
