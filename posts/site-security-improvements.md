<!--
.. title: Site Security Improvements
.. slug: site-security-improvements
.. date: 2016/10/07 07:01:00
.. tags:
.. spellcheck_exceptions: CSP,HSTS,XSS,evaluator,validator,SecurityHeaders,io,Helme's,Qualys,JavaScript
.. is_orphan: False
.. link:
.. description:
-->

I did some security work on this site recently. I was able to get some nice wins without a great investment of time, in part due to the great resources that are available. Here are the areas of work, the resources that I used, and the outcomes:

# Content Security Policy (CSP)
A CSP constrains the actions that a web page can take or the actions that can be performed upon it. It allows one to apply the *principle of least privilege* to a page and site. A CSP allows one to specify constraints like *"Only Load CSS from these sources"*, *"Don't allow this site to be embedded in frames"* and *"Don't allow inline JavaScript"*. I developed a CSP after reading a [the HTML5rocks CSP tutorial](https://www.html5rocks.com/en/tutorials/security/content-security-policy/) and [Scott Helme's CSP intro](https://scotthelme.co.uk/content-security-policy-an-introduction/). I validated my policy using [Google's CSP evaluator](https://csp-evaluator.withgoogle.com) and [Mozilla's Observatory tool](
https://observatory.mozilla.org/analyze.html). In order to apply best-practices, which include disabling inline JavaScript and CSS, I needed to make a simple changes to the site. I've been conscious to minimise JavaScript and CSS as I've developed this site, and it was great to see how that choice made the application of best-practices a simple task.

# Miscellaneous security headers
I implemented `X-XSS-Protection`, `X-Content-Type-Options` and `X-Frame-Options` and while the effect of these headers overlaps a little with CSP, providing them is still a good idea because of inconsistent CSP implementations and benefits unrelated to CSP. I learnt about them from [Scott Helme's Response Headers page](https://scotthelme.co.uk/hardening-your-http-response-headers/#x-frame-options) and [Mozilla's web security guidelines](https://wiki.mozilla.org/Security/Guidelines/Web_Security#X-Content-Type-Options). I validated my setup with the [SecurityHeaders validation tool](https://securityheaders.io/) and [Mozilla's Observatory tool](https://observatory.mozilla.org/analyze.html).

# SSL
I already had a reasonable SSL setup but while looking at the [Mozilla web security guidelines](https://wiki.mozilla.org/Security/Guidelines/Web_Security#HTTPS), I didn't consider how my list of cipher choices would need regular updating (I'd last reviewed them 2 years ago!). Mozilla are good enough to provide [nginx config snippets](https://wiki.mozilla.org/Security/TLS_Configurations#Nginx) for to help with good cipher selection, and their config snippet included an [HTTP Strict Transport Security (HSTS)](https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security) directive. I'd considered HSTS before, but found the SSL certificate renewal process to be complex enough that I was unsure I wouldn't accidentally take my site offline around renewal time. Having recently switched my site certificates over to the (awesome) [Let's Encrypt](https://letsencrypt.org) renewal process, I felt comfortable activating HSTS at the same time. I validated my setup with the [Qualys SSL Report](
https://www.ssllabs.com/ssltest/analyze.html)

# Outcome
It took about 4 hours to make the changes, and after the changes were applied, this site [^1] moved from an A to an A+ on the Qualys SSL Report. The Mozilla Observatory tool gives the site an A+ and the SecurityHeaders.io validator gives it an A. My [nginx config is available on GitHub](https://github.com/edwinsteele/setup-scripts/tree/master/ansible/roles/webhost/files).
 
[^1]: Actually, I use Cloudflare as a CDN, so I ran the tests against [my origin server](https://origin.wordspeak.org). 