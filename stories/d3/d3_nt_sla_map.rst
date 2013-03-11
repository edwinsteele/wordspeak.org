.. title: Map of Spoken English Language Proficiency for Indigenous Australians in the NT
.. slug: d3-nt-sla-map
.. date: 2013/03/10 17:56:01
.. tags: 
.. link: 
.. description: 


Proficiency in Spoken English Amongst Indigenous Australians in NT
------------------------------------------------------------------

This was an exercise in finding the number of data dimensions that could be put into a
single infographic. It shares the same dataset as the `scatterplot </pages/d3/d3-nt-sla-scatter.html>`_
and served as a concrete example of where maps have value over other types of
graphical representation. In technical terms, this provided an opportunity to:

* develop a GeoJSON map with more complicated boundaries than the simple Australian map that I'd created previously. The challenge was ensuring map areas remained enclosed as the number of polygons was reduced. A smaller file often led to *bleeding* of areas when the area was filled.
* generate a meaningful and interesting multi-dimensional dataset
* learn how to zoom and scroll the map, which was surprisingly easy (if you're willing to tolerate a few glitches)
* implement mouse-overs to show another dimension of data, even though it requires the user to interact with the graph to extract that data.  There doesn't seem to be a clean way to do mouse-overs as the SVG spec doesn't offer z-positioning, so the method feels a bit dirty.

.. raw:: html

    <div id="d3_top_level_div_map"/>
    <style type="text/css">

        body {
          font-family: sans-serif;
        }
        
        .sla path {
          stroke: #fff;
          stroke-width: 0.1px;
        }
        
    </style>

Stuff about the scatterplot

.. raw:: html

    <div id="d3_top_level_div_scatter"/>
    <style type="text/css">
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


The map came from the ESRI Shapefiles of the `Northern Territory Statistical Local Areas <http://www.abs.gov.au/ausstats/abs@.nsf/DetailsPage/1259.0.30.0022006?OpenDocument>`_
that were available as a part of the Australian 2006 Census. It was converted
to GeoJSON format in the QGIS program, after reducing the complexity using the
QGIS *simplify geometries* function with a tolerance of 0.005.

The numerical data was also obtained from 2006 Census data using the (now
superceded) *CDATA online* tool focussing on dimensions of spoken english
language, indigenous language and religion dimensions for the indigenous
population in the Northern Territory. The dataset required extra processing
as the CDATA pivot tables needed aggregation to give the appropriate level of
granularity. The current tool for this type of analysis of Census data is
called `TableBuilder <http://www.abs.gov.au/websitedbs/censushome.nsf/home/tablebuilder?opendocument&navpos=240>`_.
It may provide a level of control that makes this post-processing uneccessary.

Map and data is available on `GitHub <https://github.com/edwinsteele/d3-projects/data>`_

.. raw:: html

    <script type="text/javascript" src="/d3-projects/lib/d3.v2.js"></script>
    <script type="text/javascript" src="/assets/d3_nt_sla_map.js"></script>
    <script type="text/javascript" src="/assets/d3_nt_sla_scatter.js"></script>

