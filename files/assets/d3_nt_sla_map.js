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

svg = d3.select("#d3_top_level_div_map").append("svg")
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
