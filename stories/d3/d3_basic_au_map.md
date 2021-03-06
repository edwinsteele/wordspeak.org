<!--
.. title: d3 Australian Map Demo (States by Awesomeness)
.. slug: d3-australian-map-demo
.. date: 2013/03/08 18:24:23
.. spellcheck_exceptions: 
.. tags: Technology
.. link: 
.. description: 
.. stylesheet_urls: /assets/d3_basic_au_map.css
.. script_urls: /d3-projects/lib/d3.v2.js,/assets/d3_basic_au_map.js
.. template: project.tmpl
-->


Australian States coloured by Awesomeness
=========================================

This was one of my first d3 experiments. I wanted to see a d3 map showing something other than the USA, which meant that I needed to work out how to generate GeoJSON files [^d3amd-1] and get my head around the projection mechanisms in d3. It also gave me an opportunity to play with colour scales.

<div id="d3_top_level_div"></div>

If you want to see the numbering used in the colour scale, and my rationale for declaring NSW as the best state and QLD as the worst, see the source!

Github has [the original (unembedded) html file](https://github.com/edwinsteele/d3-projects/blob/master/basic_au_map/basic_au_map.html)

I made the GeoJSON file by converting ESRI Shapefiles from the [2006 Australian Census](http://www.abs.gov.au/ausstats/abs@.nsf/DetailsPage/1259.0.30.0022006?OpenDocument) using the QGIS program. I used the *simplify geometries* function within that program, with a tolerance of 0.005, to reduce the detail to a suitable level for the web. Github has [the data files](https://github.com/edwinsteele/d3-projects/blob/master/data/au-states.geojson)


[^d3amd-1]: Please let me know of a source of Australian maps in geojson format, if you're aware of one

