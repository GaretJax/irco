News for IRCO 0.9
=================

Upgrade
-------

You can install the latest version of the irco tool by issuing the following
command::

    pip install --upgrade irco

Changelog
---------

 * ``irco-scrape`` command to download WoS search results.
 * Records with ambiguous author affiliations are ignored. The number of
   ignored records due to ambiguity is reported at the end of each
   ``irco-import`` as ``Records with ambiguous auth. aff.``.
 * The affiliation in the `reprint author` field (``RP``) takes precedence
   over the affiliation listed in the `affiliations` field (``AF``).
