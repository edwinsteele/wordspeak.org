.. link: 
.. description: 
.. tags: Technology, UNIX, Privacy
.. date: 2014/10/01 17:00:27
.. title: Privacy with HTTPS
.. slug: privacy-with-https


# Privacy is a right
Everyone has a right to read and communicate in private, without fear of eavesdropping by a person or government, but that right isn't honoured. This right is not related to the subject material and the desire for privacy should never be used to imply guilt. To make it possible to reading in private, this site can now be accessed over [HTTPS](https://www.wordspeak.org). It doesn't matter to me that this is a personal, low traffic site, nor is it important that the content is unlikely to offend; Everyone has a right to read and communicate in private.

I found enabling HTTPS to be an inexpensive and reasonably simple operation that hasn't noticably affected the performance of the site.

# Enabling HTTPS isn't costly
I'm using a 12-month free SSL certificate from [StartSSL](https://www.ssllabs.com/ssltest/). The reputation of certificate providers is very important, and while I found it hard to find recommendations on reputable providers, these guys seem to be ok. When renewal time comes, a 12-month single domain certificate from them is $49, and [I'm told that there are free options](https://istlsfastyet) non-commercial use.

# Enabling HTTPS isn't that complicated
It took a few hours to setup, but most of that was because I like this sort of change to be repeatable so I did my usual dance with version control for all the keys, certificates and artifacts and then introduced HTTPS to the site via my ansible playbooks.
When I started, I wasn't particularly familiar with certificate formats or signing requests but I followed a [StartSSL and nginx-oriented walkthrough](https://konklone.com/post/switch-to-https-now-for-free#register-with-startssl) which helped immensely. I used [Qualys' SSL Server Test](https://www.ssllabs.com/ssltest) to validate my setup.

# HTTPS isn't slow
Once I applied a few well understood optimisations, it's almost the same speed as my http setup. I began with the ["more complete nginx config"](https://gist.github.com/konklone/6532544) that was mentioned on the [StartSSL and nginx-oriented walkthrough](https://konklone.com/post/switch-to-https-now-for-free) and read through some writing by Ilya Grikorik, particularly [Optimizing NGINX TLS Time To First Byte (TTTFB)](https://www.igvita.com/2013/12/16/optimizing-nginx-tls-time-to-first-byte/). Some of the optimisations required using a newer version of nginx and I was thrilled to find that nginx maintain a CentOS repo which made the upgrade process trivial (no need to build from source or admit defeat and stick with the standard CentOS 6 version). The greatest performance improvement came from enabling [OCSP stapling](https://en.wikipedia.org/wiki/OCSP_stapling).

## So how much slower is HTTPS?
My server is hosted by Rackspace in their Sydney datacentre. I've used [Webpagetest](https://www.webpagetest.org) to record the time to *document complete*, in situations where the webpage test client is in Sydney and San Jose:

* HTTP with a Sydney client: [0.39s](http://www.webpagetest.org/result/141004_D0_Q75/)
* HTTPS with a Sydney client: [0.42s](http://www.webpagetest.org/result/141004_17_Q87/)
* HTTP with a San Jose client: [1.78s](http://www.webpagetest.org/result/141001_4Y_CRC/)
* HTTPS with a San Jose client: [1.96s](http://www.webpagetest.org/result/141001_Z3_CRH/)

So the difference is really just the extra TCP round-trip, within a margin of error.

# What now?
There are still a few more changes to make, particularly enabling [HTTP Strict Transport Security](https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security) once I'm comfortable with my setup and to review and understand the optimisations described at [Is TLS Fast Yet?](https://istlsfastyet.com). Oh yeah, that and enjoying that people can read in private.
