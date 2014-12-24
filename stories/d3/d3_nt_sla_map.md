<!--
.. title: Map of Spoken English Language Proficiency for Indigenous Australians in the NT
.. slug: d3-nt-sla-map
.. date: 2013/03/10 17:56:01
.. spellcheck_exceptions: 
.. tags: Technology, Visualisation
.. link: 
.. description: 
-->


Proficiency in Spoken English Amongst Indigenous Australians in NT
==================================================================

This was an exercise in maximising data density, and an experiment in different forms of presentation of the same dataset. Both graphics below share the same dataset, which was interesting because it was real, multi-dimensional data from the 2006 Australian Census.

In technical terms the map provided an opportunity to:

-   develop a GeoJSON map with more complicated boundaries than the simple Australian map that I'd created previously. The challenge was ensuring map areas remained enclosed as the number of polygons was reduced. A smaller file often led to *bleeding* of areas when the area was filled.
-   learn how to zoom and scroll the map, which was surprisingly easy (if you're willing to tolerate a few glitches)
-   implement mouse-overs to show another dimension of data, even though it requires the user to interact with the graph to extract that data. There doesn't seem to be a clean way to do mouse-overs as the SVG spec doesn't offer z-positioning, so the method feels a bit dirty.

<div id="d3_top_level_div_map"></div>
<style type="text/css">

    .sla path {
      stroke: #fff;
      stroke-width: 0.1px;
    }

    .axis path {
      fill: none;
      stroke: #C0C0C0;
    }

    .axis text {
      font-size: 9px;
    }

    .legendtext {
      font-size: 10px;
      stroke-width: 0.75px;
    }

    #tooltip {
      position: absolute;
      z-index: 10;
      visibility: hidden;
      background-color: yellow;
      font-size: 12px;
    }

</style>

This scatterplot attempts to help answer the following question:

Where is the greatest opportunity for missionary work in NT indigenous Australian communities if we wanted to minimise the effect of language barriers?

<div id="d3_top_level_div_scatter"></div>

The dataset only includes the indigenous community, those who said they are Aboriginal or Torres Strait Islanders and who were in the Northern Territory on census night. The dimensions are:

x-axis
:   percentage that consider themselves protestant christian

y-axis
:   percentage that consider they have "good" or "excellent" spoken english

data-points
:   each point refers to a census Statistical Local Area (SLA). This was the smallest geographical subdivision in the 2006 census.

colour
:   the bubbles are coloured by the largest language group in the SLA. While this is another dimension on the graph, it adds little value as there is such (magnificent) diversity within those language groups. It was an example of how another dimension could be added to the graph.

size
:   the bubble is scaled to show the indigenous population in the SLA.

The name of the SLA is shown, along with population, as a mouse-over, and a map (of dubious value) is shown when the bubble is clicked.

Apologies for the lack of labelling - I found axis labels quite hard in d3.

This graph took quite some time, and taught me about:

-   text placement on a canvas
-   the perils of using areas to represent a relative values (humans aren't able to compare the size of areas very well)
-   linking from canvas objects
-   drawing on a canvas

I'm really pleased with this scatterplot as a proof of concept.

The map came from the ESRI Shapefiles of the [Northern Territory Statistical Local Areas](http://www.abs.gov.au/ausstats/abs@.nsf/DetailsPage/1259.0.30.0022006?OpenDocument) that were available as a part of the Australian 2006 Census. It was converted to GeoJSON format in the QGIS program, after reducing the complexity using the QGIS *simplify geometries* function with a tolerance of 0.005.

The numerical data was also obtained from 2006 Census data using the (now superceded) *CDATA online* tool focussing on dimensions of spoken english language, indigenous language and religion dimensions for the indigenous population in the Northern Territory. The dataset required extra processing as the CDATA pivot tables needed aggregation to give the appropriate level of granularity. The current tool for this type of analysis of Census data is called [TableBuilder](http://www.abs.gov.au/websitedbs/censushome.nsf/home/tablebuilder?opendocument&navpos=240). It may provide a level of control that makes this post-processing uneccessary.

My Github repo has the [Map and data files](https://github.com/edwinsteele/d3-projects/tree/master/data)

<script type="text/javascript" src="/d3-projects/lib/d3.v2.js"></script>
<script type="text/javascript" src="/assets/d3_nt_sla_map.js"></script>
<script type="text/javascript" src="/assets/d3_nt_sla_scatter.js"></script>

