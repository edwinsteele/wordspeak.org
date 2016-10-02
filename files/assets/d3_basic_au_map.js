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
