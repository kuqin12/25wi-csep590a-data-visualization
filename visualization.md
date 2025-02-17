---
title: Interactive Visualization Submission
toc: false
---

# Interactive Visualization Submission

```js echo
async function loadData() {
	const BASE_URL =
		"https://media.githubusercontent.com/media/kuqin12/25wi-csep590a-data-visualization/refs/heads/main/";

	const players = (await d3.csv(BASE_URL + "all_players.csv")).sort((a, b) =>
		a.last_name.localeCompare(b.last_name)
	);
	const teams = (await d3.csv(BASE_URL + "all_teams.csv")).sort((a, b) =>
		a.full_name.localeCompare(b.full_name)
	);

	const shots_contested = await d3.csv(
		BASE_URL + "x_shot_summary_2014_2024_contested.csv",
		d3.autoType
	);
	const shots_loc = await d3.csv(
		BASE_URL + "x_shot_summary_2014_2024_loc.csv",
		d3.autoType
	);

	return { players, teams, shots_contested, shots_loc };
}

loadData().then((data) => {
	console.log("Data Loaded:", data);
	window.data = data;
	init();
});
```

```js echo
const VIEW_WIDTH = 1500;
const VIEW_HEIGHT = 700;
const MARGIN = { top: 50, right: 50, bottom: 80, left: 80 };
const DEFAULT_CHART_WIDTH = VIEW_WIDTH * 0.3 - MARGIN.left - MARGIN.right;
const DEFAULT_CHART_HEIGHT = VIEW_HEIGHT / 2 - MARGIN.top - MARGIN.bottom;
const COURT_WIDTH = VIEW_WIDTH * 0.4;
const SEARCH_WIDTH = VIEW_WIDTH * 0.3;
const SEARCH_HEIGHT = 200;
const AUTO_WIDTH = 100;
const AUTO_HEIGHT = 100;
const USABLE_WIDTH = Math.min(500, COURT_WIDTH);
const COURT_MARGINS = 20;
const COURT_HEIGHT = (USABLE_WIDTH / 50) * 47;
```

```js echo
import { hexbin as d3Hexbin } from "d3-hexbin";

document.addEventListener("DOMContentLoaded", init);

function init() {
	const svg = d3
		.create("svg")
		.attr("viewBox", [0, 0, VIEW_WIDTH, VIEW_HEIGHT])
		.style("font-family", '"Open Sans", sans-serif');

	drawSelector(svg);
	drawShotChart(svg, window.data.shots_contested);
	drawEfficiencyChart(svg, window.data.shots_contested);
	drawShotHeatmap(svg, window.data.shots_loc);
	renderLogo(svg);

	display(svg.node());
}

function drawSelector(svg) {
	const selectorGroup = svg
		.append("g")
		.attr(
			"transform",
			`translate(${DEFAULT_CHART_WIDTH + COURT_WIDTH}, ${MARGIN.top})`
		);
	const foreignObject = selectorGroup
		.append("foreignObject")
		.attr("width", SEARCH_WIDTH)
		.attr("height", SEARCH_HEIGHT);
	const body = foreignObject
		.append("xhtml:body")
		.style("margin", "5px")
		.style("padding", "5px");

	const input = body
		.append("input")
		.attr("type", "text")
		.attr("id", "autocomplete-input")
		.attr("style", "width: 90%; height: 100%;")
		.attr("placeholder", "Search for a team or player")
		.on("input", debounce(handleSearchInput, 300));

	function handleSearchInput() {
		const value = input.property("value").toLowerCase();
		const suggestions = window.data.teams
			.concat(window.data.players)
			.filter((d) => d.full_name.toLowerCase().includes(value));
		showSuggestions(suggestions);
	}

	function showSuggestions(suggestions) {
		d3.select("#suggestions").remove();
		const suggestionsContainer = body
			.append("div")
			.attr("id", "suggestions")
			.attr(
				"style",
				"position: absolute; width: 90%; max-height: 150px; overflow-y: auto; background: white; border: 1px solid #ccc;"
			);
		suggestions.forEach((suggestion) => {
			suggestionsContainer
				.append("div")
				.attr("style", "padding: 5px; cursor: pointer;")
				.text(suggestion.full_name)
				.on("click", () => {
					input.property("value", suggestion.full_name);
					d3.select("#suggestions").remove();
					// updateCharts(suggestion.id);
				});
		});
	}
}

function drawShotChart(svg, shotData) {
	const shotChart = svg
		.append("g")
		.attr("id", "shot_chart")
		.attr("transform", `translate(${MARGIN.left}, ${MARGIN.top})`);
	const processedData = processShotData(shotData);
	const xScale = d3
		.scaleBand()
		.domain(processedData.map((d) => d.SEASON))
		.range([0, DEFAULT_CHART_WIDTH])
		.padding(0.1);

	const yScale = d3
		.scaleLinear()
		.domain([0, 0.8])
		.nice()
		.range([DEFAULT_CHART_HEIGHT, 0]);

	drawShotLines(shotChart, processedData, xScale, yScale);
	drawShotDots(
		shotChart,
		processedData,
		xScale,
		yScale,
		"steelblue",
		"Shot Percentage"
	);
	drawShotDots(
		shotChart,
		processedData,
		xScale,
		yScale,
		"orange",
		"Contested Percentage",
		true
	);
	drawAxesAndLabels(
		shotChart,
		"Shot Percentage and Contested Percentage Over Seasons",
		xScale,
		yScale,
		"Seasons",
		"Percentages"
	);
	drawLegend(shotChart, ["steelblue", "orange"], ["Shot %", "Contested %"]);

	function processShotData(data) {
		return d3
			.flatGroup(data, (d) => d.SEASON)
			.map((d) => ({
				SEASON: d[0],
				SHOT_PCT:
					d3.sum(d[1], (e) => e.MADE_3PT) /
					d3.sum(d[1], (e) => e.ATTEMPTED_3PT),
				CONTEST_PCT:
					d3.sum(d[1], (e) => e.CONTESTED_3PT) /
					d3.sum(d[1], (e) => e.ATTEMPTED_3PT),
			}));
	}

	function drawShotLines(chart, data, xScale, yScale) {
		chart
			.append("path")
			.datum(data)
			.attr("fill", "none")
			.attr("stroke", "steelblue")
			.attr(
				"d",
				d3
					.line()
					.x((d) => xScale(d.SEASON) + xScale.bandwidth() / 2)
					.y((d) => yScale(d.SHOT_PCT))
			);
		chart
			.append("path")
			.datum(data)
			.attr("fill", "none")
			.attr("stroke", "orange")
			.attr(
				"d",
				d3
					.line()
					.x((d) => xScale(d.SEASON) + xScale.bandwidth() / 2)
					.y((d) => yScale(d.CONTEST_PCT))
			);
	}
}

function drawShotDots(
	chart,
	data,
	xScale,
	yScale,
	color,
	tooltipText,
	isContested = false
) {
	const dots = chart
		.selectAll(`circle.${isContested ? "contested" : "shot"}`)
		.data(data)
		.enter()
		.append("circle")
		.attr("class", isContested ? "contested" : "shot")
		.attr("cx", (d) => xScale(d.SEASON) + xScale.bandwidth() / 2)
		.attr("cy", (d) => yScale(d[isContested ? "CONTEST_PCT" : "SHOT_PCT"]))
		.attr("r", 4)
		.attr("fill", color)
		.on("mouseover", function (event, d) {
			d3.select(this).attr("stroke", "#333").attr("stroke-width", 2);
		})
		.on("mouseout", function () {
			d3.select(this).attr("stroke", null);
		});

	dots
		.append("title")
		.text(
			(d) =>
				`Year: ${d.SEASON}\n${tooltipText}: ${(
					d[isContested ? "CONTEST_PCT" : "SHOT_PCT"] * 100
				).toFixed(2)}%`
		);
}

function drawShotHeatmap(svg, shotsLocData) {
	const heatmap = svg
		.append("g")
		.attr("id", "court_chart")
		.attr(
			"transform",
			`translate(${
				DEFAULT_CHART_WIDTH + MARGIN.left + MARGIN.left + MARGIN.left
			}, ${DEFAULT_CHART_HEIGHT})`
		);

	drawCourtOutline(heatmap);
	drawHeatmap(heatmap, shotsLocData);
}

function drawEfficiencyChart(svg, efficiencyData) {
	const efficiencyChart = svg
		.append("g")
		.attr("id", "efficiency_chart")
		.attr(
			"transform",
			`translate(${MARGIN.left}, ${
				DEFAULT_CHART_HEIGHT + MARGIN.top + MARGIN.top + MARGIN.top
			})`
		);

	const processedData = efficiencyData.map((d) => ({
		X_ID: d.X_ID,
		SEASON: d.SEASON,
		SHOT_PCT: d.MADE_3PT / d.ATTEMPTED_3PT,
		CONTEST_PCT: d.CONTESTED_3PT / d.ATTEMPTED_3PT,
	}));

	const xScale = d3
		.scaleLinear()
		.domain([0, d3.max(processedData, (d) => d.SHOT_PCT)])
		.nice()
		.range([0, DEFAULT_CHART_WIDTH]);

	const yScale = d3
		.scaleLinear()
		.domain([0, d3.max(processedData, (d) => d.CONTEST_PCT)])
		.nice()
		.range([DEFAULT_CHART_HEIGHT, 0]);

	efficiencyChart
		.selectAll("circle")
		.data(processedData)
		.enter()
		.append("circle")
		.attr("cx", (d) => xScale(d.SHOT_PCT))
		.attr("cy", (d) => yScale(d.CONTEST_PCT))
		.attr("r", 4)
		.attr("fill", "steelblue")
		.on("mouseover", function (event, d) {
			d3.select(this).attr("stroke", "#333").attr("stroke-width", 2);
		})
		.on("mouseout", function (d) {
			d3.select(this).attr("stroke", null);
		})
		.append("title")
		.text(
			(d) =>
				`ID: ${d.X_ID}\nYear: ${d.SEASON}\nShot Percentage: ${(
					d.SHOT_PCT * 100
				).toFixed(2)}%\nContest Percentage: ${(d.CONTEST_PCT * 100).toFixed(
					2
				)}%`
		);

	drawAxesAndLabels(
		efficiencyChart,
		"Shot Efficiency vs Contest Percentage",
		xScale,
		yScale,
		"Shot Efficiency",
		"Contest Percentage"
	);
}

function drawHeatmap(court, shotsLocData) {
	const X_NBA_DATA = d3
		.scaleLinear()
		.range([0, USABLE_WIDTH - COURT_MARGINS * 2])
		.domain([-250, 250]);
	const Y_NBA_DATA = d3
		.scaleLinear()
		.range([0, (COURT_HEIGHT - COURT_MARGINS * 2) * 2])
		.domain([-52, 888]);
	const COURT_EXTENT = [
		[0, 0],
		[USABLE_WIDTH - COURT_MARGINS * 2, (COURT_HEIGHT - COURT_MARGINS * 2) * 2],
	];

	const hexbin = d3Hexbin()
		.x((d) => X_NBA_DATA(d.LOC_X))
		.y((d) => Y_NBA_DATA(d.LOC_Y))
		.extent(COURT_EXTENT)
		.radius(4);
	const bins = hexbin(
		shotsLocData
			.filter((d) => d.LOC_Y < 418)
			.map((d) => ({
				LOC_X: +d.LOC_X,
				LOC_Y: +d.LOC_Y,
				MADE: d.SHOT_MADE_FLAG,
				ATTEMPTED: d.SHOT_ATTEMPTED_FLAG,
			}))
	);

	bins.forEach((d) => {
		d.total_made = d3.sum(d, (e) => e.MADE);
		d.pct = d.total_made / d.length;
	});

	const maxPct = d3.max(bins, (d) => d.pct);
	const minPct = d3.min(bins, (d) => d.pct);
	const colorScale = d3
		.scaleSequential(d3.interpolateRdYlBu)
		.domain([minPct, maxPct]);

	const hexagons = court
		.append("g")
		.selectAll("path")
		.data(bins)
		.enter()
		.append("path")
		.attr("class", "hexagon")
		.attr("d", hexbin.hexagon())
		.attr("transform", (d) => `translate(${d.x},${d.y})`)
		.attr("fill", (d) => colorScale(d.pct))
		.attr("stroke", "white")
		.attr("opacity", 0.7)
		.on("mouseover", function (event, d) {
			d3.select(this).attr("stroke", "#333");
		})
		.on("mouseout", function (d) {
			d3.select(this).attr("stroke", "white");
		});

	hexagons
		.append("title")
		.text(
			(d) =>
				`Shot Percentage: ${(d.pct * 100).toFixed(2)}%\nAttempts: ${d.length}`
		);

	drawHeatmapLegend(court, colorScale, minPct, maxPct);
}

function drawHeatmapLegend(svg, colorScale, minPct, maxPct) {
	const LEGEND_WIDTH = 200;
	const LEGEND_HEIGHT = 20;

	const legendScale = d3
		.scaleLinear()
		.domain([minPct, maxPct])
		.range([0, LEGEND_WIDTH]);

	const legend = svg
		.append("g")
		.attr(
			"transform",
			`translate(${
				DEFAULT_CHART_WIDTH + MARGIN.left + MARGIN.left
			}, ${SEARCH_HEIGHT})`
		);

	legend
		.selectAll("rect")
		.data(d3.range(minPct, maxPct, (maxPct - minPct) / 20))
		.enter()
		.append("rect")
		.attr("x", (d) => legendScale(d))
		.attr("width", 10)
		.attr("height", LEGEND_HEIGHT)
		.style("fill", (d) => colorScale(d));

	legend
		.append("text")
		.attr("x", 0)
		.attr("y", LEGEND_HEIGHT + 15)
		.attr("text-anchor", "start")
		.text(`${(minPct * 100).toFixed(1)}%`);

	legend
		.append("text")
		.attr("x", LEGEND_WIDTH)
		.attr("y", LEGEND_HEIGHT + 15)
		.attr("text-anchor", "end")
		.text(`${(maxPct * 100).toFixed(1)}%`);
}

function renderLogo(svg) {
	svg
		.append("g")
		.attr("class", "chart")
		.attr("id", "auto_chart")
		.attr(
			"transform",
			`translate(${(VIEW_WIDTH - MARGIN.left - MARGIN.right) / 2}, 0)`
		)
		.append("image")
		.attr(
			"xlink:href",
			"https://cdn.1min30.com/wp-content/uploads/2018/03/logo-NBA.jpg"
		)
		.attr("width", AUTO_WIDTH)
		.attr("height", AUTO_HEIGHT);
}

// General function to draw Court Outline
function drawCourtOutline(court) {
	court.style("fill", "none").style("stroke", "#000");

	const x_nba = d3
		.scaleLinear()
		.range([0, USABLE_WIDTH - COURT_MARGINS * 2])
		.domain([-25, 25]);
	const y_nba = d3
		.scaleLinear()
		.range([0, COURT_HEIGHT - COURT_MARGINS * 2])
		.domain([0, 47]);

	const arc = (radius, start, end) => {
		const points = [...Array(30)].map((d, i) => i);
		const angle = d3
			.scaleLinear()
			.domain([0, points.length - 1])
			.range([start, end]);
		return d3
			.lineRadial()
			.radius(radius)
			.angle((d, i) => angle(i))(points);
	};

	const threeAngle = (Math.atan((10 - 0.75) / 22) * 180) / Math.PI;
	const basket = y_nba(4);
	const basketRadius = y_nba(4.75) - basket;
	const pi = Math.PI / 180;

	const elements = [
		{
			type: "circle",
			attrs: [
				["r", basketRadius],
				["cx", x_nba(0)],
				["cy", y_nba(4.75)],
			],
		},
		{
			type: "rect",
			attrs: [
				["x", x_nba(-3)],
				["y", basket],
				["width", x_nba(3) - x_nba(-3)],
				["height", 1],
			],
		},
		{
			type: "rect",
			attrs: [
				["x", x_nba(-8)],
				["y", y_nba(0)],
				["width", x_nba(8) - x_nba(-8)],
				["height", y_nba(15) + basket],
			],
		},
		{
			type: "rect",
			attrs: [
				["x", x_nba(-6)],
				["y", y_nba(0)],
				["width", x_nba(6) - x_nba(-6)],
				["height", y_nba(15) + basket],
			],
		},
		{
			type: "path",
			attrs: [
				["d", arc(x_nba(4) - x_nba(0), 90 * pi, 270 * pi)],
				["transform", `translate(${[x_nba(0), basket]})`],
			],
		},
		{
			type: "path",
			attrs: [
				["d", arc(x_nba(6) - x_nba(0), 90 * pi, 270 * pi)],
				["transform", `translate(${[x_nba(0), y_nba(15) + basket]})`],
			],
		},
		{
			type: "path",
			attrs: [
				["d", arc(x_nba(6) - x_nba(0), -90 * pi, 90 * pi)],
				["transform", `translate(${[x_nba(0), y_nba(15) + basket]})`],
				["stroke-dasharray", "3,3"],
			],
		},
		{
			type: "line",
			attrs: [
				["x1", x_nba(-21.775)],
				["x2", x_nba(-21.775)],
				["y2", y_nba(14)],
			],
		},
		{
			type: "line",
			attrs: [
				["x1", x_nba(21.775)],
				["x2", x_nba(21.775)],
				["y2", y_nba(14)],
			],
		},
		{
			type: "path",
			attrs: [
				[
					"d",
					arc(y_nba(23.75), (threeAngle + 90) * pi, (270 - threeAngle) * pi),
				],
				["transform", `translate(${[x_nba(0), basket + basketRadius]})`],
			],
		},
		{
			type: "path",
			attrs: [
				["d", arc(x_nba(6) - x_nba(0), -90 * pi, 90 * pi)],
				["transform", `translate(${[x_nba(0), y_nba(47)]})`],
			],
		},
		{
			type: "path",
			attrs: [
				["d", arc(x_nba(2) - x_nba(0), -90 * pi, 90 * pi)],
				["transform", `translate(${[x_nba(0), y_nba(47)]})`],
			],
		},
		{
			type: "line",
			attrs: [
				["x1", x_nba(-25)],
				["x2", x_nba(25)],
				["y1", y_nba(47)],
				["y2", y_nba(47)],
			],
		},
		{
			type: "rect",
			attrs: [
				["x", x_nba(-25)],
				["y", y_nba(0)],
				["width", x_nba(25)],
				["height", y_nba(47)],
				["stroke", "#ddd"],
			],
		},
	];

	elements.forEach(({ type, attrs }) => {
		const elem = court.append(type);
		attrs.forEach(([attrName, attrValue]) => {
			elem.attr(attrName, attrValue);
		});
	});
}

/*--Utility Functions--*/

// General function to draw axes, labels, and title
function drawAxesAndLabels(chart, titleText, xScale, yScale, xLabel, yLabel) {
	chart
		.append("g")
		.attr("transform", `translate(0,${DEFAULT_CHART_HEIGHT})`)
		.call(d3.axisBottom(xScale).ticks(5));

	chart.append("g").call(d3.axisLeft(yScale).ticks(5));

	chart
		.append("text")
		.attr("x", DEFAULT_CHART_WIDTH / 2)
		.attr("y", -MARGIN.top / 2)
		.attr("text-anchor", "middle")
		.text(titleText);

	chart
		.append("text")
		.attr("x", DEFAULT_CHART_WIDTH / 2)
		.attr("y", DEFAULT_CHART_HEIGHT + MARGIN.bottom / 2)
		.attr("text-anchor", "middle")
		.text(xLabel);

	chart
		.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", -MARGIN.left / 1.5)
		.attr("x", -DEFAULT_CHART_HEIGHT / 2)
		.attr("text-anchor", "middle")
		.text(yLabel);
}

// General function to draw a legend
function drawLegend(chart, colors, labels) {
	const legend = chart
		.append("g")
		.attr("transform", `translate(${DEFAULT_CHART_WIDTH}, 0)`);
	colors.forEach((color, i) => {
		legend
			.append("rect")
			.attr("width", 10)
			.attr("height", 10)
			.attr("fill", color)
			.attr("y", i * 20);
		legend
			.append("text")
			.attr("x", 15)
			.attr("y", i * 20 + 10)
			.text(labels[i]);
	});
}

// Utility function to debounce input
function debounce(func, wait) {
	let timeout;
	return function (...args) {
		clearTimeout(timeout);
		timeout = setTimeout(() => func.apply(this, args), wait);
	};
}
```
