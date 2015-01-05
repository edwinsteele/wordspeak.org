<!--
.. title: Let the computer do the menial testing
.. slug: let-the-computer-do-the-menial-testing
.. date: 2013/03/17 15:41:31
.. spellcheck_exceptions: 
.. tags: Technology
.. link: 
.. description: 
-->


There are a number of valuable checks that I should do every time I make a change to this site, things like checking for broken links and misspelled words, catching build warnings, locating orphaned pages (those that exist on disk but aren't linked) and confirming that my build environment is correctly versioned. I'm lazy (or busy, or both) so while those things might be valuable, unless someone or something does them for me, they're unlikely to be done regularly. Fortunately the nature of these tasks makes them great candidates for automation.

Recently I [wrote](/posts/experimenting-with-fabric-for-deployments.html) about switching my wordspeak deployment scripts to fabric and I've been gradually extending my fabric *fabfile* to include these validation checks. Here's the output from my most recent deployment, showing:

-   the build, checking for Nikola warnings
-   spell checking using [pyenchant](https://pypi.python.org/pypi/pyenchant) (actually, this isn't shown, but it does happen)
-   versioning the modules used in my build environment
-   confirming I've version controlled my posts and build environment
-   the sync to the staging site (on my local machine)
-   broken link checking using [linkchecker](https://pypi.python.org/pypi/linkchecker)
-   checking for orphaned files (I'm still working out what to do with the gallery, and I haven't finished writing the background for the other page)
-   the sync to the main site
-   a push to the github repository to make sure it's current

```.console
(wordspeak)Mercury:wordspeak.org esteele$ fab deploy
[localhost] local: /Users/esteele/.virtualenvs/wordspeak/bin/nikola build
0 actions performed
[localhost] local: pip freeze > requirements.txt
[localhost] local: git status --porcelain
[localhost] local: rsync --delete-after -a output/ /Users/esteele/Sites/staging.wordspeak.org
[localhost] local: rsync --delete-after -a output/.htaccess /Users/esteele/Sites/staging.wordspeak.org
[localhost] local: linkchecker --config linkcheckerrc http://staging.wordspeak.org
That's it. 182 links checked. 0 warnings found. 0 errors found.
[localhost] local: linkchecker --config linkcheckerrc --verbose --file-output=csv/linkchecker-output.csv --no-status --ignore-url '!(staging.wordspeak.org)' http://staging.wordspeak.org
Orphaned file: categories/index.html
Orphaned file: pages/d3/d3-nt-sla-map.html
Orphaned html files exist (are on disk but aren't linked). Continue? [Y/n] y
Push to live site? [Y/n] y
[localhost] local: rsync --delete-after -a output/ wordspeak.org:/users/home/esteele/web/public
[localhost] local: rsync --delete-after -a output/.htaccess wordspeak.org:/users/home/esteele/web/public
[localhost] local: git push
Counting objects: 17, done.
Delta compression using up to 2 threads.
Compressing objects: 100% (13/13), done.
Writing objects: 100% (13/13), 2.17 KiB, done.
Total 13 (delta 9), reused 0 (delta 0)
To git@github.com:edwinsteele/wordspeak.org.git
39b8464..c81b8b1  master -> master
Done.
(wordspeak)Mercury:wordspeak.org esteele$
```

You can see that Fabric is doing all the donkey work, and I'm left to confirm a few (temporary) oddities and make a final choice to send the change onto the live site. It's very satisfying. At some point I'll probably extend it to do W3C validation of the HTML and RSS and as I don't know a way to detect JavaScript errors, I could use it as an excuse to learn how to write [selenium](https://pypi.python.org/pypi/selenium) tests. I regularly trigger warnings even in its current state, though, so it's value is clear.

I consider these sort of tasks to be the unit tests and static validations for my site, and apply the same sort of mindset as one would with other checks of this type. Namely:

-   Make them repeatable
-   make the checks run quickly (mine run in around 30 seconds)
-   make it harder to deploy the site without running them than with them (I do this by making my deploy command run all the tests)
-   white-list the known, but accepted, violations so you don't have to think about whether the warning is *known*

The source for my fabfile is on [github](https://github.com/edwinsteele/wordspeak.org/blob/master/fabfile.py)

