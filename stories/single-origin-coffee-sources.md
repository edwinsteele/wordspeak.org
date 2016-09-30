<!-- 
.. title: Single-origin coffee sources
.. slug: single-origin-coffee-sources
.. date: 2015-05-29 13:50:11 UTC+10:00
.. spellcheck_exceptions: geolocated,Javascript,LatLng,OpenStreetMap,addPoints,addTo,clickable,geo,geolocation,href,https,openstreetmap,png,programatically,px,py,setView,tileLayer
.. tags: 
.. link: 
.. description: 
.. type: text
-->

Single-Origin Coffee Sources
============================

I love coffee and I regularly try beans from new locations. I've kept a running list of my single-origin beans for a little while and I thought it'd be interesting to plot their locations. I intentionally kept to a uniform format with [the raw data](https://github.com/edwinsteele/wordspeak.org/blob/master/files/assets/single_origin_coffee_data.txt) but some massaging of the data was necessary before OpenStreetMap could provide accurate geolocation data. In some cases the region listed by the roaster could be improved by gleaning information from the name of the supplier and in some cases there were differences in the anglicised version of the town or province name. In all cases it was an interesting dive into the providers and it was an excuse to experiment with [Leaflet](http://leafletjs.com/) for programatically creating maps.

The script and the Javascript are quick-and-dirty jobs - this was definitely more about the fun of the data and the visualisation than an exercise in writing beautiful code - [coffee_geo.py](https://github.com/edwinsteele/wordspeak.org/blob/master/coffee_geo.py)

The location markers are clickable to show more information about the beans.

<link rel="stylesheet" href="/assets/leaflet-0.7.3/leaflet.css" />
<style>
@media(min-width:870px) {
	#map { height: 416px; width: 555px; }
}
@media(max-width:870px) {
	#map { height: 337px; width: 450px; }
}
@media(max-width:500px) {
	#map { height: 300px; width: 400px; }
}
</style>
<div id="map"></div>

<script src="/assets/leaflet-0.7.3/leaflet.js"></script>
<script src="/assets/single_origin_coffee_data.js"></script>
<script>
var map = L.map('map');
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
map.setView(new L.LatLng(0, 0), 1);
addPoints();
</script>


