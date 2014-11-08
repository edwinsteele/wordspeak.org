.. title: Wordspeak site performance improvements
.. slug: wordspeak-site-performance-improvements
.. date: 2013/10/20 10:55:47
.. tags: Technology
.. link:
.. description:


Improving the performance of this site has been a fun journey. I don't think the principles of optimisation change much from domain to domain so the challenge is learning how to apply those principles to a new domain (and learning which ones are going to have the most impact). So these improvements aren't novel, but the process of discovering and implementing them was enjoyable. With no loss of functionality, I was able to significantly improve page load time for all visitors to the site and make additional improvements for those that read the site from Eastern Australia.

The optimisations below were made over the space of about 6 months the improvements to page load time aren't quantified. I did look at `waterfall graphs <http://developers.google.com/chrome-developer-tools/docs/network#network_panel_overview>`_ and get feedback from `WebPagetest <http://www.webpagetest.org>`_ but I wanted to have fun with optimisation instead of baselining and measuring at each stage:

Minimise geographical distances
===============================

**Host locally**

Everything feels faster when it's closer. When I was in California recently, everything felt fast and the main difference was that the services were physically close. Connections to my web server changed from being a 190ms pacific ocean round trip to a 30ms hop within the state. DNS lookups in the wordspeak.org domain went from 240ms to 50ms. When I consider that most of my readers are in Australia, it makes sense to host in Australia so that the first connection and any subsequent connections are much faster (its even more significant when the first connection involves a DNS lookup). It also means that ssh sessions are more responsive, particularly over mobile networks where packet loss is higher. The first step was to move my server from Linode in California to AWS in Sydney and the next step is to move DNS from Rackspace, whose closest Anycast node is in Texas, to Amazon Route 53 who have Anycast nodes in Sydney.

Minimise what you need to transfer
==================================

**Reduce Page Weight and Request Count** 

Each library that is used on a site will usually involve requesting at least one extra JavaScript or CSS file. It takes time to initiate those requests and it takes time to download the content in those requests. My improvements came from removing unused libraries that my site builder, Nikola, includes by default and then using `webassets bundles <http://webassets.readthedocs.org/en/latest/bundles.html>`_ to concatenate like files so I have a single CSS and a single JavaScript file instead of 12 files. Even though the JavaScript and CSS were already minified, I was further able to reduce the amount of data in the CSS files by removing redundant selectors using `mincss <https://github.com/peterbe/mincss>`_.

`Content Delivery Networks <http://en.wikipedia.org/wiki/Content_delivery_network>`_ (CDNs) can reduce page load time under some circumstances, so I experimented with transferring (`JQuery <http://jquery.com>`_ and `Twitter Bootstrap <http://getbootstrap.com>`_) from CDNs but I observed better performance by self-hosting. I expect this was for a few reasons:

#. Obtaining JQuery and Bootstrap from the CDNs added two DNS lookups and three requests to the page load if the CDN files weren't in cache. The non-CDN setup had these libraries incorporated into the single CSS and JavaScript file that was produced by webassets so these lookups and requests weren't necessary, even though webassets-generated files were larger. 
#. The Bootstrap CDN didn't compress content (yes, I double-checked. No, I don't understand why they wouldn't!)
#. mincss meant that I didn't need to transfer most of the bootstrap CSS file anyway, so my Bootstrap was slimmer than the CDN Bootstrap.

Minimise what you actually transfer
===================================

**Compress. Compress. Compress**

Retrieving compressed content from a web server is very widely supported. Without compression, there was 261KB of data transferred to show the front page of my site, but with compression enabled it dropped to 86KB, 33% of the uncompressed size. I use Nginx as my web server, so it was as simple as having the following snippet in the default http section of the nginx.conf:

.. code:: nginx

    gzip  on;
    gzip_http_version 1.1;
    gzip_types    text/plain text/CSS text/javascript
                  application/x-javascript text/xml application/json
                  application/xml application/xml+rss;

However, I still found that json files were not being compressed, even though I'd added the ``application/json`` MIME type to the gzip_types directive. I resolved this by declaring an ``application/json`` MIME type, associated with the ``json`` file type in the Nginx ``mime.types`` file.

.. code:: nginx

  types {
    text/html                             html htm shtml;
    application/x-javascript              JavaScript;
    ...
    application/json                      json;
    ...
  }

Use the fastest source for a resource
=====================================

**Or: don't request what you already have**

Caches provide faster access to a frequently used resource - the principle is the same whether it's someone putting a favourite app on the front screen of their smartphone, a CPU retrieving from L3 cache instead of main memory, or placing the salt at the front of the spice shelf for easy retrieval (and relegating fenugreek to the back). In most cases, the hard work is specifying a cache policy so that the cache contains a valid copy of the most valuable resources. To help the client cache appropriately, I configured Nginx to tell the browser how long a cached item should be considered valid. Images shouldn't change once I put them on the site, and all but the top level content (index.html and archive.html) shouldn't change once they've been put up so this is policy works well for me.

.. code:: nginx

    location ~* \.(jpg|jpeg|gif|png|ico) {
        root   /home/esteele/Sites/www.wordspeak.org;
        expires 365d;
    }

    location ~* \.(html|json|js|css) {
        root   /home/esteele/Sites/www.wordspeak.org;
        expires 7d;
    }

    location = (index.html|archive.html) {
        root   /home/esteele/Sites/www.wordspeak.org;
        expires 1h;
    }

And in conclusion
=================

Optimisation isn't just about getting more done with less; it's also about completing the same work more quickly with existing resources. Try applying these principles to something that you control - it'll make you really awesome, people will like you more, and it'll probably make you rich and stuff.
