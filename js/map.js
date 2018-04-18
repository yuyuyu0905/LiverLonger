function compare(property) {
    return function(a, b) {
        var value1 = a[property];
        var value2 = b[property];
        return value2 - value1;
    }
}

var w = 1250,
    h = 600,
    pad = 20,
    h2 = 150;
var tooltip = d3.select("body").append("div").attr("class", "toolTip");
var svg_3 = d3.select('#div-geo').append('svg')
    .attr('preserveAspectRatio',"xMinYMin meet")
    .attr('viewBox',"-150 0 1650 600")
var projection = d3.geoAlbersUsa()
    .scale([1200])
    .translate([w / 2, h / 2])
var svg2_3 = d3.select('#div-barchart').append('svg')
    .attr('id', 'barchart')
   .attr('width', w + 20)
    .attr('height', h2 + 40);

var lowColor = '#ffffb2';
var highColor = '#bd0026';
var ramp = d3.scaleLinear()
        .domain([91,95])
        .range([lowColor,highColor]);

// svg2_3.append("text")
//       .attr("transform", "rotate(-90)")
//       .attr("y", 0)
//       .attr("x",0 - (h2 / 2 + 30))
//       .attr("dy", "1em")
//       .style("text-anchor", "middle")
//       .text("Salary ($)");

svg2_3.append("text")
      .attr('id', 'rank')
      .attr("y", h2 + 20)
      .attr("x",(w / 2 + 30))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text("Ranks");
var path = d3.geoPath()
    .projection(projection);

function bars(data) {
    var l = data.length
    //console.log(data);
    max = data[0];
    var x = d3.scaleBand()
        .range([15, 30 * l + 15])
        .round(true)
        .domain(data.map(function(d, i) { return i + 1; }))

    var div = d3.select("body").append("div").attr("class", "toolTip");
    d3.select('#axis').call(d3.axisBottom(x));

    d3.select('#barchart').attr('width', Math.max(960, 30 * data.length))
    d3.select('#rank')
    .transition().duration(1000).attr('x', 30 * data.length / 2 + 30)

}
d3.json("data/usa2.json", function(error, world) {
    svg_3.append('path')
        .attr('class', 'graticule')
        .attr('d', path);
    svg_3.selectAll('path')
        .data(world.features)
        .enter()
        .append("path")
        .attr('class', 'path')
        .attr('id', function(d) { return d['properties']['abbr']; })
        .attr("fill", function(d, i) {
            return 'rgb(230,210,210)'
        })
        .attr('stroke', 'black')
        .attr('d', path);




    d3.csv("data/wage_gap_all.csv", function(error, data) {
        var state_map = {}
        var region_map = {}
        var state_data = d3.nest()
            .key(function(d) { return d['State']; })
            .entries(data);

        var region_data = d3.nest()
            .key(function(d) { return 'Region' + d['Region']; })
            .entries(data);
        console.log(state_data);
        console.log(region_data);
        var avg_data = d3.nest()
            .key(function(d) { return d['State']; })
            .rollup(function(v) {
                return {
                    count: v.length,
                    Stage1: d3.mean(v, function(d) { return d['Stage1']; }),
                    Stage2: d3.mean(v, function(d) { return d['Stage2']; }),
                    Stage3: d3.mean(v, function(d) { return d['Stage3']; }),
                    WaitingTime: d3.mean(v, function(d) { return d['WaitingTime']; }),

                };
            })
            .entries(data);
        console.log(avg_data);
        var region_avg_data = d3.nest()
            .key(function(d) { return 'Region' + d['Region']; })
            .rollup(function(v) {
                return {
                    count: v.length,
                    Stage1: d3.mean(v, function(d) { return d['Stage1']; }),
                    Stage2: d3.mean(v, function(d) { return d['Stage2']; }),
                    Stage3: d3.mean(v, function(d) { return d['Stage3']; }),
                    WaitingTime: d3.mean(v, function(d) { return d['WaitingTime']; }),
                };
            })
            .entries(data);
        console.log(region_avg_data);


        for (i = 0; i < state_data.length; i++) {
            state_map[state_data[i].key] = i
        }

        for (i = 0; i < region_data.length; i++) {
            region_map[region_data[i].key] = i
        }
        console.log(state_map);
        console.log(region_map)
        for (i = 0; i < state_data.length; i++) {
            d3.select('#' + state_data[i]['values'][0]['State'])
                .attr('class', 'Region' + state_data[i]['values'][0]['Region'])
            state_map[state_data[i].key] = i
        }
        byState('Stage1');
        function byState(attr) {
        	max_value = d3.max(data, function(d) { return d[attr];});
        	min_value = d3.min(data, function(d) { return d[attr];});
        	if(attr == "WaitingTime"){
        		var ramp = d3.scaleLinear()
        	    .domain([min_value, max_value])
        	    .range([lowColor, highColor]);
        	}else{
        		var ramp = d3.scaleLinear()
        	    .domain([max_value, min_value])
        	    .range([lowColor, highColor]);
        	}
            d3.select('#map_legend').style("display", "inline");
            d3.select('#map_legend_2').style("display", "inline");
            for (i = 0; i < avg_data.length; i++) {
                res = avg_data[i]['value'][attr];
                temp = avg_data[i]['value'][attr];
                d3.select('#' + avg_data[i]['key'])
                    .style('stroke', function(d) {
                        d[attr] = temp;
                        // d['avg_md'] = avg_data[i]['value']['avg_md'];
                        d['color'] = ramp(res);
                        return 'black'
                    })
                    .style('fill', function(d) {return d['color']})
                    .on("click touchstart", function(d) {
                        for (i = 0; i < avg_data.length; i++) {
                            d3.select('#' + avg_data[i]['key'])
                                .style('fill', function(d) { return d['color'] })
                        }
                        // console.log('#' + d3.select(this).attr('id'))
                        d3.select('#' + d3.select(this).attr('id'))
                            // .style('fill', function(d, i) {
                            //     return color(i);
                            // })
                            .style('stroke-width', '5px')
                        var current = state_data[state_map[d.properties.abbr]];
                        var current_state = current['key'];
                        var colleges = current['values'];
                        colleges.sort(compare('Starting Median Salary'));
                        // console.log(current_state);
                        // console.log(colleges);
                        // console.log(state_data[state_map[d.properties.abbr]]);
                        //bars(colleges);
                    })
                    .on("mousemove", function(d) {
                        tooltip
                            .style("left", d3.event.pageX - 100 + "px")
                            .style("top", d3.event.pageY - 100 + "px")
                            .style("display", "inline-block")
                            .html(d['properties']['NAME'] + "<br>" + "Success Rate: " + d[attr].toLocaleString());
                    })
                    .on("mouseout", function(d) {
                        tooltip.style("display", "none");
                        d3.select('#' + d3.select(this).attr('id'))
                            .style('stroke-width', '1px')
                    })
                    .style('fill', 'rgb(' + (res-100) + ',' + res + ', ' + res + ')')

            }
        }


        var selected = d3.selectAll('input[name="input_value"]').on('click', function(d){byState(d3.select(this).node().value)});
        function byRegion() {
            d3.select('#map_legend').style("display", "none");
            d3.select('#map_legend_2').style("display", "none");

            for (i = 0; i < region_avg_data.length; i++) {
                res = parseInt((region_avg_data[i]['value']['avg_st'] - 90) / 3 * 255);
                temp = region_avg_data[i]['value']['avg_st'];
                temp2 = region_avg_data[i]['key'];
                var color = d3.scaleOrdinal(d3.schemeCategory20c);
                d3.selectAll('.' + region_avg_data[i]['key'])
                    .style('stroke', function(d) {
                        d['avg_st'] = temp;
                        d['avg_md'] = avg_data[i]['value']['avg_md'];
                        d['color'] = 'rgb(' + (res - 100) + ',' + res + ', ' + res + ')'
                        return 'black'
                    })
                    .on("click touchstart", function(d) {
                        for (i = 0; i < region_avg_data.length; i++) {
                            d3.selectAll('.' + region_avg_data[i]['key'])
                                // .style('fill', 'grey')
                                .style('stroke-width', '1px')
                                // .transition()
                        }
                        d3.selectAll('.' + d3.select(this).attr('class'))
                            // .style('fill', function(d, i) {
                            //     return color(i);
                            // })
                            .style('stroke-width', '5px')
                            .style('opacity', 1)
                            .transition()
                        var current = region_data[region_map[d3.select(this).attr('class')]];
                        var current_state = current['key'];
                        var colleges = current['values'];
                        colleges.sort(compare('Starting Median Salary'));
                        // console.log(current_state);
                        // console.log(colleges);
                        // console.log(state_data[state_map[d.properties.abbr]]);
                        // bars(colleges);
                    })
                    .on("mousemove", function(d) {
                        d3.selectAll('.' + d3.select(this)
                                .attr('class')).style('opacity', 0.9)
                            .attr('stroke-width', '3px')

                        tooltip
                            .style("left", d3.event.pageX - 100 + "px")
                            .style("top", d3.event.pageY - 100 + "px")
                            .style("display", "inline-block")
                            .html(d3.select(this).attr('class') + "<br>" + "States: " + d['properties']['NAME'] + "<br>" + "Success Rate: " + d['avg_md']);


                    })
                    .on("mouseout", function(d) {
                    	console.log(d3.select(this).attr('class'))
                        d3.selectAll('.' + d3.select(this).attr('class'))
                            .style('opacity', 1)
                            // .style('fill', function(d){return d['color']})
                            .attr('stroke-width', '1px')
                        tooltip.style("display", "none");
                    })


            }
        }
        d3.select('#button-state')
            .on('click', function(d) {
            	console.log(d3.select('input[name="input_value"]:checked').node().value)
                byState(d3.select('input[name="input_value"]:checked').node().value)})
        d3.select('#button-region')
            .on('click', function(d) {
                byRegion();
            })
        // console.log(data);
        var x = d3.scaleBand()
            .range([0, w - 40])
            .round(true)
            .domain(state_data.map(function(d) { return ''; }))
            .padding(0.1);

        var y = d3.scaleLinear()
            .domain([0, 60])
            .range([h2, 0]);

        var main = svg2_3.append('g')
            .attr('transform', 'translate(' + 20 + ',' + 0 + ')')

        // main.append("g")
        //     .attr('id', 'axis')
        //     .attr("transform", "translate(0," + (h2) + ")")
        //     .call(d3.axisBottom(x));


        main.append("text")
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .attr('transform', 'translate(820, 470) rotate(' + 90 + ')');
        var g = svg_3.append('g').attr('id','map_legend');
          var myScale = d3.scaleLinear()
                          .domain([0, 10])
                          .range([91, 95])
          g.selectAll('rect')
            .data([0,1,2,3,4,5,6,7,8,9,10])
            .enter()
            .append('rect')
            .attr('x', function(d){return 20 *(d + 33);})
            .attr('y', h - 40)
            .attr('width', function(d){return 20})
            .attr('height', 20)
            .style('fill', function(d){
              var res = 4.0 * (d / 10) + 91
              return ramp(res);
            })
          var g = svg_3.append('g').attr('id','map_legend_2');
          g.selectAll('text')
            .data([0,3,7,10])
            .enter()
            .append('text')
            .style('text-anchor', 'middle')
            .attr('x', function(d){return 20 *(d + 33);})
            .attr('y', h - 50)
            .text(function(d){return parseInt(myScale(d)).toLocaleString()});

          g.selectAll('rect')
            .data([0,3,7,10])
            .enter()
            .append('rect')
            .attr('x', function(d){return 20 *(d + 33);})
            .attr('y', h - 44)
            .attr('width', function(d){return 3})
            .attr('height', 24)
            .text(function(d){return parseInt(myScale(d))})

        //console.log(avg_data)
    });
});