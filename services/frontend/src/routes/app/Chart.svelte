<script>
	import "./style.css";
	import { onMount } from "svelte";
	import { chart } from "../../chart/chart.js";
	import {toDT, chartQuery, setups_list, request , currentEntry} from "../../store.js";
	let innerWidth, innerHeight, Chart, queryLabel, chartContainer, selectedT, selectedPrice, selectedMenuAction, clickX, clickY;
    let ticker = "MSFT";
	let tf = "1d";
	let dt = null;
    let pm, chartMenuVisible, chartFocused = false;
	let queryValue, queryError = "";
	const options = {
        widthOffset: typeof window != 'undefined' ? window.innerWidth * 0.25 : 0,
		heightOffset: 0,
		margin: 30,
		defaultCandleWidth: 10,
	};
    function handleChartClick(event) {
        chartFocused = true;
        chartMenuVisible = false;
    }


    function handleWindowClick(event) { //entire window including chart? 
        if (!chartContainer.contains(event.target)) {
            chartMenuVisible = false;
            chartFocused = false;
            queryValue = "";
            queryLabel = null;
            queryError = "";
        }
    }
	onMount(() => {
		Chart = new chart(chartContainer, options);
        chartQuery.subscribe((value) => {
            //ticker, i, t, pm
            Chart.updateQuery(value[0],value[1],value[2],value[3]);
        });
        chartContainer.addEventListener("contextmenu", (event) => {
            event.preventDefault();
            if (!Chart.queryValid) return;
            clickX = event.clientX - chartContainer.getBoundingClientRect().left;
            clickY = event.clientY - chartContainer.getBoundingClientRect().top;

            chartMenuVisible = true;

            selectedT = Chart.currentT;
            selectedPrice = Chart.currentPrice;
        });
        chartContainer.addEventListener("click", handleChartClick);
        window.addEventListener("click", handleWindowClick);
        return () => {
            window.removeEventListener("click", handleWindowClick);
            chartContainer.removeEventListener("click", handleChartClick);
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


<svelte:window on:keydown={onKeydown} bind:innerWidth bind:innerHeight />
<div bind:this={chartContainer} id="chartContainer"></div>

{#if chartMenuVisible}
    <div class="menu" style="top: {clickY}px; left: {clickX}px;">
        <p>Add {`${Chart.ticker} ${toDT(selectedT)}`} to ...</p>
        <button on:click={() => {selectedMenuAction = "newAnnotation"; chartMenuVisible = false}}>Annotate</button>
        <button on:click={() => {currentEntry.update((e) => `${e} [${Chart.ticker}|${Chart.I}|${selectedT}] `)}}>Entry</button>
    </div>
{/if}
{#if selectedMenuAction}
    <div class="menu" style="top: {clickY}px; left: {clickX}px;">
        {#each $setups_list as setup}
            <button on:click={() => {request(null,true,selectedMenuAction,Chart.ticker,setup.setup_id,selectedT); selectedMenuAction = null; chartMenuVisible = false}}>{setup.setup_name}</button>
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
	.menu {
        position: absolute;
        color: white; /* Text color */
        background-color: #2c2f36; /* Dark background color from the screenshot */
        padding: 10px; /* Adjust to your preference */
        border-radius: 5px; /* Smaller border radius to match the theme */
        text-align: left; /* Align text to the left */
        box-sizing: border-box;
        z-index: 1000;
        font-size: 16px; /* Adjust to your preference */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Subtle shadow for depth */
        font-family: Arial, sans-serif; /* Match font to the screenshot */
    }

    .menu button {
        display: block; /* Make buttons stack vertically */
        margin: 5px 0; /* Add some margin between buttons */
        background-color: #3a3f47; /* Darker background for buttons to stand out */
        color: #ffffff; /* Text color for buttons */
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
        background-color: #20242a; /* Solid background color to match the screenshot */
        border: 2px solid #2962ff; /* Blue border as in the second screenshot */
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        box-sizing: border-box;
        z-index: 2000;
        font-size: 16px; /* Adjust font size to match the theme */
        color: #ffffff; /* Text color to match the theme */
        font-family: Arial, sans-serif; /* Match font to the screenshot */
        text-transform: uppercase; /* Uppercase text for the value */
    }

    .value {
        font-size: 16pt; /* Adjusted font size for consistency */
    }

    .label {
        margin-top: 5px; /* Reduced spacing for a compact look */
        font-size: 12pt; /* Adjusted font size for consistency */
    }
    .value {
        font-size: 24pt; /* Smaller font size for the label */
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
        color: #D8000C;
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
    .update-button {
        position: fixed;
        top: 700px;
        right: 80px;
        z-index: 10000;
        padding: 10px 20px;
        border-radius: 10px;
        background-color: #007bff;
        color: white;
        font-size: 20px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.7);
    }
</style>
