<!-- 
.. title: Site optimisations from Velocity Conference
.. slug: site-optimisations-from-velocity-conference
.. date: 2015-06-29 15:54:28 UTC+10:00
.. tags: 
.. link: 
.. spellcheck_exceptions: webby,Grigorik's,SVG,SVGs,ImageOptim,JPEGs,filesize,Flickr's,Firefox,Inline,inline,navbar,Dao
.. is_orphan: false
.. description: 
.. type: text
-->


My day job is mostly running a team within IT Operations but I also do a bunch of product management for in-house web-based and command-line tools that help us manage our production environment. [My employer](http://www.optiver.com/sydney/) sent me to [Velocity Conference](http://velocityconf.com/devops-web-performance-2015) where I heard some great Ops and Web development talks. Some of the talks were also relevant to this site, so I've put a few into action and this post will explain the wins.

My two favourite webby talks were [Ilya Grigorik's presentation on HTTP2](https://docs.google.com/presentation/d/1r7QXGYOLCh4fcUq0jDdDwKJWNqWK1o4xMtYpKZCJYjM/present#slide=id.p19) and [Bruce Lawson's talk about web performance in the third world](https://brucelawson.github.io/talks/2015/velocity/). My take-aways were:

1. Images, specifically photos, are still the bulk of the data on my pages. I've worked hard to keep my page structure lean but the photos were so heavy by comparison and [page weight affects more than just load time](http://whatdoesmysitecost.com/test/150610_W0_AED)
2. I could offer images tailored to specific devices, but wasn't.
3. I was still loading unnecessary resources, and could replace a web font with SVG and have some learn something along the way.
4. The site was responsive, but it was a bit brittle because I was still using _px_ rather than _em_ to size my elements and media breakpoints


# 1. Lightweight images

The [Designing for Performance](http://shop.oreilly.com/product/0636920033578.do) book suggests ways to reduce image download size without tangibly compromising quality. I took their advice and used [ImageOptim](https://imageoptim.com/) to apply a bunch of size reduction techniques to my images, including setting JPEGs to have a maximum quality of 80%. ImageOptim reduced the filesize by about 60% (compared to the flickr-hosted images) and I couldn't tell the difference.

Previously I was allowing Flickr to host the images, so this optimisation technique meant that I needed to host them myself. Hosting the files on this site saves a DNS lookup and SSL handshake (as long as I'm not loading so many images that multiple connections are opened) but I don't get the advantage of using [[Flickr's CDN](https://geopeeker.com/fetch/?url=https%3A%2F%2Ffarm9.staticflickr.com%2F8574%2F16533922280_f659db4b04_z.jpg)]. When I host the images myself, the site loads faster for Australian viewers ([1.5s document complete](http://www.webpagetest.org/result/150617_ZF_BAE/1/details/)) than when I use the flickr CDN ([1.7s document complete](http://www.webpagetest.org/result/150602_BJ_JNC/1/details/)) because the nearest Flickr CDN to Australia is in Singapore, which is a ~160ms round-trip. An Irish viewer would have a slower experience from my self-hosting ([4.3s document complete](http://www.webpagetest.org/result/150617_SC_BBR/1/details/)) because Flickr has a CDN in Ireland, and that's only a few milliseconds away.

While I could easily make the site faster for all users by hosting the whole site with Cloudflare I'd lose control of the end-to-end technical setup and that's been a fun experience so far, so part of me would like to keep it in my control.


# 2. Responsive images

Responsive images allow a browser to download an image that is appropriate for the device in use. This means that a browser on a phone can download a small image, a browser on a wide screen can download a larger image and a device with a retina screen can download a more detailed image.

When I started looking at responsive images, I immediately started looking at the picture tag, which was the thing that people were excitedly talking about. The picture tag is very powerful ([examples](http://www.html5rocks.com/en/tutorials/responsive/picture-element/)), but after a while I realised that if I don't care about orientation *(a.k.a. art direction)* or alternative media formats, the srcset tag of img is just as effective, and is far simpler. Incidentally, [srcset support](http://caniuse.com/srcset) is a little better than [picture support](http://caniuse.com/picture)). When I started implementing, I followed Opera's nice explanation on [srcset-style responsive images](https://dev.opera.com/articles/native-responsive-images/) but if the picture tag is your thing they have [one for picture-style responsive images](https://dev.opera.com/articles/responsive-images/) too.

I ended up using the srcset width (w) descriptor and making 4 image sizes available to make sure that there was an appropriate range of images to cover phones up to desktop retina screens. While Safari and mobile safari don't support the width descriptor (they only support the resolution switching (x) descriptor), the fallback is no worse than what I had before and it produces really nice output on Chrome and Firefox, which is good enough for me (it's what I use).


# 3. Inline fonts

While HTTP2 reduces the need to minimise HTTP requests, I won't start serving HTTP2 until nginx supports it later this year, so I'm still choosing to approach optimisation with an HTTP 1.1 mindset, which includes minimising requests. One of my requests is a web font that is visible on small screens where I replace navbar text with icons. This optimisation involved moving the icons from a font file into (inline) SVG. This change retained the resolution independence that comes from using fonts, as SVGs are vector-based, while reducing page weight and eliminating an HTTP request. I had already created a customised, low-weight web font using [Fontello](http://fontello.com) and this was a reasonably smooth transition given they also provide an SVG version of the glyphs. The only gotchas involved setting the dimensions of the glyph and applying a transform to display the glyphs the right way up (see [step 3 & step 5 of this article](http://www.heydonworks.com/article/font-hacking)). This was a chance to learn a little about SVG to be honest and while the outcomes are nice, they're not particularly compelling.


# 4. Resolution Independent Layout

I was a _px_ holdout. I didn't see the value in using _em_ over _px_, so I'd been defining everything *(borders, margins, text size, media breakpoints)* in pixels _(px)_ rather than in terms of the base font size _(em)_. During the conference I finally understood that using _em_ meant that elements would scale appropriately when someone set a custom font size (+accessibility) or when someone was using a retina screen... so I changed it all to _em_. Reading [The Dao of Web Design](http://alistapart.com/article/dao) also helped me let go of the idea of controlling every last pixel on the screen and allowing the reader to choose how my content was presented. Oh, how freeing. This new mindset led to a rethink and removal of most of the micro-positioning and micro-formatting directives that were cluttering my CSS. One can now change the base font size in a browser, or zoom, and the text and all the elements scale nicely and in an unsurprising way... and the CSS is cleaner.

Along the way I spent a little time trying to work out whether I should specify media breakpoints in _px_ or _em_. I got stuck thinking about particular devices and the number of pixels on their screens, but one doesn't want to set breakpoints for particular devices, or even classes of devices as there are simply too many. The recommendations that sat best with me were ones that set media breakpoints based on content rather than device widths. In practice that meant I brought up my normal layout, measured the width of the normal layout text header (in _em_) added a bit for fat, and then made that the max-width of my mobile layout icon header. Here are two good articles that helped me with the process: [Where And How To Set Breakpoints in Media Queries](http://www.vanseodesign.com/web-design/media-query-breakpoints/) and [7 Habits of Highly Effective Media Queries](http://bradfrost.com/blog/post/7-habits-of-highly-effective-media-queries/) 


So those are the recent changes - three cheers for Velocity conference. What a great learning environment.