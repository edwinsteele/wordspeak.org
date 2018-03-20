<!-- 
.. title: Single-origin coffee sources
.. slug: single-origin-coffee-sources
.. date: 2015-05-29 13:50:11 UTC+10:00
.. spellcheck_exceptions: geolocated,Javascript,LatLng,OpenStreetMap,addPoints,addTo,clickable,geo,geolocation,href,https,openstreetmap,png,programatically,px,py,setView,tileLayer
.. tags: 
.. stylesheet_urls: /assets/leaflet-0.7.3/leaflet.css,/assets/single_origin_coffee.css
.. script_urls: /assets/leaflet-0.7.3/leaflet.js,/assets/single_origin_coffee.js
.. preconnect_urls: https://a.tile.openstreetmap.org,https://b.tile.openstreetmap.org,https://c.tile.openstreetmap.org,https://d.tile.openstreetmap.org
.. link: 
.. description: 
.. type: text
.. template: project.tmpl
-->

Single-Origin Coffee Sources
============================

I love coffee and I regularly try beans from new locations. I've kept a running list of my single-origin beans for a little while and I thought it'd be interesting to plot their locations. I intentionally kept to a uniform format with [the raw data](https://github.com/edwinsteele/wordspeak.org/blob/master/files/assets/single_origin_coffee_data.txt) but some massaging of the data was necessary before OpenStreetMap could provide accurate geolocation data. In some cases the region listed by the roaster could be improved by gleaning information from the name of the supplier and in some cases there were differences in the anglicised version of the town or province name. In all cases it was an interesting dive into the providers and it was an excuse to experiment with [Leaflet](http://leafletjs.com/) for programatically creating maps.

The script and the Javascript are quick-and-dirty jobs - this was definitely more about the fun of the data and the visualisation than an exercise in writing beautiful code - [coffee_geo.py](https://github.com/edwinsteele/wordspeak.org/blob/master/coffee_geo.py)

The location markers are clickable to show more information about the beans.

<div id="map"></div>
