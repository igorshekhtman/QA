import os.path
#JSON_LOC = 'this.is.test'

def generateHTML(environment, JSON_LOC):
  filename = '/var/www/html/html/' +environment + '.' + JSON_LOC + '.html'
  #completeName = os.path.join("../html/",filename)
  
  f = open(filename,'w+')
  template = """

        <meta http-equiv="refresh" content="60">
    <script src="http://mbostock.github.com/d3/d3.v2.js"></script>

    <script language="javascript" type="text/javascript" src="jquery.js"></script>
  <style>
      /* tell the SVG path to be a thin blue line without any area fill */
      path {
        stroke: steelblue;
        stroke-width: 3;
        fill: none;
      }

      .axis {
        shape-rendering: crispEdges;
      }

      .x.axis line {
        stroke: lightgrey;
      }

      .x.axis .minor {
        stroke-opacity: .5;
      }

      .x.axis path {
        display: none;
      }

      .y.axis line, .y.axis path {
        fill: none;
        stroke-width: 1;
        stroke: #000;
      }
          div.tooltip {
  position: absolute;
  text-align: center;
  width: 80px;
  height: 40px;
  padding: 2px;
  font: 12px sans-serif;
  background: lightsteelblue;
  border: 0px;
  border-radius: 8px;
  pointer-events: none;
}
    </style>
  </head>
  <body>
    <center><h2>Quality Dashboard</h2></center>
    <h3>Charts</h3>
    <div id="graphTwo" class="aGraph"></div>
    <div id="legendTwo" class="legend" ></div>
  <script>
    //Pipeline - Daily Dashboard
    update();

  var updateInterval;
  function update() {

          console.log("just updated");

  $.ajaxSetup({
    async: false
    });

  $.getJSON("../json/%s.json", function( json ) {


  updateInterval = json.updateInterval * 1000;


        // Labels for Graphs
    var labelText = json.charttitle;

    // axes' labels
    var yLabel = json.yaxistitle;
        var xLabel = json.xaxistitle;

  // Data for 1st graph
        var allData = [];
        for ( a = 1; a <= Object.keys(json.yaxisdata).length; a++) {
                allData.push(json.yaxisdata[a].map(Number));
        }
        var baselineData = [];
        for ( z = 1; z <= Object.keys(json.baselinedata).length; z++) {
                baselineData.push(json.baselinedata[z].map(Number));
        }
    // browser window dimensions

        var frameHeight = (parent.window.frames[2].innerHeight);
        var frameWidth = (parent.window.frames[2].innerWidth);

    // dimensions of graph
        var m = [80, 80, 80, 80]; // margins

        var w = frameWidth - m[0] * 4.5;
        var h = frameHeight/2.5;

        var graphTop = h/4;

    // dimensions of legend
    var legHeight = 20;
    var legWidth = 220;

        var barWidth = w / ((baselineData[0].length*baselineData.length) + (allData[0].length*allData.length));

        // Legend Colors
        var legColors = [];
        for ( b = 1; b <= Object.keys(json.legendcolors).length; b++) {
                legColors.push(json.legendcolors[b]);
        }

    // 1st graph legend rectangle design and messages.
        var legendRectangles = [];
          for (c = 0; c < Object.keys(json.legendcolors).length; c++) {
                var obj = new Object();
                        obj.xloc = m[0] + legWidth * (Math.floor(c / 4) );
                        obj.yloc = 10 + ((legHeight * c) %s 80);
                        obj.width = legWidth;
                        obj.height = legHeight;
                        obj.color = legColors[c];
                        obj.message = json.legenddata[c + 1];
                legendRectangles.push(obj);
          }

        // x axis values
    var xScaleVals = json.xaxisdata[1];

    // sets dimensions of graphs to be dynamic for the window.
    var graph1Loc = d3.select("#graphTwo")
              .style("position","fixed")
              .style("top",graphTop)
              .style("left",m[0]/2)
                          .style("width",frameWidth);

    var leg1Loc = d3.select("#legendTwo")
              .style("position","fixed")
              .style("top",graphTop + h + m[0] * 1.5)
              .style("left",m[0]/2)
                          .style("width",frameWidth);

    // object with function to make several graphs
    var Grapher = {
      graphThis : function(graphNum, legendNum, mainLabel, yLabel, xLabel,data,dottedData, legendRects, legendColors, scaleValues) {

    // find max value of the data to determine y-axis scale
    var maxVal = d3.max(data.concat(dottedData), function(d) { return d3.max(d); });

    // X scale will fit all xScaleVals within pixels 0-w
    var x = d3.scale.linear().domain([0,scaleValues.length - 1]).range([0, w]);


    // Y scale will fit values from 0-maxVal within pixels h-0 (Note the inverted domain for the y-scale: bigger is up!)
    var y = d3.scale.linear().domain([0, maxVal]).range([h, 0]);
    // create a line function that can convert data[] into x and y points
    var line = d3.svg.line()
                .interpolate("monotone")
                .x(function(d,i) {return x(i);})
                .y(function(d)   {return y(d);});

     // delete old svg element on update.
   d3.select("#graphSVG").remove();
    // Add an SVG element with the desired dimensions and margin.
    var yaxisspacing = 1.0;
        if (maxVal >= 1000000000) {
                yaxisspacing = 1.6
        } else if(maxVal >= 1000000) {
                yaxisspacing = 1.4;
          } else if(maxVal >= 100000){
                yaxisspacing = 1.2;
          } else {
                yaxisspacing = 1.0;
          }

        var graph = d3.select("#" + graphNum).append("svg:svg")
            .attr("id", "graphSVG")
      .attr("width", frameWidth)
            .attr("height", h + m[0] + m[2])
          .append("svg:g")
            .attr("transform", "translate(" + m[3]*yaxisspacing + "," + m[0] + ")");

      // create xAxis
      var xAxis = d3.svg.axis().scale(x).tickSize(-h).ticks(scaleValues.length).tickFormat(function(d, i){return scaleValues[d]});

      // Add the x-axis.
      graph.append("svg:g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + h + ")")
            .call(xAxis);

      // create left yAxis
      var yAxisLeft = d3.svg.axis().scale(y).ticks(8).orient("left");

      // Add the y-axis to the left
          graph.append("svg:g")
            .attr("class", "y axis")
            .attr("transform", "translate(-20,0)")
            .call(yAxisLeft);

 d3.select("#vertLabel").remove();
      //adds y axis textual label
      var vertLabel = d3.select("body")
                .append("div")
                        .attr("id","vertLabel")
                        .style("position","fixed")
            .style("top",graphTop + m[0])
            .style("left",0)
                .append("svg")
                        .attr("width",m[0]/2)
                        .attr("height",h)
            .attr("class", "y axis label")
                .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", m[0] * 0.4 )
            .attr("x", 0 - h / 2 )
            .style("text-anchor", "middle")
            .text(yLabel);

   //adds x axis textual label

    graph.append("svg:g")
          .attr("class", "x axis label")
        .append("text")
          .attr("y", h + m[0] * 0.4)
          .attr("x", w / 2)
          .style("text-anchor", "middle")
          .text(xLabel);

  //adds title to legend
    graph.append("svg:g")
          .attr("class", "Legend label")
        .append("text")
          .attr("y", h + m[0] * 0.5)
          .attr("x", 0 + m[0] / 4)
          .style("text-anchor", "middle")
          .text(json.legendtitle[1]);

      //adds main label to top of graph
      graph.append("svg:g")
          .attr("class", "main label")
        .append("text")
          .attr("x", w / 2)
          .attr("y", 0 - (m[0] / 2))
          .style("text-anchor", "middle")
          .text(mainLabel);

      //draws x axis
      graph.append("svg:g")
          .attr("class","xLine")
          .append("path")
          .attr("d", "m0 " + h + " l" + w + " 0")
          .style({"stroke": "black","stroke-width": 1});

          d3.select("#info").remove();
          var div = d3.select("body").append("div")
                        .attr("id","info")
                        .attr("class", "tooltip")
                        .style("opacity", 0);

          var legendInfo = "Dotted Line";

          if (json.charttype == "bar") {

          legendInfo = "Shaded Bar";

          graph.append("svg:svg").attr("id","currData");
                for ( numSets = 0; numSets < data.length; numSets++) {
                        for( numBars = 0; numBars < data[numSets].length; numBars++) {
                                d3.select("#currData")
                                        .append("rect").attr("width",barWidth).attr("height",h - y(dottedData[numSets][numBars])).attr("x",x(numBars) + (barWidth * (numSets*2+1))).attr("y",y(dottedData[numSets][numBars])).style("fill",legendColors[numSets]).style("opacity",0.3).on("mouseover",
                        function(d) {
            div.transition()
                .duration(50)
                .style("opacity", .9);
            div .text("Base-Line Data")
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 35) + "px");
            })
        .on("mouseout", function(d) {
            div.transition()
                .duration(400)
                .style("opacity", 0);
        });

                        }
                };
                graph.append("svg:svg").attr("id","oldData");
                for ( Sets = 0; Sets < data.length; Sets++) {
                        for( Bars = 0; Bars < data[Sets].length; Bars++) {
                                d3.select("#oldData")
                                        .append("rect").attr("width",barWidth).attr("height",h - y(data[Sets][Bars])).attr("x",x(Bars) + (barWidth * (Sets*2))).attr("y",y(data[Sets][Bars])).style("fill",legendColors[Sets]).on("mouseover",
                        function(d) {
            div.transition()
                .duration(50)
                .style("opacity", .9);
            div .text("Current Data")
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 35) + "px");
            })
        .on("mouseout", function(d) {
            div.transition()
                .duration(400)
                .style("opacity", 0);
        });

                        }
                };

        } else if(json.charttype == "line") {
        legendInfo = "Dotted Line";
        var circles = [];
      // graphs the data
      for ( i = 0; i < data.length; i++) {

                graph.append("svg:g").attr("id","line" + i.toString())
          .append("path")
          .attr("d", line(data[i]))
          .style({"stroke": legendColors[i],"stroke-width": 3, "opacity": 1});
                circles.push(graph.select("#line" + i.toString()).selectAll("circle").data(data[i]).enter().append("circle"));
                for (f = 0; f < data[i].length; f++) {
                        d3.select(circles[i][0][f]).attr("cy",y(data[i][f])).attr("cx",x(f)).attr("r",json.dotSize).style("fill",json.dotColor).on("mouseover",
                        function(d) {
            div.transition()
                .duration(50)
                .style("opacity", .9);
            div .text(json.yaxistitle +  ": " + d)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 35) + "px");
            })
        .on("mouseout", function(d) {
            div.transition()
                .duration(400)
                .style("opacity", 0);
        });
                }
      }

                        var dotcircles = [];
      // graphs the data
      for ( j = 0; j < dottedData.length; j++) {

                graph.append("svg:g").attr("id","dotted" + j.toString())
          .append("path")
                  .attr("stroke-dasharray","10,10")
          .attr("d", line(dottedData[j]))
          .style({"stroke": legendColors[j],"stroke-width": 7, "opacity": 0.3});
                dotcircles.push(graph.select("#dotted" + j.toString()).selectAll("circle").data(dottedData[j]).enter().append("circle"));
                for (t = 0; t < dottedData[j].length; t++) {
                        d3.select(dotcircles[j][0][t]).attr("cy",y(dottedData[j][t])).attr("cx",x(t)).attr("r",json.dotSize).style("fill",json.dotColor).on("mouseover",
                        function(d) {
            div.transition()
                .duration(50)
                .style("opacity", .9);
            div .text(json.yaxistitle +  ": " + d)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 35) + "px");
            })
        .on("mouseout", function(d) {
            div.transition()
                .duration(400)
                .style("opacity", 0);
        });
                }
      }
        }
         d3.select("#legendSVG").remove();
      //Handles the Legend portion of the graph.
      var legend = d3.select("#" +legendNum).append("svg:svg")
        .attr("id", "legendSVG")
        .attr("width", frameWidth)
        .attr("height", 500);

      // generates the legend rectangles
      var legBars = legend.append("svg:g")
            .attr("class","legendRects")
           .selectAll("rect")
            .data(legendRects)
            .enter()
            .append("rect");

      // sets the attributes of the legend rectangles
      var legAttributes = legBars
                      .attr("x", function (d) { return d.xloc; })
                      .attr("y", function (d) { return d.yloc; })
                      .attr("width", function (d) { return d.width; })
                      .attr("height", function(d) { return d.height; })
            .style("fill", function(d) { return d.color; });

      // generates the text labels for the legend rectangles
      var text = legend.select("g").selectAll("text")
            .data(legendRects)
            .enter()
            .append('svg:text');

      // sets the message and attributes for text labels for the legend rectangles
      var textAttributes = text
            .text(function (d) {return d.message;})
            .attr('x', function (d) { return d.xloc * 1.1 ;} )
            .attr('y', function (d) { return d.yloc + legHeight / 1.5 ;} )
            .attr('fill', 'black')
			.style('font-weight', 'bold');

          var baselineLeg = legend.append("text")
                .text(legendInfo + " = Base-Line Data")
                .attr("x", w/2)
                .attr("y", legHeight*5);
    }
      }

    Grapher.graphThis("graphTwo","legendTwo",labelText,yLabel,xLabel,allData,baselineData,legendRectangles,legColors,xScaleVals);
  });

  setTimeout(update, updateInterval);
  }

  </script>
  </body>
	</html>""" % (environment + '.' + JSON_LOC, "%")

  f.write(template)
  f.close()
  
#generateHTML("staging",JSON_LOC)
