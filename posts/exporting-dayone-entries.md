<!--
.. title: Exporting DayOne Entries
.. slug: exporting-dayone-entries
.. date: 2015/11/07 02:45:37
.. tags: 
.. spellcheck_exceptions: Markdown,DayOne,GitHub,iCloud,Dropbox,journalling,metadata,dayone
.. is_orphan: False
.. link:
.. description:
-->

I keep a journal, and for a while I've written and kept the journal entries in [DayOne](http://dayoneapp.com/). It's a nice App that has encouraged me to write, to the point where journalling has become an indispensable part of how I do life. While DayOne gave me features to start me writing, I now want to write entries in my standard editor, with all its niceties. DayOne uses Markdown and the App can be told to store its data in iCloud or Dropbox, so it wasn't hard to find the entries on disk, but the Markdown is embedded in a file along with metadata. There's a little bit of work involved in exporting the entries as regular Markdown files with metadata, so I've put my export script on GitHub in case someone finds it useful.

[export_dayone_entries.py](https://github.com/edwinsteele/python-scripts/blob/master/export_dayone_entries.py)
