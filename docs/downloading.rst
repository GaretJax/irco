Downloading search results from WoS
===================================

Shell script
------------

IRCO version >= 0.9 provide the `irco-scrape` command to download search
results from the Web of Science database. The usage of the command is simple::

    irco-scrape <search-id> path/to/output/directory

Where ``<search-id>`` has to be replaced with the WoS search id, as found in the
URL (under the named GET parameter ``SID``).

Bookmarklet
-----------

To simplify the construction of the command, along with its correct
``<search-id>`` parameter, you can add the link below to the bookmarks of your
browser (normally it suffices to drag & drop it to the bookmarks bar):

.. raw:: html

   <p><a href="javascript:!function(){var%20o={},n=(window.location.href.replace(/[%3F%26]+([^=%26]+)=([^%26]*)/gi,function(n,i,r){o[i]=r}),%22irco-scrape%20%22+o.SID+%22%20output/dir%22);prompt(%22To%20download%20this%20search%20results%20run%20the%20following%20command%20in%20terminal:%22,n)}();">Download WoS results</a></p>

You can then open it while displaying the search results page to get a popup
window containing the command to run. Note that you still have to copy & paste
the command into a shell and run it.

.. todo:: This command currenly just downloads the files to the given folder.
   You still have to manually import them using the ``irco-import`` command.
