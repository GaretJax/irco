Generating graphs
=================

Graph types
-----------

Currently three types of graphs are supported:

1. Country
2. Institution
3. Author

These graphs types can be seen as three differently grained levels of the same
dataset. The first one is the most coarse grained, while the last one is the
most fine grained.


Filtering publications
----------------------

Filtering by publication year
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to limit the result set for which graphs are generated to 
publications occurred during certain years.

To activate the filtering, it suffices to pass a value for the ``--years``
option when invoking the ``irco-graph`` command.

The ``--years`` options can parse the following values:

* A single year: ``2012``
* A list of single years: ``2003,2007,2013``
* A range of years (inclusive on both ends): ``2003-2006`` (equivalent to
  ``2003,2004,2005,2006``). Additionally a range can be open on one of its end,
  in which case no limiting will occur on that side:

  - ``2012-`` will select all publications with a publication date of 2012 or later;
  - ``-2002`` will select all publication with a publication date of 2002 or earlier.

* A combination of single years and ranges: ``2003-2006,2009,2012-``

The following command creates a ``country`` graph with all papers published in
or before 2000, in 2002, in 2003, in 2004, in 2005, in 2006, in 2008, in 2009,
or after 2013 (included)::

    irco-graph --years 2008,2009,2002-2006,-2000,2013- country sqlite:///test.db test.gexf


Filtering by corresponding author country
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Publications can be filtered by ore more corresponding author countries. When
active, this filter will only show publications for which the country of the 
institution of the corresponding author is in the list of defined values.

To activate the filtering, it suffices to pass one or more values for the
``--ca-country`` option when invoking the ``irco-graph`` command. The option
can be repeated multiple times to specify more than one alowed countries.

The short hand version of the argument, ``-c``, can be used as well and the
country name matching is case insensitive.

The following command creates a ``country`` graph with all papers which have
a corresponding authors affiliated to an institution residing in either Kuwait
or Qatar::

    irco-graph --ca-country=Kuwait -c qatar country sqlite:///test.db test.gexf



Filtering by publication type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Publications can be filtered by their type. The currently known types are:
``journal``, ``conference``, ``book``, ``book in series`` and ``patent``.

Filtering by publication type works similarly as with the corresponding author
country filter, but by using the ``--type`` (or ``-t`` short hand) command line
option.

The followign command creates a ``country`` graph with all journal articles or
book publications::

    irco-graph --type=book -t journal country sqlite:///test.db test.gexf


Misc notes
----------

Problems with the *Institution* graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current implementation of the *Institution* graph takes the institution
name as the key to create graph nodes. This behaviour induces the system to
create numerous nodes for the same entity as the instituion name is not
normalized in the data sets from which the database is populated.

For example, in one of the examined testing data sets, the *"Carnegie Mellon
University"* appears in at least 19 different variations of its name::

    Carnegie Mellon Qatar, Qatar
    Carnegie Mellon University - Qatar, Doha, Qatar
    Carnegie Mellon University In Qatar, P.O. Box 24866, Doha, Qatar
    Carnegie Mellon University in Qatar, Compute Science Department, Doha, Qatar
    Carnegie Mellon University in Qatar, Doha, Qatar
    Carnegie Mellon University in Qatar, Education City, Doha, Qatar
    Carnegie Mellon University in Qatar, Education City, PO Box 24866, Doha, Qatar
    Carnegie Mellon University in Qatar, P.O. Box 24866, Doha, Qatar
    Carnegie Mellon University in Qatar, PO Box 24866, Doha, Qatar
    Carnegie Mellon University in Qatar, Qatar Cloud Computing Center, Qatar
    Carnegie Mellon University in Qatar, Qatar Foundation, Education City, P.O. Box 24866, Doha, Qatar
    Carnegie Mellon University, 5000 Forbes Avenue, Pittsburgh, PA 15213, United States
    Carnegie Mellon University, Doha, Qatar
    Carnegie Mellon University, Education City, PO Box 24866, Doha, Qatar
    Carnegie Mellon University, Heinz College, Pittsburgh, PA, United States, Qatar Campus, Doha, Qatar
    Carnegie Mellon University, P.O. Box 24866, Qatar, Qatar
    Carnegie Mellon University, Pittsburgh, PA, United States
    Carnegie Mellon University, Qatar
    Carnegie Mellon University, Qatar Campus, PO Box 24866, Doha, Qatar
    Carnegie Mellon University, Qatar Education City, Doha, Qatar

Also note that this university exists once with its original name in
Pennsylvania and as a branch campus in Qatar (with the *"in Qatar"* suffix).

Different approaches can help solve (or at least reduce) the impact of this
problem:

1. Use of a normalized data set
2. Normalization of the data set with data mining techniques

In the second case (*in-house normalization*), the following non-exhaustive
list of techniques can be employed:

1. Normalization through geolocation
2. Normalization through text analysis (pattern matching + similarity
   measures)
3. Exploitation of other information respositories (Google searches,
   Wikipedia articles, ...)
4. Manual matching (crowdsourcing, `Amazon Machine Turk <https://requester.mturk.com/>`_,
   ...)
