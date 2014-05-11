Configuration
=============

IRCO uses INI files as its configuration format. Each time an IRCO command is
run, configuration is loaded from different places:

* ``/etc/irco/irco.ini``
* ``~/.irco.ini``
* ``irco.ini`` in the directory where the command is executed

Values defined in following files overwrite the same directives defined in
previous files.

Initialization on OS X
----------------------

To create a new user-specific configuration file, issue the following
commands::

   cd ~
   touch .irco.ini
   open -a TextEdit .irco.ini

At this point, the TextEdit application opens up with an empty configuration
file. Edit the file to your liking, save and close the application.
