Generating graphs
=================

Currently three types of graphs are supported:

1. Country
2. Institution
3. Author

These graphs types can be seen as three differently grained levels of the same
dataset. The first one is the most coarse grained, while the last one is the
most fine grained.


Problems with the *Institution* graph
---------------------------------------

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
