.. title: Spoken English Language Proficiency - Indigenous Australians in the NT
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

    <div id="d3_top_level_div"/>
    <style type="text/css">

        body {
          font-family: sans-serif;
        }
        
        .sla path {
          stroke: #fff;
          stroke-width: 0.1px;
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
granularity.

Map and data is available on `GitHub <https://github.com/edwinsteele/d3-projects/data>`_

.. raw:: html

    <script type="text/javascript" src="/d3-projects/lib/d3.v2.js"></script>
    <script type="text/javascript">
    
    SLA_NAME_STR="SLA Name";
    SLA_ID_STR="SLA ID";
    GOOD_ENGLISH_PERC_STR="Percent IP with good english";
    NO_GOOD_ENGLISH_PERC_STR="Percent IP without good english";
    UNKNOWN_EVERYTHING_STR="Percent of unknown Indigenous status without stated english language proficiency (% of total IPs)";
    SAMPLE_SIZE_STR="Indigenous Sample Size";
    
    csvFile="/d3-projects/data/au-northern-territory-sla_ingp_lanp_engp_combined.csv";
    geoJsonFile="/d3-projects/data/au-northern-territory_sla.json";
    
    var tooltip = d3.select("body")
      .append("div")
      .attr("id", "tooltip")
      .style("position", "absolute")
      .style("z-index", "10")
      .style("visibility", "hidden")
      .style("background-color", "yellow")
      .style("font-size", "12px")
      .text("");
    
    d3.csv(csvFile, function(data) {
    
      mapData = {};
      data.map(function(sla) {
        mapData[parseInt(sla[SLA_ID_STR])] = {
          "sla_name":sla[SLA_NAME_STR],
          "ge_perc":parseFloat(sla[GOOD_ENGLISH_PERC_STR]),
          "nge_perc":parseFloat(sla[NO_GOOD_ENGLISH_PERC_STR]),
          "unknowns_perc":parseFloat(sla[UNKNOWN_EVERYTHING_STR]),
          "sample_size":parseInt(sla[SAMPLE_SIZE_STR])
          };
      });
    
      var w = 500,
          h = 600;
    
      var fill = d3.scale.linear()
          .domain([0, 1])
          .range(["red", "green"]);
    
      var projection = d3.geo.mercator()
          .translate([-4500,-370])
          .scale(12800);
    
      var path = d3.geo.path()
          .projection(projection);
    
      svg = d3.select("#d3_top_level_div").append("svg")
            .attr("width", w)
            .attr("height", h)
          .append("g")
            .call(d3.behavior.zoom()
              .on("zoom", redraw))
    
      d3.json(geoJsonFile, function(collection) {
    
        var statisticalLocalArea = svg.selectAll("path")
              .data(collection.features)
            .enter().append("g")
            .attr("class", "sla");
    
        statisticalLocalArea.append("path")
          .on("mouseover", function(d) {
            slaCode = d.properties["SLA_CODE06"];
            s = d.properties["SLA_NAME06"];
            if ( mapData.hasOwnProperty(parseInt(slaCode)) ) {
              var md = mapData[parseInt(slaCode)];
              s += ": " + Math.round(md["ge_perc"] * 100) +
                 "% of indig. pop has good english (pop: " +
                  mapData[parseInt(d.properties["SLA_CODE06"])]["sample_size"] + ")";
            }
            var fieldNameElement = document.getElementById("tooltip");
            while(fieldNameElement.childNodes.length >= 1) {
                fieldNameElement.removeChild(fieldNameElement.firstChild);
            }
            fieldNameElement.appendChild(fieldNameElement.ownerDocument.createTextNode(s));
            return tooltip.style("visibility", "visible");
          })
          .on("mousemove", function() {
            return tooltip.style("top", (d3.event.pageY - 10) + "px")
                    .style("left",(d3.event.pageX + 10) + "px");
          })
          .on("mouseout", function() {return tooltip.style("visibility", "hidden");})
          .attr("fill", function(d) {
            slaCode = d.properties["SLA_CODE06"];
            if ( mapData.hasOwnProperty(parseInt(slaCode)) ) {
              return fill(mapData[parseInt(d.properties["SLA_CODE06"])]["ge_perc"]);
            }
            else {
              if ( slaCode.slice(0,3) == "705" ) {
                // We're in Darwin, that's ok
                return "grey";
              }
              else {
                console.log("mapData doesn't have a key for " + d.properties["SLA_NAME06"]);
                return "black";
              }
            }
           })
          .attr("d", path);
      });
    
    });
    
    function redraw() {
      svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }
    
    </script>

