// Column Headers
SLA_NAME_STR="SLA Name";
SLA_ID_STR="SLA ID";
GOOD_ENGLISH_PERC_STR="Percent IP with good english";
NO_GOOD_ENGLISH_PERC_STR="Percent IP without good english";
UNKNOWN_EVERYTHING_STR="Percent of unknown Indigenous status without stated english language proficiency (% of total IPs)";
SAMPLE_SIZE_STR="Indigenous Sample Size";
PROTESTANT_PERC_STR="Percent Protestant";
LANGUAGE_GROUP_STR="Dominant Indigenous Langauge Group";

/*
// Created in the map js when both are in the same page
var tooltip = d3.select("body")
  .append("div")
  .attr("id", "tooltip")
  .text("");
*/

d3.csv("/d3-projects/data/au-northern-territory-sla_ingp_lanp_engp_combined.csv", function(data) {
  var languageGroups = [],
      maxSampleSize = 0;

  var slaData = data.map(function(oneRow) {
    maxSampleSize = Math.max(maxSampleSize, parseFloat(oneRow[SAMPLE_SIZE_STR]));
    if (languageGroups.indexOf(oneRow[LANGUAGE_GROUP_STR]) == -1) {
      languageGroups.push(oneRow[LANGUAGE_GROUP_STR]);
    }
    return {sla_id: oneRow[SLA_ID_STR],
      sla_name: oneRow[SLA_NAME_STR],
      ge_perc: parseFloat(oneRow[GOOD_ENGLISH_PERC_STR]),
      unknowns_perc: parseFloat(oneRow[UNKNOWN_EVERYTHING_STR]),
      protestant_perc: parseFloat(oneRow[PROTESTANT_PERC_STR]),
      sample_size: parseInt(oneRow[SAMPLE_SIZE_STR]),
      dominant_language_group:oneRow[LANGUAGE_GROUP_STR],
    };
  });

  var legendDotSizes = [100,1000,2000,5000];

  var graphWidth = 800,
      graphHeight = 500,
      legendWidth = 200,
      legendTextHeight = 100,
      legendTextBottomPadding = 10,
      legendDotHeight = 100,
      legendLeftPadding = 10,
      legendRightPadding = 20,
      legendTopPadding = 20,
      graphLeftPadding = 50,
      graphRightPadding = 10,
      graphTopPadding = 20,
      graphBottomPadding = 20,
      minDatapointRadius = 1,
      maxDatapointRadius = 20,

      // dominant language group
      dlgColour = d3.scale.category10()
        .domain(languageGroups)
      dlgTextLegendPlacement = d3.scale.ordinal()
        .domain(languageGroups)
        .rangeRoundBands([0,legendTextHeight])
      dotLegendPlacement = d3.scale.linear()
        .domain(legendDotSizes)
        .range([legendTextHeight + legendTextBottomPadding + 0,
          legendTextHeight + legendTextBottomPadding + 33,
          legendTextHeight + legendTextBottomPadding + 66,
          legendTextHeight + legendTextBottomPadding + 100])
      // radius of datapoints
      r = d3.scale.sqrt()
        .domain([0,maxSampleSize])
        .range([minDatapointRadius,maxDatapointRadius]),
      // percentage with good english
      x = d3.scale.linear()
        .domain([0,1])
        .range([0,graphWidth]),
      // percentage protestant
      y = d3.scale.linear()
        .domain([1,0])
        .range([0,graphHeight]),
      xAxis = d3.svg.axis()
        .scale(x)
        .ticks(4)
        .tickSize(4,2)
        .tickFormat(d3.format("%")),
       yAxis = d3.svg.axis()
        .scale(y)
        .ticks(4)
        .tickSize(4,2)
        .tickFormat(d3.format("%"))
        .orient("left");

  var s = d3.select("#d3_top_level_div_scatter")
    .append("svg:svg")
      .attr("width", graphLeftPadding + graphWidth + graphRightPadding
         + legendLeftPadding + legendWidth + legendRightPadding)
      .attr("height", graphHeight + graphBottomPadding + graphTopPadding)

  var graphHolder = s.append("svg:g")
      .attr("class", "graphholder")
      .attr("transform", "translate(" + graphLeftPadding + "," + graphTopPadding + ")");

  graphHolder.append("svg:g")
    .attr("class", "axis")
    .attr("transform", "translate(0," + graphHeight + ")")
    .call(xAxis);

  graphHolder.append("svg:g")
    .attr("class", "axis")
    .call(yAxis);

  var legendHolder = s.append("svg:g")
      .attr("class", "legendholder")
      .attr("transform", "translate("
        + (graphLeftPadding + graphWidth + graphRightPadding + legendLeftPadding)
        + "," + legendTopPadding + ")");

  legendHolder.selectAll("g#legendholder")
    .data(languageGroups)
  .enter().append("svg:text")
    .attr("class", "legendtext")
    .attr("stroke", function(d) { return dlgColour(d); })
    .attr("y", function(d) { return dlgTextLegendPlacement(d); })
    .text(String);

  legendHolder.selectAll("g#legendholder")
    .data(legendDotSizes)
  .enter().append("svg:circle")
    .attr("fill", "#C0C0C0")
    .attr("cx", 10)
    .attr("cy", function(d) { return dotLegendPlacement(d); })
    .attr("r", function(d) { return r(d); })

  legendHolder.selectAll("g#legendholder")
    .data(legendDotSizes)
  .enter().append("svg:text")
    .attr("class", "legendtext")
    .attr("stroke", "#C0C0C0")
    .attr("x", 30)
    .attr("dy", "0.35em")
    .attr("y", function(d) { return dotLegendPlacement(d); })
    .text(function(d) { return "Pop: " + d; })

  var statisticalLocalArea = graphHolder.selectAll("g#graphholder")
    .data(slaData)
  .enter().append("a")
    .attr("class", "sla")
    .attr("xlink:href", function(d) {
      return "http://www.censusdata.abs.gov.au/ABSNavigation/ImageServer?id=map,Census,2006," + d.sla_id; })
    .attr("target", "new")

  statisticalLocalArea.append("svg:circle")
   .attr("class", "datapoint")
   .attr("cx", function(d) { return x(d.ge_perc); })
   .attr("cy", function(d) { return y(d.protestant_perc); })
   .attr("r", function(d) { return r(d.sample_size); })
   .attr("fill", function(d) { return dlgColour(d.dominant_language_group); })
   .on("mouseover", function(d) {
     s = d.sla_name + " (pop: " + d.sample_size + ")";
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
   .on("mouseout", function() { return tooltip.style("visibility", "hidden");})

});
