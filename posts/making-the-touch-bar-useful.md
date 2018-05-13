<!--
.. title: Making the Touch Bar useful
.. slug: making-the-touch-bar-useful
.. date: 2018-05-12 06:58:50 UTC+10:00
.. tags: Technology
.. category: 
.. link: 
.. description: 
.. spellcheck_exceptions: BetterTouchTool,BTT,ADSL,SNMP,BitBar,ctrl,Alacritty
.. type: text
-->

I've had a Touch Bar equipped Macbook Pro for about 6 months. Until recently, I only used the Touch ID sensor with any regularity; I couldn't see a use for the other buttons and the switch from buttons to sliders was a usability regression. I recently read [Making the Touch Bar finally useful](http://vas3k.com/blog/touchbar/) and discovered how [BetterTouchTool](https://folivora.ai/) can be used to customise the touch bar. Wow.

Here's my new touch bar:.

{{% wordspeak_image cloudinary_id=touch-bar_ele2ra title="My customised Touch Bar" %}}

From right-to-left:

* The escape key. As a user of an Apple iPad keyboard that lacks an escape key, I've mostly retrained muscle memory to use `ctrl+[` for escape. I use it occasionally (and I'd still rather have a physical key).
* Battery info. I had battery info in the menu bar but the Touch Bar is more noticeable, and the extra space allows for more info. This helps me be more aware of battery-hungry apps, and now my battery lasts longer.
* ADSL connection info. My ADSL model exposes this info by SNMP. It was previously in the menu bar as a [custom plugin](https://github.com/edwinsteele/bitbar-plugins/blob/13752ceb419d07bf7b6cf1f32d709ba06f7b4a10/Network/wan_status.10m.sh) for [BitBar](https://getbitbar.com/) and, like the battery info, it's more visible and useful in the Touch Bar.
* www.wordspeak.org ping time. This is an indication of my upstream connection quality, not as monitoring. When touched, it opens an [Alacritty](https://github.com/jwilm/alacritty) terminal to my hosting machine, with the appropriate colour scheme.
* Gateway ping time. Like the other ping time widget, this gives me an indication of link congestion, which often happens when devices are doing cloud backups or uploads. When touched, it also opens a [custom Alacritty terminal](https://github.com/edwinsteele/dotfiles/blob/master/alacritty-gateway.yml).
* Coffee time! Puts the laptop to sleep.
* Volume and brightness. Buttons, not sliders. The Touch Bar is a small target, and I found it hard to set the brightness or volume correctly with the sliders that Apple uses in the default configuration.
* Weather. Live, local weather from the [Bureau of Meteorology](https://www.bom.gov.au) implemented in [shell](https://github.com/edwinsteele/dotfiles/blob/master/btt-weather.sh)
* Clock. It's in the menu bar too, but I notice it more in this location.


The Touch Bar is a well implemented piece of technology, with a poor default configuration. [Paying a few dollars for a BTT licence](https://www.folivora.ai/buy) to make it useful is a good move.