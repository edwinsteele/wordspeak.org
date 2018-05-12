<!--
.. title: Making the touch bar useful
.. slug: making-the-touch-bar-useful
.. date: 2018-05-12 06:58:50 UTC+10:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

I've had a touch-bar equipped Macbook Pro for about 6 months. Until recently, I'd only ever used the Touch-ID sensor regularly - the other buttons and sliders served no purpose or were a disincentive for use. I recently read [Making the Touch Bar finally useful](http://vas3k.com/blog/touchbar/) and discovered how [BetterTouchTool](https://folivora.ai/) can be used to customise the touch bar. Wow.
I now believe that the Touch Bar is a well implemented piece of technology, with a poor default configuration, rather than being outright useless.

Here's my new touch bar:.

{{% wordspeak_image cloudinary_id=touch-bar_ele2ra title="My customised touch bar" %}}

From right-to-left:

* The escape key. I still don't use it. As a user of an Apple iPad keyboard that lacks an escape key, I've mostly retrained muscle memory to use `ctrl+[` for escape. I'd rather have a physical key, but I can't do anything about that.
* Battery info. Compact battery info was previously in the menu bar, and moving it here means that I can get a better feel for battery life. Having it visible means that I'm aware of battery-hungry apps, and am able to make the battery last far longer.
* ADSL connection info. This is info from my ADSL modem that is exposed by SNMP. I was previously in the menu bar as a [custom plugin](https://github.com/edwinsteele/bitbar-plugins/blob/13752ceb419d07bf7b6cf1f32d709ba06f7b4a10/Network/wan_status.10m.sh) for [BitBar](https://getbitbar.com/).
* www.wordspeak.org ping time. This is an indication of my upstream connection quality, not as monitoring. When touched, it opens an [Alacritty](https://github.com/jwilm/alacritty) terminal to my hosting machine, with the appropriate colour scheme.
* Gateway ping time. Like the other ping time widget, this gives me an indication of link congestion, which often happens when devices are doing cloud backups or uploads. When touched, it also opens a [custom alacritty terminal](https://github.com/edwinsteele/dotfiles/blob/master/alacritty-gateway.yml).
* Coffee time! Puts the laptop to sleep.
* Volume and brightness. Buttons, not sliders. The touchbar is a small target, and I could never get the brightness or volume right with the default configuration of sliders.
* Weather. Live local weather from the [Bureau of Meteorology](https://www.bom.gov.au) implemented in [shell](https://github.com/edwinsteele/dotfiles/blob/master/btt-weather.sh)
* Clock. It's in the menu bar too, but I find myself noticing it more in this location.
