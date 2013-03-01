.. title: Farewell Wireless Broadband
.. slug: 20060402farewell-wireless-broadband
.. date: 2006/04/02 08:26:33
.. tags: Technology
.. link: 
.. description: 


I'm not normally an early adopter. Many years ago, I decided that it was
important for consumer electronics to *just work* so that I could actually use
them instead of spending eons fighting with some glossy new technology just to
be the first to see it in action. Wireless broadband does fit into the "glossy
new technology" category but it was a really good fit for me.

- I want ADSL-like speed for my internet access
- I don't need sub-100ms ping times
- I don't have a landline (I have a great mobile phone plan)
- I can't get Cable Internet in my apartment block
- I don't agree with leeching bandwidth from my neighbours' open wireless points

Wireless broadband?
-------------------

Yeah, it's not common but it's not a new concept either. If you worked in San
Francisco around 1999 there was a system called Ricochet that would give you
wireless internet connectivity while you drove in the Valley (or more
accurately while you were gridlocked on the freeways in the Valley). Sydney's
setup is quite comprehensive so you can get wireless network connectivity in
most suburbs in the metropolitan area. You access the wireless networks using
proprietary hardware (a standalone modem or a PCMCIA card) at speeds up to
1024/256kbps. Unfortunately the either the technology or the implementation
were lacking which meant that it wasn't a good fit for me, so I wrote a poem
about my experiences.

An Ode to Wireless Broadband
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	bullitt:~ edwin$ ping www.unwired.com.au
	PING www.unwired.com.au (220.101.191.10): 56 data bytes
	64 bytes from 220.101.191.10: icmp_seq=0 ttl=59 time=210.72 ms
	64 bytes from 220.101.191.10: icmp_seq=1 ttl=59 time=301.443 ms
	64 bytes from 220.101.191.10: icmp_seq=4 ttl=59 time=159.269 ms
	64 bytes from 220.101.191.10: icmp_seq=5 ttl=59 time=561.475 ms
	64 bytes from 220.101.191.10: icmp_seq=7 ttl=59 time=219.599 ms
	64 bytes from 220.101.191.10: icmp_seq=8 ttl=59 time=491.45 ms
	64 bytes from 220.101.191.10: icmp_seq=9 ttl=59 time=113.836 ms
	^C
	--- www.unwired.com.au ping statistics ---
	10 packets transmitted, 7 packets received, 30% packet loss
	round-trip min/avg/max = 113.836/293.970/561.475 ms


A post-mortem
-------------

To their credit, the providers state that this is not the sort of technology
for gamers who need ultra-low ping times. That didn't worry me because I'm not
a gamer but I do want reasonable page loading times, reasonable download
speeds, the ability to streaming audio or video and reasonable quality on
Skype or VOIP. Over the 6 months that I had my 512/128kbps connection, I was
very attentive to these areas. Here are my observations.

Page loading times
^^^^^^^^^^^^^^^^^^

Yuk. Terrible. Yuk. If you look at the ping times above you'll understand when
I say that it would often take 5 seconds to load the google search page.
Interestingly enough, larger pages weren't that much slower although they
still took forever to put the first bit of information up on the screen. The
page loading times deteriorated over the course of my 6 month contract which
is consistent with increasing (over?)load at the base-stations. Forum comments
on `Whirlpool <http://www.whirlpool.net.au>`_, Australia's broadband review site, showed my experiences were
consistent with others on the same service. However, while the loading times
were very irritating, it's not the end of the world. I'm not a huge web user,
I can be patient and the $35/month I was saving over the cost of an ADSL
connection was worth it.

Reasonable download speeds
^^^^^^^^^^^^^^^^^^^^^^^^^^

The download speeds were pretty close to the maximum throughput of my
connection on the rare occasions that I downloaded a demo of some software or
the most recent Battlestar Galactica episode off BitTorrent (yes, I buy the
DVDs. no, I'm not a pirate) . I found this to be particularly interesting
because it suggests that the page loading problem doesn't lie with
over-allocated bandwidth at the provider's end.

Streaming Audio and Video
^^^^^^^^^^^^^^^^^^^^^^^^^

This was the wireless broadband deal-breaker. The ability to stream a radio
station or a music sample from the iTunes store is important to me. It's also
nice to be able to check out a movie trailer or watch an segment from 
`ABC's Foreign Correspondent <http://www.abc.net.au/foreign/broadband.htm>`_.
No matter what I tried, I couldn't get more than a few
seconds of content before it would re-buffer. It wasn't the site and it's not
my local setup (as ADSL has confirmed). I never did any analysis on the number
of packets that the applications thought they were loosing but I bet that
packet loss was the problem.

Skype and VOIP
^^^^^^^^^^^^^^

I wish I'd characterised Skype behaviour a little better but I didn't. I guess
you can blame the broken mic on my powerbook. The time that I did have a
conversation, a call using SkypeOut to Canada early in my 6 month contract,
had acceptable connection quality but a sample size of one ain't much good. I
do have doubts about whether Skype or VOIP would be acceptable with the
latency and packet loss but can only speculate.

Setup notes
^^^^^^^^^^^

Using the built-in diagnositic software, I found that my base station was
either 1.3km or 4.7km distant (it changed between the two). Most of the time
it was connected to a base station at Silverwater. My signal strength was
-83db +/- 3. I wish I'd noted the quality. I spent the best part of an hour
positioning the modem in the apartment, watching the graph of the signal
strength was fascinating, especially when twisting the modem by 15 degrees
would give a few extra db of signal strength.

Conclusion
----------

The packet loss and latency killed this technology for me. Your mileage will
vary, for better or for worse, by your location. I would have been interested
to know whether the base station was overloaded or whether the technology just
isn't great. Either way, I'm now zooming along with ADSL. Sure I'm paying an
extra $35/month because I need a landline but it's worth it because it *just
works*.

Now...does anyone want to buy a used Unwired modem?
