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
const AUTO_WIDTH = 150;
const AUTO_HEIGHT = 150;
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

	svg
		.append("text")
		.attr("x", VIEW_WIDTH / 2)
		.attr("y", MARGIN.top / 2)
		.attr("text-anchor", "middle")
		.attr("font-size", "24px")
		.attr("font-weight", "bold")
		.text("NBA Shot Insights: Trends, Efficiency & Court Hotspots");

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
			`translate(${VIEW_WIDTH - SEARCH_WIDTH - MARGIN.right}, ${
				MARGIN.top / 2
			})`
		);
	const foreignObject = selectorGroup
		.append("foreignObject")
		.attr("width", SEARCH_WIDTH)
		.attr("height", SEARCH_HEIGHT)
		.style("position", "relative");
	const body = foreignObject
		.append("xhtml:body")
		.style("margin", "5px")
		.style("padding", "5px");

	const input = body
		.append("input")
		.attr("type", "text")
		.attr("id", "autocomplete-input")
		.attr(
			"style",
			`
			width: 80%; 
            height: 30px;
            font-size: 14px;
            padding: 5px; 
            border: 1px solid #ccc;
            border-radius: 5px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
			`
		)
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
					updateCharts(suggestion.id);
				});
		});
	}
}

let shotXScale, shotYScale;

async function drawShotChart(svg, shotData) {
	const shotChart = await svg
		.append("g")
		.attr("id", "shot_chart")
		.attr("transform", `translate(${MARGIN.left}, ${MARGIN.top + MARGIN.top})`);
	const allData = processShotData(shotData);
	shotXScale = d3
		.scaleBand()
		.domain(allData.map((d) => d.SEASON))
		.range([0, DEFAULT_CHART_WIDTH])
		.padding(0.1);

	shotYScale = d3
		.scaleLinear()
		.domain([0, 1])
		.nice()
		.range([DEFAULT_CHART_HEIGHT, 0]);

	drawAxesAndLabels(
		shotChart,
		"Shooting Trends Over the Seasons",
		shotXScale,
		shotYScale,
		"Seasons",
		"Percentages"
	);
	drawLegend(shotChart, ["steelblue", "orange"], ["Shot %", "Contested %"]);
	updateShotChart(shotData);
}

function updateShotChart(filteredData) {
	const shotChart = d3.select("#shot_chart");

	const processedData = processShotData(filteredData);

	const shotLine = d3
		.line()
		.x((d) => shotXScale(d.SEASON) + shotXScale.bandwidth() / 2)
		.y((d) => shotYScale(d.SHOT_PCT));

	const contestLine = d3
		.line()
		.x((d) => shotXScale(d.SEASON) + shotXScale.bandwidth() / 2)
		.y((d) => shotYScale(d.CONTEST_PCT));

	shotChart
		.selectAll(".shot-line")
		.data([processedData])
		.join(
			(enter) =>
				enter
					.append("path")
					.attr("class", "shot-line")
					.attr("fill", "none")
					.attr("stroke", "steelblue")
					.attr("d", shotLine),

			(update) => update.transition().duration(750).attr("d", shotLine),

			(exit) => exit.remove()
		);

	shotChart
		.selectAll(".contest-line")
		.data([processedData])
		.join(
			(enter) =>
				enter
					.append("path")
					.attr("class", "contest-line")
					.attr("fill", "none")
					.attr("stroke", "orange")
					.attr("d", contestLine),

			(update) => update.transition().duration(750).attr("d", contestLine),

			(exit) => exit.remove()
		);

	const shotDots = shotChart
		.selectAll(".shot-dot")
		.data(processedData, (d) => d.SEASON)
		.join(
			(enter) =>
				enter
					.append("circle")
					.attr("class", "shot-dot")
					.attr("cx", (d) => shotXScale(d.SEASON) + shotXScale.bandwidth() / 2)
					.attr("cy", (d) => shotYScale(d.SHOT_PCT))
					.attr("r", 4)
					.attr("fill", "steelblue")
					.append("title")
					.text(
						(d) =>
							`Year: ${d.SEASON}\nShot Percentage: ${(d.SHOT_PCT * 100).toFixed(
								2
							)}%`
					),

			(update) =>
				update
					.transition()
					.duration(750)
					.attr("cx", (d) => shotXScale(d.SEASON) + shotXScale.bandwidth() / 2)
					.attr("cy", (d) => shotYScale(d.SHOT_PCT)),

			(exit) => exit.remove()
		);

	const contestDots = shotChart
		.selectAll(".contest-dot")
		.data(processedData, (d) => d.SEASON)
		.join(
			(enter) =>
				enter
					.append("circle")
					.attr("class", "contest-dot")
					.attr("cx", (d) => shotXScale(d.SEASON) + shotXScale.bandwidth() / 2)
					.attr("cy", (d) => shotYScale(d.CONTEST_PCT))
					.attr("r", 4)
					.attr("fill", "orange")
					.append("title")
					.text(
						(d) =>
							`Year: ${d.SEASON}\nContested Shot Percentage: ${(
								d.CONTEST_PCT * 100
							).toFixed(2)}%`
					),

			(update) =>
				update
					.transition()
					.duration(750)
					.attr("cx", (d) => shotXScale(d.SEASON) + shotXScale.bandwidth() / 2)
					.attr("cy", (d) => shotYScale(d.CONTEST_PCT)),

			(exit) => exit.remove()
		);
}

function processShotData(data) {
	return d3
		.flatGroup(data, (d) => d.SEASON)
		.map((d) => ({
			SEASON: d[0],
			SHOT_PCT:
				d3.sum(d[1], (e) => e.MADE_3PT) / d3.sum(d[1], (e) => e.ATTEMPTED_3PT),
			CONTEST_PCT:
				d3.sum(d[1], (e) => e.CONTESTED_3PT) /
				d3.sum(d[1], (e) => e.ATTEMPTED_3PT),
		}));
}

async function drawShotHeatmap(svg, shotsLocData) {
	const heatmap = await svg
		.append("g")
		.attr("id", "court_chart")
		.attr(
			"transform",
			`translate(${(VIEW_WIDTH - USABLE_WIDTH) / 2}, ${DEFAULT_CHART_HEIGHT})`
		);

	heatmap
		.append("text")
		.attr("x", USABLE_WIDTH / 2)
		.attr("y", -MARGIN.top / 2)
		.attr("text-anchor", "middle")
		.attr("font-size", "16px")
		.attr("font-weight", "bold")
		.attr("stroke", "none")
		.attr("fill", "black")
		.text("Shot Hotspots Across the Court");

	drawCourtOutline(heatmap);
	drawHeatmap(heatmap, shotsLocData);
}

let efficiencyXScale, efficiencyYScale;

async function drawEfficiencyChart(svg, efficiencyData) {
	const efficiencyChart = await svg
		.append("g")
		.attr("id", "efficiency_chart")
		.attr(
			"transform",
			`translate(${MARGIN.left}, ${
				DEFAULT_CHART_HEIGHT + MARGIN.top + MARGIN.top + MARGIN.top + MARGIN.top
			})`
		);

	const allData = efficiencyData.map((d) => ({
		X_ID: d.X_ID,
		SEASON: d.SEASON,
		SHOT_PCT: d.MADE_3PT / d.ATTEMPTED_3PT,
		CONTEST_PCT: d.CONTESTED_3PT / d.ATTEMPTED_3PT,
	}));

	efficiencyXScale = d3
		.scaleLinear()
		.domain([0, d3.max(allData, (d) => d.SHOT_PCT)])
		.nice()
		.range([0, DEFAULT_CHART_WIDTH]);

	efficiencyYScale = d3
		.scaleLinear()
		.domain([0, d3.max(allData, (d) => d.CONTEST_PCT)])
		.nice()
		.range([DEFAULT_CHART_HEIGHT, 0]);

	drawAxesAndLabels(
		efficiencyChart,
		"Shot Efficiency vs Defensive Pressure",
		efficiencyXScale,
		efficiencyYScale,
		"Shot Efficiency",
		"Contest Percentage"
	);

	updateEfficiencyChart(efficiencyData);
}

function updateEfficiencyChart(filteredData) {
	const efficiencyChart = d3.select("#efficiency_chart");

	const processedData = filteredData.map((d) => ({
		X_ID: d.X_ID,
		SEASON: d.SEASON,
		SHOT_PCT: d.MADE_3PT / d.ATTEMPTED_3PT,
		CONTEST_PCT: d.CONTESTED_3PT / d.ATTEMPTED_3PT,
	}));

	const dots = efficiencyChart
		.selectAll(".efficiency-dot")
		.data(processedData, (d) => d.X_ID)
		.join(
			(enter) =>
				enter
					.append("circle")
					.attr("class", "efficiency-dot")
					.attr("cx", (d) => efficiencyXScale(d.SHOT_PCT))
					.attr("cy", (d) => efficiencyYScale(d.CONTEST_PCT))
					.attr("r", 4)
					.attr("fill", "steelblue"),

			(update) =>
				update
					.transition()
					.duration(750)
					.attr("cx", (d) => efficiencyXScale(d.SHOT_PCT))
					.attr("cy", (d) => efficiencyYScale(d.CONTEST_PCT)),

			(exit) => exit.transition().duration(750).attr("r", 0).remove()
		);

	dots
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
				`ID: ${d.X_ID}\nYear: ${d.SEASON}\nShot Percentage: ${(
					d.SHOT_PCT * 100
				).toFixed(2)}%\nContest Percentage: ${(d.CONTEST_PCT * 100).toFixed(
					2
				)}%`
		);
}
let heatmapXScale, heatmapYScale;

function drawHeatmap(court, shotsLocData) {
	heatmapXScale = d3
		.scaleLinear()
		.range([0, USABLE_WIDTH - COURT_MARGINS * 2])
		.domain([-250, 250]);
	heatmapYScale = d3
		.scaleLinear()
		.range([0, (COURT_HEIGHT - COURT_MARGINS * 2) * 2])
		.domain([-52, 888]);
	const COURT_EXTENT = [
		[0, 0],
		[USABLE_WIDTH - COURT_MARGINS * 2, (COURT_HEIGHT - COURT_MARGINS * 2) * 2],
	];

	const hexbin = d3Hexbin()
		.x((d) => heatmapXScale(d.LOC_X))
		.y((d) => heatmapYScale(d.LOC_Y))
		.extent(COURT_EXTENT)
		.radius(4);
	window.hexbinGenerator = hexbin;

	updateHeatmap(shotsLocData);
}

function updateHeatmap(filteredData) {
	const court = d3.select("#court_chart");

	const bins = window.hexbinGenerator(
		filteredData
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

	const maxPct = d3.max(bins, (d) => d.pct) || 1;
	const minPct = d3.min(bins, (d) => d.pct) || 0;
	const colorScale = d3
		.scaleSequential(d3.interpolateRdYlBu)
		.domain([minPct, maxPct]);

	const hexagons = court
		.selectAll(".hexagon")
		.data(bins, (d) => `${d.x}-${d.y}`);

	hexagons
		.enter()
		.append("path")
		.attr("class", "hexagon")
		.attr("d", window.hexbinGenerator.hexagon())
		.attr("transform", (d) => `translate(${d.x},${d.y})`)
		.attr("fill", (d) => colorScale(d.pct))
		.attr("stroke", "white")
		.attr("opacity", 0)
		.transition()
		.duration(500)
		.attr("opacity", 0.7);

	hexagons
		.transition()
		.duration(500)
		.attr("transform", (d) => `translate(${d.x},${d.y})`)
		.attr("fill", (d) => colorScale(d.pct));

	hexagons.exit().transition().duration(500).attr("opacity", 0).remove();

	court
		.selectAll(".hexagon")
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

	legend
		.append("text")
		.attr("x", LEGEND_WIDTH / 2)
		.attr("y", -5)
		.attr("text-anchor", "middle")
		.attr("fill", "black")
		.attr("stroke", "none")
		.text("Shot Accuracy %");
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

function updateCharts(selectedId) {
	const isTeam = window.data.teams.some((t) => t.id === selectedId);
	const isPlayer = window.data.players.some((p) => p.id === selectedId);

	let filteredData;
	let filteredShots;
	let url;
	if (isTeam) {
		filteredData = window.data.shots_contested.filter(
			(d) => d.X_ID === parseInt(selectedId)
		);
		filteredShots = window.data.shots_loc.filter(
			(d) => d.TEAM_ID === parseInt(selectedId)
		);
		url = `https://cdn.nba.com/logos/nba/${selectedId}/primary/L/logo.svg`;
	} else if (isPlayer) {
		filteredData = window.data.shots_contested.filter(
			(d) => d.X_ID === parseInt(selectedId)
		);
		filteredShots = window.data.shots_loc.filter(
			(d) => d.PLAYER_ID === parseInt(selectedId)
		);
		url = `https://cdn.nba.com/headshots/nba/latest/1040x760/${selectedId}.png`;
	} else {
		filteredData = window.data.shots_contested;
		filteredShots = window.data.shots_loc;
		url = "https://cdn.nba.com/logos/leagues/logo-nba.svg";
	}

	d3.select("#auto_chart").selectAll("image").attr("xlink:href", url);

	updateEfficiencyChart(filteredData);
	updateShotChart(filteredData);
	updateHeatmap(filteredShots);
}

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
		.attr("font-size", "16px")
		.attr("font-weight", "bold")
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
