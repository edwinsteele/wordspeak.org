.. title: Wordspeak site performance improvements
.. slug: wordspeak-site-performance-improvements
.. date: 2013/10/07 20:55:47
.. tags: 
.. link:
.. description:


Improving the performance of this site has been a fun journey. Having been a UNIX sysadmin many (well, several) moons ago, none of these improvements were particularly surprising after a little thought, but the process of discovering and implementing was enjoyable. The priciples of optimisation don't change much from domain to domain - the challenging is learning how to apply what you already know to a new domain (and learning which ones are going to have the most impact) 

This is qualitative. The points below come from about 6 months of optimisation. I did look at `waterfall graphs <https://developers.google.com/chrome-developer-tools/docs/network>`_ and I've got feedback from `WebPagetest <http://www.webpagetest.org>`_ but I didn't want to focus on getting exact baselines and measuring everything at each stage. In this case the fun comes from learning how to optimise page load time for a site.

In order:

Minimise geographical distances
===============================

**Host locally**

I was in the USA recently for work and I was amazed at the speed of the internet. I'm convinced that it wasn't the fast hotel connection - the difference was that the services were physically close. For my web server, I had replaced the 190ms pacific ocean round trip with a 20ms hop within California. For DNS lookups in the wordspeak.org domain, I'd gone from 240ms to 50ms (I use Rackspace for DNS, and the closest Anycast server is in Austin, Texas). Most of my readers are in Australia so it makes sense to host in Australia (CDNs are overkill at my scale). This means that establishing the first connection, and any subsequent connections is much faster. It also means that ssh sessions are more responsive, particularly over mobile networks where packet loss is higher. I did this by moving my server from Linode in California to AWS in Sydney and I saw my ping times drop from 190ms to 30ms. I'm still hosting DNS with Rackspace, but have plans to move to Amazon Route 53 as they have DNS servers in their Anycast network based in Sydney)

Minimise what you need to transfer
==================================

**Reduce Page Weight and Page Requests** 

Libraries are a great way to introduction functionality on your site, and each of them generally requires you to load a css and a javascript file. Each file that's loaded has a cost, and every byte of those files has a cost. In the beginning I had about 12 javascript or css files (minified, fortunately). I reduced that by removing the libraries that Nikola includes by default, but I don't use. Then I used `webassets bundles <http://webassets.readthedocs.org/en/latest/bundles.html>`_ to concatinate like files so I have a single css and a single js file. This minimised the number of requests. Then I was able to reduce the amount of data in the CSS files using `mincss <https://github.com/peterbe/mincss>`_ to remove redundant selectors.

I also experimented with transferring two significant libraries (`JQuery <http://jquery.com>`_ and `Twitter Bootstrap <http://getbootstrap.com>`_) from `Content Delivery Networks <http://en.wikipedia.org/wiki/Content_delivery_network>`_ (CDNs) and while CDNs mean that sometimes the user will already have downloaded those libraries as they viewed an unrelated site, I observed better performance when I stopped using them. I expect this was for a few reasons:

#. The non-CDN setup had these libraries incorporated into the single CSS and JavaScript file that was produced by Webassets. When Bootstrap and JQuery were obtained from the CDNs, the webassets files still needed to be transferred (albeit smaller files), so there were 3 extra files that needed downloading (JS for JQuery and Bootstrap, and CSS for Bootstrap).
#. The Bootstrap CDN didn't compress content (why, oh why wouldn't they do this?)
#. If the user hadn't downloaded the files from a CDN because of another site, there were two additional DNS lookups.
#. mincss meant that I didn't need most of the bootstrap CSS file anyway, so the page weight savings were even more significant over the CDN.

Minimise what you actually transfer
===================================

**Compress. Compress. Compress**

Sending compressed content from a webserver is very widely supported. When I enabled it, the data that I actually transfer dropped to about 30% of the uncompressed size. I use nginx as my webserver, so it was as simple as having the following snippet in the default http section of the nginx.conf:

.. code:: nginx

    gzip  on;
    gzip_http_version 1.1;
    gzip_types    text/plain text/css text/javascript
                  application/x-javascript text/xml application/json
                  application/xml application/xml+rss;

However, I still found that json files were not being compressed. I solved this by declaring an application/json MIME type in the nginx mime.types files, associating the json file suffix with the application/json mime type that I had used in the gzip_types directive.

.. code:: nginx

  types {
    text/html                             html htm shtml;
    application/x-javascript              js;
    ...
    application/json                      json;
    ...


Remove or streamline blocking operations
========================================

**Reduce DNS lookups and operations that block page rendering**

People visit a website to view or read the content, yet the browser is smart enough to know which components of a page are going to affect how to page looks. So by observing a few rules, it's possible for a web browser to render your page before everything has downloaded. To give faster visual feedback, I moved `CSS to the top of the page <http://developer.yahoo.com/performance/rules.html#css_top>`_ and `JavaScript to the bottom of the page <http://developer.yahoo.com/performance/rules.html#js_bottom>`_

Use the fastest source for a resource
=====================================

**Or: don't request what you already have**

Caches provide faster access to a frequently used resource - this is the same whether the situation is a CPU using L3 cache instead of main memory, or someone putting their favourite app on the front screen of a smartphone or when salt is placed at the front of the spice shelf (and fenugreek is relegated to the back). In most cases, the hard work is specifying a cache policy so that the cache contains a valid copy of the most valuable resources. In this situation, I did this by configuring nginx to tell the client (via HTTP eTAG headers) how long a cached item should be considered valid. Images shouldn't change once I put them on the site, and all but the top level content (index.html and archive.html) shouldn't change once they've been put up so this is policy works well for me.

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
