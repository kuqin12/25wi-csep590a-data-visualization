---
title: Interactive Visualization Submission
toc: false
---

# Interactive Visualization Submission

```js echo
import { hexbin as d3Hexbin } from "d3-hexbin";

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
const AUTO_WIDTH = SEARCH_WIDTH;
const AUTO_HEIGHT = VIEW_HEIGHT - SEARCH_HEIGHT;
```

```js echo
document.addEventListener("DOMContentLoaded", init);

function init() {
	const svg = d3.create("svg").attr("viewBox", [0, 0, VIEW_WIDTH, VIEW_HEIGHT]);

	drawSelector(svg);
	drawShotChart(svg, window.data.shots_contested);
	drawEfficiencyChart(svg, window.data.shots_contested);

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
		.domain([0, d3.max(processedData, (d) => d.SHOT_PCT)])
		.nice()
		.range([DEFAULT_CHART_HEIGHT, 0]);

	drawShotLines(shotChart, processedData, xScale, yScale);
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

	function drawShotLines(chart, data) {
		const x = d3
			.scaleBand()
			.domain(data.map((d) => d.SEASON))
			.range([0, DEFAULT_CHART_WIDTH])
			.padding(0.1);
		const y = d3
			.scaleLinear()
			.domain([0, d3.max(data, (d) => d.SHOT_PCT)])
			.nice()
			.range([DEFAULT_CHART_HEIGHT, 0]);
		const contestedY = d3
			.scaleLinear()
			.domain([0, d3.max(data, (d) => d.CONTEST_PCT)])
			.nice()
			.range([DEFAULT_CHART_HEIGHT, 0]);

		chart
			.append("path")
			.datum(data)
			.attr("fill", "none")
			.attr("stroke", "steelblue")
			.attr(
				"d",
				d3
					.line()
					.x((d) => x(d.SEASON) + x.bandwidth() / 2)
					.y((d) => y(d.SHOT_PCT))
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
					.x((d) => x(d.SEASON) + x.bandwidth() / 2)
					.y((d) => contestedY(d.CONTEST_PCT))
			);
	}
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
