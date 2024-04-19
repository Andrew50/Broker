<!-- chart.svelte -->
<script>
	import { onMount } from "svelte";
	import { chart } from "../../chart/chart.js";
	import {toDT, chartQuery, setups_list, sidebarWidth, request , currentEntry} from "../../store.js";
	let innerWidth, canvas, innerHeight, Chart, queryLabel,  selectedT, selectedPrice, selectedMenuAction, clickX, clickY;
    let ticker = "MSFT";
	let tf = "1d";
	let dt = null;
    let pm, chartMenuVisible = false;
    let chartFocused = true;
	let queryValue, queryError = "";

    function handleChartClick(event) {
        chartFocused = true;
        chartMenuVisible = false;
        selectedMenuAction = null;
    }

    function updateChartSize() {
        if (!canvas) return;
        const sidebarWidthPx = $sidebarWidth / 100 * window.innerWidth;
        const menuWidthPx = window.innerWidth * 0.05;
        const chartWidth = window.innerWidth - sidebarWidthPx - menuWidthPx;
        const chartHeight = window.innerHeight;
        canvas.width = chartWidth;
        canvas.height = chartHeight;
        Chart.draw();
    }

    function handleWindowClick(event) {
        if (!canvas.contains(event.target)) {
            chartMenuVisible = false;
            chartFocused = false;
            queryValue = "";
            queryLabel = null;
            queryError = "";
        }
    }
	onMount(() => {
		Chart = new chart(canvas, {
            margin: 20,
            defaultCandleWidth: 10,
        });
        window.addEventListener("resize", updateChartSize);
        sidebarWidth.subscribe(updateChartSize);
        updateChartSize();
        chartQuery.subscribe((value) => {Chart.updateQuery(value[0],value[1],value[2],value[3]);});
        canvas.addEventListener("contextmenu", (event) => {
            event.preventDefault();
            if (!Chart.queryValid) return;
            clickX = event.clientX - canvas.getBoundingClientRect().left;
            clickY = event.clientY - canvas.getBoundingClientRect().top;
            chartMenuVisible = true;
            selectedT = Chart.currentT;
            selectedPrice = Chart.currentPrice;
        });
        canvas.addEventListener("click", handleChartClick);
        window.addEventListener("click", handleWindowClick);
        return () => {
            window.removeEventListener("click", handleWindowClick);
            canvas.removeEventListener("click", handleChartClick);
        };
    });

    function classifyInput(input){
        if (queryValue) {
        return /^[0-9]$/.test(input[0]) ? "Interval" : "Ticker";
        }else{
            return null;
        }
    }

	function onKeydown(event) {
        if (!chartFocused) return;
        chartMenuVisible = false;
		if (/^[a-zA-Z0-9]$/.test(event.key.toLowerCase())) {
            queryError = ""
			queryValue += event.key;
            queryLabel = classifyInput(queryValue);
		}else if (event.key == "Backspace") {
            queryValue = queryValue.slice(0, -1);
            queryLabel = classifyInput(queryValue);
        }else if (event.key == "Escape") {
            queryValue = "";
            queryLabel = null;
            queryError = "";
        }
        else if (event.key == "Enter") {
            switch (queryLabel) {
                case "Ticker":
                    ticker = queryValue.toUpperCase();
                    chartQuery.set([ticker,tf,dt,pm]);
                    break;
                case "Interval":
                    tf = queryValue;
                    chartQuery.set([ticker,tf,dt,pm]);
                    break;
                case "Date":
                    break;
                case null:
                    queryError = "Invalid Input";
                    break;
            }
			queryValue = "";
		}
	}
</script>


<canvas bind:this={canvas} class="chart-container"></canvas>
<svelte:window on:keydown={onKeydown} bind:innerWidth bind:innerHeight />

{#if chartMenuVisible}
    <div class="menu" style="top: {clickY}px; left: {clickX}px;">
        <p>Add {`${Chart.ticker} ${toDT(selectedT)}`} to ...</p>
        <button on:click={() => {selectedMenuAction = "newAnnotation"; chartMenuVisible = false}}>Annotate</button>
        <button on:click={() => {currentEntry.update((e) => `${e} [${Chart.ticker}|${Chart.i}|${selectedT}] `)}}>Entry</button>
    </div>
{/if}
{#if selectedMenuAction}
    <div class="menu" style="top: {clickY}px; left: {clickX}px;">
        {#each $setups_list as setup}
            <button on:click={() => {request(null,true,selectedMenuAction,Chart.ticker,setup[0],selectedT); selectedMenuAction = null; chartMenuVisible = false}}>{setup[1]}</button>
        {/each}
    </div>
{/if}

{#if queryValue}
    <div class="query">
        <div class="value">{queryValue}</div>
        <div class="label">{queryLabel}</div>
    </div>
{/if}
{#if queryError}
    <div class="queryError">
        {queryError}
    </div>
{/if}

<style>
    @import "../../global.css";
    .chart-container {
        background-color: black;
        width: 100%;
        height: 100%;
        flex-grow: 1;

    }
	.menu {
        position: absolute;
        color: white; /* Text color */
        background-color: var(--c2); /* Dark background color from the screenshot */
        padding: 10px; /* Adjust to your preference */
        border-radius: 5px; /* Smaller border radius to match the theme */
        text-align: left; /* Align text to the left */
        box-sizing: border-box;
        z-index: 1000;
        font-size: 16px; /* Adjust to your preference */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Subtle shadow for depth */
        font-family: Arial, sans-serif; /* Match font to the screenshot */
        border: 2px solid var(--c3); /* Blue border as in the second screenshot */
    }

    .menu button {
        display: block; /* Make buttons stack vertically */
        margin: 5px 0; /* Add some margin between buttons */
        background-color: var(--c1); /* Darker background for buttons to stand out */
        color: var(--f1); /* Text color for buttons */
        border: none;
        border-radius: 4px; /* Rounded borders for buttons */
        padding: 10px 20px;
        text-align: left; /* Align text to the left for buttons */
        width: 100%; /* Make buttons full width */
        box-sizing: border-box; /* Include padding and border in the width */
        transition: background-color 0.3s; /* Transition for interactive effect */
        cursor: pointer; /* Pointer cursor on hover */
    }

    .menu button:hover {
        background-color: #505760; /* Slightly lighter on hover */
    }

    .query {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: var(--c2); /* Solid background color to match the screenshot */
        border: 2px solid var(--c3); /* Blue border as in the second screenshot */
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        box-sizing: border-box;
        z-index: 2000;
        font-size: 16px; /* Adjust font size to match the theme */
        color: var(--f1); /* Text color to match the theme */
        font-family: Arial, sans-serif; /* Match font to the screenshot */
        text-transform: uppercase; /* Uppercase text for the value */
    }
    .value {
        font-size: 16pt; /* Adjusted font size for consistency */
    }
    .label {
        margin-top: 10px; /* Adjust spacing between value and label */
        font-size: 14pt; /* Smaller font size for the label */
        /*color: #000; /* Optional: different color for the label */
    }
    .queryError {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 10000;
        color: var(--c4);
        background-color: #FFD2D2;
        padding: 20px 40px;
        border-radius: 10px;
        border: 2px solid #D8000C;
        box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.7);
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        max-width: 600px;
        word-wrap: break-word;
        box-sizing: border-box;
    }
</style>
