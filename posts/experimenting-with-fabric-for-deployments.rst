.. title: Experimenting with fabric for deployments
.. slug: experimenting-with-fabric-for-deployments
.. date: 2013/02/24 16:50:06
.. tags: Python, UNIX
.. link: 
.. description: 


`Fabric <http://fabfile.org>`_ has caught my eye as a deployment tool several
times over the last year or so. Each time I've seen it, my thought has
been that it's a attempt to replace something that doesn't need replacing,
namely the venerable unix shell script.


Fabric came up again this week in an `article
<http://blog.apps.npr.org/2013/02/14/app-template-redux.html>`_ by the NPR
application team [1] and on this occasion I saw that they were solving a similar
problem to one that I recently solved with a shell script. The authors seemed
clear-headed and not prone to fads so I thought I'd take the opportunity to
duplicate my shell script functionality in a fabric fabfile.

I must say that I was impressed. The `fabric tutorial
<http://docs.fabfile.org/en/1.5/tutorial.html>`_ is very well structured and
allowed me to get results quickly. Within a few hours I'd git-rm'ed my shell
script and the build-version_control-test-deploy cycle for this site is now
handled by a `fabfile
<https://github.com/edwinsteele/wordspeak.org/blob/master/fabfile.py>`_. While
the fabfile is the same length as the `shell script <https://github.com/edwinsteele/setup-scripts/blob/5e4354fcefd41cd5e93bc20736e66b2291c168ab/wordspeaksync.sh>`_,
I think it's far easier to read and allows partial deployments (reminding me of
make). I particularly like the innovative use of context managers as it removes
one of the key problems with deployment scripts, that inadvertently modifying
global state can cause unexpected downstream side-effects. Well done, Fabric developers.

I don't plan to replace all my shell scripts with fabfiles, but I'll seriously
consider it next time I need to write a script.

.. [1] Hat-tip to `PyCoder's weekly <http://www.pycoders.com>`_ - a very well curated weekly digest of python articles and releases. It's just the right length for a weekly summary. Do consider it if you have an interest in python.
