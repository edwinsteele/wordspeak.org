<!--
.. title: d3 Australian Map Demo (States by Awesomeness)
.. slug: d3-australian-map-demo
.. date: 2013/03/08 18:24:23
.. spellcheck_exceptions: 
.. tags: Technology, Visualisation
.. link: 
.. description: 
-->


Australian States coloured by Awesomeness
=========================================

This was one of my first d3 experiments. I wanted to see a d3 map showing something other than the USA, which meant that I needed to work out how to generate GeoJSON files [^1] and get my head around the projection mechanisms in d3. It also gave me an opportunity to play with colour scales.

<style type="text/css">
  #states path { stroke: #fff; }
</style>
<div id="d3_top_level_div"></div>


If you want to see the numbering used in the colour scale, and my rationale for declaring NSW as the best state and QLD as the worst, see the source!

Github has [the original (unembedded) html file](https://github.com/edwinsteele/d3-projects/blob/master/basic_au_map/basic_au_map.html)

I made the GeoJSON file by converting ESRI Shapefiles from the [2006 Australian Census](http://www.abs.gov.au/ausstats/abs@.nsf/DetailsPage/1259.0.30.0022006?OpenDocument) using the QGIS program. I used the *simplify geometries* function within that program, with a tolerance of 0.005, to reduce the detail to a suitable level for the web. Github has [the data files](https://github.com/edwinsteele/d3-projects/blob/master/data/au-states.geojson)

<script type="text/javascript" src="/d3-projects/lib/d3.v2.js"></script>
<script type="text/javascript">

awesomeness = {"New South Wales":8, // + it's NSW, - legacy of NSW Labor 
    "Victoria":6, // + Architecture, Food, - it's not NSW
    "Queensland":3, // + Beaches, - it's QLD, Wally Lewis
    "South Australia":7, // + Friends, Moonarie, - it's not NSW
    "Western Australia":4, // + Beautiful Coastline, Mining Revenues, - delusions of seccession
    "Tasmania": 6, // + table mountain, cheese, - weather
    "Northern Territory": 7, // + arnhem land, cumulo nimbus clouds over Darwin, - mosquitoes
    "Other Territories":5, // I'm sure they're ok
};

var w = 960,
    h = 400;

var z = d3.scale.category10();

var fill = d3.scale.log()
    .domain(d3.extent(d3.values(awesomeness)))
    .range(["brown", "steelblue"]);

var projection = d3.geo.azimuthal()
    .origin([135, -26])
    .translate([250,180])
    .scale(700);

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("#d3_top_level_div").append("svg")
    .attr("width", w)
    .attr("height", h);

var states = svg.append("g")
    .attr("id", "states");

d3.json("/d3-projects/data/au-states.geojson", function(collection) {
  states.selectAll("path")
      .data(collection.features)
    .enter().append("path")
    .attr("fill", function(d) {
     return fill(awesomeness[(d.properties["STATE_NAME"])]);
    })
    .attr("d", path);
});
</script>

[^1]: Please let me know of a source of Australian maps in geojson format, if you're aware of one

