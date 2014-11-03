.. link: 
.. description: 
.. tags: Technology
.. date: 2014/11/04 04:56:49
.. title: DNS with Cloudflare
.. slug: dns-with-cloudflare

I've been looking for a new DNS provider for a little while, and I've settled on [CloudFlare](https://www.cloudflare.com).
I like the way they give back to the community with [Universal SSL](https://www.cloudflare.com/ssl), I like that they're consistently [rated as fast](http://www.solvedns.com/dns-comparison/2014/08) and that they're planning to implement [DNSSEC](http://blog.cloudflare.com/dnssec-an-introduction/) (somebody needs to move in this area).
I also like the price (free), even though I'd actually pay for the service if I needed to.
I'm still undecided on whether to use them as a CDN but I've already seen benefit in using them for DNS.
[WebPageTest](https://www.webpagetest.org) shows DNS resolution times out of Sydney to be a few hundred milliseconds faster than my old provider, AWS, and resolution times from Austin and New York are in the low tens of millis, which is great.
I looked at Dyn (cheap, good performance, good features) and NSone (free and good performance) but was turned off in both cases by the Terms of Service that allows them to use my name in promo materials without my consent.
CloudFlare have impressed technically and socially, and that's a great outcome.
