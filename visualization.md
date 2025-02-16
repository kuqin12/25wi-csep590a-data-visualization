---
title: Interactive Visualization Submission
toc: false
---

# Interactive Visualization Submission

Update the content of this page with your [Interactive Visualization](../w6/assignment) submission. If working as a team, all team members should post same the content in each person's individual repository.

You are encouraged to delete all existing content on this page and replace it with your own!

```js echo
import { render } from "../components/vega-lite.js";
import { hexbin as d3Hexbin } from "d3-hexbin";

// Load the teams, players and shots data
var players = await d3.csv("https://raw.githubusercontent.com/kuqin12/25wi-csep590a-data-visualization/refs/heads/main/all_players.csv");
players = players.sort((a, b) => a.last_name.localeCompare(b.last_name));

var teams = await d3.csv("https://raw.githubusercontent.com/kuqin12/25wi-csep590a-data-visualization/refs/heads/main/all_teams.csv");
teams = teams.sort((a, b) => a.full_name.localeCompare(b.full_name));

const shots_contested = await d3.csv("https://raw.githubusercontent.com/kuqin12/25wi-csep590a-data-visualization/refs/heads/main/x_shot_summary_2014_2024_contested.csv", d3.autoType);

const geo_data = FileAttachment("../data/city-weather.json").json();

const shots_loc = FileAttachment("../data/x_shot_summary_2014_2024_loc.csv").csv({type: d3.autoType});
```

```js echo
// ------------------------------------------------------------------------------
// |                        |                               |                   |
// |                        |                               |                   |
// |                        |                               |                   |
// |                        |                               |-------------------|
// |                        |                               |                   |
// |                        |                               |                   |
// |------------------------|                               |                   |
// |                        |                               |                   |
// |                        |                               |                   |
// |                        |                               |                   |
// |                        |                               |                   |
// |                        |                               |                   |
// |                        |                               |                   |
// ------------------------------------------------------------------------------

// Define some constants for the chart
const view_width = 1080;
const view_height = 700;

// For shot chart
const shot_width = view_width * 0.3;
const shot_height = view_height / 2;

// For court chart
const court_width = view_width * 0.4;

// For search box
const search_width = view_width * 0.3;
const search_height = 200;

// For auto chart
const auto_width = search_width;
const auto_height = view_height - search_height;
```

```js echo
display((() => {
    const svg = d3.create("svg")
        .attr("viewBox", [0, 0, view_width, view_height]);

    // Create a group element to hold the team selector
    const selectorGroup = svg.append("g")
        .attr("transform", `translate(${shot_width + court_width}, 0)`);

    // Create an input element inside the SVG
    const foreignObject = selectorGroup.append("foreignObject")
            .attr("width", search_width - 10)
            .attr("height", search_height)

    const body = foreignObject.append("xhtml:body")
        .style("margin", "0")
        .style("padding", "0");

    const input = body.append("input")
        .attr("type", "text")
        .attr("id", "autocomplete-input")
        .attr("style", "width: 90%; height: 100%;")
        .attr("placeholder", "Search for a team or player...");

    // Function to get the value of the input element
    function getInputValue() {
        return d3.select("#autocomplete-input").property("value").toLowerCase();
    }

    // Filter the data based on the input value
    input.on("input", function() {
        const value = getInputValue();
        const suggestions = teams.filter(d => d.full_name.toLowerCase().includes(value))
        .concat(players.filter(d => d.full_name.toLowerCase().includes(value)));
        showSuggestions(suggestions);
    });

    // Function to display the suggestions
    function showSuggestions(suggestions) {
        d3.select("#suggestions").remove();

        const suggestionsContainer = body.append("div")
            .attr("id", "suggestions")
            .attr("style", "position: absolute; width: 90%; max-height: 150px; overflow-y: auto; background: white; border: 1px solid #ccc;");
        suggestions.forEach(suggestion => {
            suggestionsContainer.append("div")
                .attr("style", "padding: 5px; cursor: pointer;")
                .text(suggestion.full_name)
                .on("click", function() {
                    d3.select("#autocomplete-input").property("value", suggestion.full_name);
                    d3.select("#suggestions").remove();
                    update(suggestion.id);
                });
        });
    }

    svg.append('g')
        .attr('class', 'chart')
        .attr('id', 'auto_chart')
        .attr('transform', `translate(${shot_width + court_width},${search_height})`)
        .append('image')
        .attr('xlink:href', 'https://cdn.1min30.com/wp-content/uploads/2018/03/logo-NBA.jpg')
        .attr('width', auto_width)
        .attr('height', auto_height);

    /// ------------------------------ Shot Chart ------------------------------    
    svg.append('g')
        .attr('class', 'chart')
        .attr('id', 'shot_chart')
        .attr('transform', 'translate(0, 0)');

    // For chart 1, we will draw year vs. shot percentage
    var shot_data = d3.flatGroup(shots_contested, d => d.SEASON)
        .map(d => ({
            // parse the year from the season string into a number
            SEASON: d[0],
            SHOT_PCT: d3.sum(d[1], e => e.MADE_3PT) / d3.sum(d[1], e => e.ATTEMPTED_3PT),
            CONTEST_PCT: d3.sum(d[1], e => e.CONTESTED_3PT) / d3.sum(d[1], e => e.ATTEMPTED_3PT)
        }));

   const x = d3.scaleBand()
        .domain(shot_data.map(d => d.SEASON))
        .range([0, shot_width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(shot_data, d => d.SHOT_PCT)])
        .nice()
        .range([shot_height, 0]);

    // Create the line
    const pct_line = d3.line()
        .x(d => x(d.SEASON) + x.bandwidth() / 2)
        .y(d => y(d.SHOT_PCT));

    // For the secondary line, we will draw year vs. contested shot percentage
    const yScale2 = d3.scaleLinear()
        .domain([0, d3.max(shot_data, d => d.CONTEST_PCT)])
        .nice()
        .range([shot_height, 0]);

    // Create the line
    const contested_line = d3.line()
        .x(d => x(d.SEASON) + x.bandwidth() / 2)
        .y(d => yScale2(d.CONTEST_PCT));

    const shot_chart = svg.select("#shot_chart");

    const pct_path = shot_chart.append("path")
        .datum(shot_data)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", pct_line);

    const contest_path = shot_chart.append("path")
        .datum(shot_data)
        .attr("fill", "none")
        .attr("stroke", "orange")
        .attr("stroke-width", 1.5)
        .attr("d", contested_line);

    // Add circles at data points
    const shot_dots = shot_chart.selectAll("circle")
        .data(shot_data)
        .enter().append("circle")
        .attr("cx", d => x(d.SEASON) + x.bandwidth() / 2)
        .attr("cy", d => y(d.SHOT_PCT))
        .attr("r", 4)
        .attr("fill", "steelblue");

    const contest_dots = shot_chart.selectAll("circle2")
        .data(shot_data)
        .enter().append("circle")
        .attr("cx", d => x(d.SEASON) + x.bandwidth() / 2)
        .attr("cy", d => yScale2(d.CONTEST_PCT))
        .attr("r", 4)
        .attr("fill", "orange");

    shot_chart.append("g")
        .attr("transform", `translate(0,${shot_height})`)
        .call(d3.axisBottom(x).tickSizeOuter(0))
        .attr("font-size", "10px")
        // rotate the x-axis labels
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .attr("text-anchor", "end")
        .attr("dx", "-0.5em")
        .attr("dy", "0.5em");

    shot_chart.append("g")
        .call(d3.axisLeft(y).tickSizeOuter(0))
        .selectAll("path, line")
        .attr("stroke", "black")
        .attr("shape-rendering", "crispEdges");

    shot_dots
        .append('title')
        .text(d => `Year: ${d.SEASON}\nShot Percentage: ${(d.SHOT_PCT * 100).toFixed(2)}%`);

    shot_dots
        .on("mouseover", function(event, d) {
            d3.select(this).attr('stroke', '#333').attr('stroke-width', 2);
        })
        .on("mouseout", function(d) {
            d3.select(this).attr('stroke', null);
        });

    contest_dots
        .append('title')
        .text(d => `Year: ${d.SEASON}\nShot Percentage: ${(d.CONTEST_PCT * 100).toFixed(2)}%`);

    contest_dots
        .on("mouseover", function(event, d) {
            d3.select(this).attr('stroke', '#333').attr('stroke-width', 2);
        })
        .on("mouseout", function(d) {
            d3.select(this).attr('stroke', null);
        });

    /// --------------------------- Efficiency Chart ---------------------------

    svg.append('g')
        .attr('class', 'chart')
        .attr('id', 'efficiency_chart')
        .attr('transform', `translate(0,${shot_height})`);

    // This is the scatter plot of shot efficiency vs. contest intensity
    const efficiency_data = shots_contested.map(d => ({
            // parse the year from the season string into a number
            X_ID: d.X_ID,
            SEASON: d.SEASON,
            SHOT_PCT: d.MADE_3PT / d.ATTEMPTED_3PT,
            CONTEST_PCT: d.CONTESTED_3PT / d.ATTEMPTED_3PT
        }));

    display(efficiency_data)

    const x_eff = d3.scaleLinear()
        .domain([0, d3.max(efficiency_data, d => d.SHOT_PCT)])
        .nice()
        .range([0, shot_width]);

    const y_eff = d3.scaleLinear()
        .domain([0, d3.max(efficiency_data, d => d.CONTEST_PCT)])
        .nice()
        .range([shot_height, 0]);

    const efficiency_chart = svg.select("#efficiency_chart");
    efficiency_chart.append("g")
        .attr("transform", `translate(0,${shot_height})`)
        .call(d3.axisBottom(x_eff).ticks(5))
        .attr("font-size", "10px");

    efficiency_chart.append("g")
        .call(d3.axisLeft(y_eff).ticks(5))
        .attr("font-size", "10px");

    efficiency_chart.selectAll("circle")
        .data(efficiency_data)
        .enter().append("circle")
        .attr("cx", d => x_eff(d.SHOT_PCT))
        .attr("cy", d => y_eff(d.CONTEST_PCT))
        .attr("r", 4)
        .attr("fill", "steelblue");

    efficiency_chart.selectAll("circle")
        .append('title')
        .text(d => `ID ${// look up the id in the original data
            d.X_ID
            // players.find(e => e.X_ID === d.X_ID).id
        }\n
        Year: ${d.SEASON}\nShot Percentage: ${(d.SHOT_PCT * 100).toFixed(2)}%\nContest Percentage: ${(d.CONTEST_PCT * 100).toFixed(2)}%`);

    efficiency_chart.selectAll("circle")
        .on("mouseover", function(event, d) {
            d3.select(this).attr('stroke', '#333').attr('stroke-width', 2);
        })
        .on("mouseout", function(d) {
            d3.select(this).attr('stroke', null);
        });

    /// ----------------------------- Court Chart ------------------------------

    svg.append('g')
        .attr('class', 'chart')
        .attr('id', 'court_chart')
        .attr('transform', `translate(${shot_width},0)`);

    // Draw NBA half-court in the larger chart
    const court = svg.select("#court_chart")
        .style('fill', 'none')
        .style('stroke', '#000');
    const usableWidth = Math.min(500, court_width)
    const margins = 20
    const height = usableWidth / 50 * 47

    const x_nba = d3.scaleLinear().range([0, usableWidth - margins * 2]).domain([-25,25])
    const y_nba = d3.scaleLinear().range([0, height - margins * 2]).domain([0, 47])

    const arc = (radius, start, end) => {
        const points = [...Array(30)].map((d,i) => i);

        const angle = d3.scaleLinear()
            .domain([ 0, points.length - 1 ])
            .range([ start, end ]);

        const line = d3.lineRadial()
            .radius(radius)
            .angle((d,i) => angle(i));

        return line(points);
    }

    const threeAngle = Math.atan( (10 - 0.75) / 22 ) * 180 / Math.PI
    const basket = y_nba(4)
    const basketRadius = y_nba(4.75) - basket
    const pi = Math.PI / 180

    // basket
    court.append('circle')
        .attr('r', basketRadius)
        .attr('cx', x_nba(0))
        .attr('cy', y_nba(4.75))
    
    // backboard
    court.append('rect')
        .attr('x', x_nba(-3))
        .attr('y', basket)
        .attr('width', x_nba(3) - x_nba(-3))
        .attr('height', 1)
    
    // outer paint
    court.append('rect')
        .attr('x', x_nba(-8))
        .attr('y', y_nba(0))
        .attr('width', x_nba(8) - x_nba(-8))
        .attr('height', y_nba(15) + basket)
    
    // inner paint
    court.append('rect')
        .attr('x', x_nba(-6))
        .attr('y', y_nba(0))
        .attr('width', x_nba(6) - x_nba(-6))
        .attr('height', y_nba(15) + basket)

    // restricted area
    court.append('path')
        .attr('d', arc(x_nba(4) - x_nba(0), 90 * pi, 270 * pi))
        .attr('transform', `translate(${[x_nba(0), basket]})`)

    // freethrow
    court.append('path')
        .attr('d', arc(x_nba(6) - x_nba(0), 90 * pi, 270 * pi))
        .attr('transform', `translate(${[x_nba(0), y_nba(15) + basket]})`)
    
    // freethrow dotted
    court.append('path')
        .attr('d', arc(x_nba(6) - x_nba(0), -90 * pi, 90 * pi))
        .attr('stroke-dasharray', '3,3')
        .attr('transform', `translate(${[x_nba(0), y_nba(15) + basket]})`)
    
    // 3-point lines
    court.append('line')
        .attr('x1', x_nba(-21.775)) // lines up the stroke a little better than the true 22 ft.
        .attr('x2', x_nba(-21.775))
        .attr('y2', y_nba(14))
    
    court.append('line')
        .attr('x1', x_nba(21.775))
        .attr('x2', x_nba(21.775))
        .attr('y2', y_nba(14))
    
    // 3-point arc
    court.append('path')
        .attr('d', arc(y_nba(23.75), (threeAngle + 90) * pi, (270 - threeAngle) * pi))
        .attr('transform', `translate(${[x_nba(0), basket + basketRadius]})`)

    // half court outer
    court.append('path')
        .attr('d', arc(x_nba(6) - x_nba(0), -90 * pi, 90 * pi))
        .attr('transform', `translate(${[x_nba(0), y_nba(47)]})`)
    
    // half court inner
    court.append('path')
        .attr('d', arc(x_nba(2) - x_nba(0), -90 * pi, 90 * pi))
        .attr('transform', `translate(${[x_nba(0), y_nba(47)]})`)
    
    // half court line
    court.append('line')
        .attr('x1', x_nba(-25))
        .attr('x2', x_nba(25))
        .attr('y1', y_nba(47))
        .attr('y2', y_nba(47))
    
    // boundaries
    court.append('rect')
        .style('stroke', '#ddd')
        .attr('x', x_nba(-25))
        .attr('y', y_nba(0))
        .attr('width', x_nba(25))
        .attr('height', y_nba(47))

    // Then using the court chart, we will draw the shot heatmap
    const x_nba_data = d3.scaleLinear().range([0, usableWidth - margins * 2]).domain([-250,250])
    const y_nba_data = d3.scaleLinear().range([0, (height - margins * 2) * 2]).domain([-52, 888])
    const court_chart = svg.select("#court_chart");
    const hexbin = d3Hexbin()
        .x(d => x_nba_data(d.LOC_X))
        .y(d => y_nba_data(d.LOC_Y))
        .extent([[0, 0], [usableWidth - margins * 2, (height - margins * 2) * 2]])
        .radius(4);

    // loc_x needs to converted to numbers
    const bins = hexbin(shots_loc
        .filter(d => d.LOC_Y < 418) // Filter the data to only include shots taken in the front court
        .map(d => ({
            LOC_X: +d.LOC_X,
            LOC_Y: +d.LOC_Y,
            MADE: d.SHOT_MADE_FLAG,
            ATTEMPTED: d.SHOT_ATTEMPTED_FLAG
        })));

    bins.forEach(d => {
        d.total_made = d3.sum(d, e => e.MADE);
        d.pct = d3.sum(d, e => e.MADE) / d.length;
    });

    // try to find the max/min value of d3.sum(d, e => e.MADE) / d.length
    const max_pct = d3.max(bins, d => d.pct);
    const min_pct = d3.min(bins, d => d.pct);

    const q25 = d3.quantile(bins.map(d => d.pct), 0.3);
    const q75 = d3.quantile(bins.map(d => d.pct), 0.5);
    const color = d3.scaleSequential(d3.interpolateRdYlBu)
        .domain([min_pct, max_pct])

    const legendScale = d3.scaleLinear()
        .domain([min_pct, max_pct])
        .range([0, 200]);

    const legend = svg.append("g")
        .attr("transform", `translate(${shot_width + court_width},${search_height})`);

    legend.selectAll("rect")
        .data(d3.range(min_pct, max_pct, (max_pct - min_pct) / 20))
        .enter().append("rect")
        .attr("x", d => legendScale(d))
        .attr("width", 10)
        .attr("height", 20)
        .style("fill", d => color(d));

    const hexagons = court_chart.append("g")
        .selectAll("path")
        .data(bins)
        .enter().append("path")
        .attr("class", "hexagon")
        .attr("d", hexbin.hexagon())
        .attr("transform", d => `translate(${d.x},${d.y})`)
        .attr("fill", d => color(d.pct))
        .attr("stroke", "white")
        .attr("opacity", 0.6)
        .on("mouseover", function(event, d) {
            d3.select(this).attr('stroke', '#333');
        })
        .on("mouseout", function(d) {
            d3.select(this).attr('stroke', 'white');
        });

    hexagons
        .append('title')
        .text(d => `Shot Percentage: ${(d.total_made / d.length * 100).toFixed(2)}%\nAttempts: ${d.length}`);


    /// ----------------------------- Update Chart -----------------------------
    function update_shot_chart(team) {
        display(team)
        const data = d3.flatGroup(team, d => d.SEASON)
            .map(d => ({
                // parse the year from the season string into a number
                SEASON: d[0],
                SHOT_PCT: d3.sum(d[1], e => e.MADE_3PT) / d3.sum(d[1], e => e.ATTEMPTED_3PT),
                CONTEST_PCT: d3.sum(d[1], e => e.CONTESTED_3PT) / d3.sum(d[1], e => e.ATTEMPTED_3PT)
            }));

        const shot_chart = svg.select("#shot_chart");

        const x_team = d3.scaleBand()
            .domain(data.map(d => d.SEASON))
            .range([0, shot_width])
            .padding(0.1);

        const y_team = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.SHOT_PCT)])
            .nice()
            .range([shot_height, 0]);

        // Create the line
        const new_pct_line = d3.line()
            .x(d => x_team(d.SEASON) + x.bandwidth() / 2)
            .y(d => y_team(d.SHOT_PCT));

        const y_contested = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.CONTEST_PCT)])
            .nice()
            .range([shot_height, 0]);

        // Create the line
        const new_contested_line = d3.line()
            .x(d => x_team(d.SEASON) + x.bandwidth() / 2)
            .y(d => y_contested(d.CONTEST_PCT));

        pct_path
            .datum(data)
            .transition()
            .duration(1000)
            .attr("d", new_pct_line);

        // Update circles at data points
        shot_dots
            .data(data)
            .transition()
            .duration(1000)
            .attr("cx", d => x_team(d.SEASON) + x.bandwidth() / 2)
            .attr("cy", d => y_team(d.SHOT_PCT))
            .attr("r", 4)
            .attr("fill", "steelblue");

        // Update the contested line
        contest_path
            .datum(data)
            .transition()
            .duration(1000)
            .attr("d", new_contested_line);

        // Update circles at data points
        contest_dots
            .data(data)
            .transition()
            .duration(1000)
            .attr("cx", d => x(d.SEASON) + x.bandwidth() / 2)
            .attr("cy", d => y_contested(d.CONTEST_PCT))
            .attr("r", 4)
            .attr("fill", "orange");

        // Update the y-axis
        shot_chart.select("g")
            .transition()
            .duration(1000)
            .call(d3.axisLeft(y).tickSizeOuter(0))
            .selectAll("path, line")
            .attr("stroke", "black")
            .attr("shape-rendering", "crispEdges");

        // Update the x-axis
        shot_chart.select("g")
            .transition()
            .duration(1000)
            .call(d3.axisBottom(x).tickSizeOuter(0))
            .attr("font-size", "10px")
            // rotate the x-axis labels
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .attr("text-anchor", "end")
            .attr("dx", "-0.5em")
            .attr("dy", "0.5em");
    }

    function update_chart(year_start, year_end, data) {
        shots_contested
            .filter(d => d.SEASON >= year_start && d.SEASON <= year_end)
            .map(d => ({
                // parse the year from the season string into a number
                X_ID: d.X_ID,
                SEASON: d.SEASON,
                SHOT_PCT: d.MADE_3PT / d.ATTEMPTED_3PT,
                CONTEST_PCT: d.CONTESTED_3PT / d.ATTEMPTED_3PT
            }));
        // const x = d3.scaleBand()
        //     .domain(data.map(d => d.SEASON))
        //     .range([0, shot_width])
        //     .padding(0.1);

        // const y = d3.scaleLinear()
        //     .domain([0, d3.max(data, d => d.SHOT_PCT)])
        //     .nice()
        //     .range([shot_height, 0]);

        // // Create the line
        // const line = d3.line()
        //     .x(d => x(d.SEASON) + x.bandwidth() / 2)
        //     .y(d => y(d.SHOT_PCT));

        // const shot_chart = svg.select("#shot_chart");

        // shot_chart.select("path")
        //     .datum(data)
        //     .transition()
        //     .duration(1000)
        //     .attr("d", line);

        // // Update circles at data points
        // shot_chart.selectAll("circle")
        //     .data(data)
        //     .transition()
        //     .duration(1000)
        //     .attr("cx", d => x(d.SEASON) + x.bandwidth() / 2)
        //     .attr("cy", d => y(d.SHOT_PCT))
        //     .attr("r", 4)
        //     .attr("fill", "steelblue");
    }

    function update(team_or_player) {
        // first we determine if this is a team or player
        const is_team = teams.some(d => d.id === team_or_player);
        const is_player = players.some(d => d.id === team_or_player);

        var url = ''
        var contested_data = []

        // This will just be a image downloaded from nba.com
        if (is_player) {
            // If this is a player, it goes like https://cdn.nba.com/headshots/nba/latest/1040x760/${player_id}.png
            url = `https://cdn.nba.com/headshots/nba/latest/1040x760/${team_or_player}.png`;
            contested_data = shots_contested.filter(d => d.X_ID === parseInt(team_or_player));
        } else if (is_team) {
            // If this is a team, it goes like https://cdn.nba.com/logos/nba/${team_id}/primary/L/logo.svg
            url = `https://cdn.nba.com/logos/nba/${team_or_player}/primary/L/logo.svg`;
            contested_data = shots_contested.filter(d => d.X_ID === parseInt(team_or_player));
        } else {
            // if it is neither, we will roll back to the whole league
            url = 'https://cdn.nba.com/logos/leagues/logo-nba.svg';
            contested_data = shots_contested;
        }

        svg.select("#auto_chart")
        .selectAll('image')
        .attr('xlink:href', url);

        update_shot_chart(contested_data);

        // Then update the other charts
        // update_chart(year, year, efficiency_data);
    }

    return Object.assign(svg.node(), { update });
})());
```
