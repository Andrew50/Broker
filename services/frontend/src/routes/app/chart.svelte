<!-- chart.svelte -->
<script>
	import { onMount } from "svelte";
	import { chart } from "../../chart/chart.js";
	import {toDT, chartQuery, setups_list,menuLeftPos,  request , currentEntry} from "../../store.js";
	let innerWidth, canvas, innerHeight, Chart, queryLabel,  selectedT, selectedPrice, selectedMenuAction, clickX, clickY;
    let ticker = "AAPL";
	let tf = "1";
	let dt = null;
    let chartMenuVisible = false;
    let pm = false;
    let chartFocused = true;
	let queryError = "";
    let queryValue = "";

    function handleChartClick(event) {
        chartFocused = true;
        chartMenuVisible = false;
        selectedMenuAction = null;
    }

    function updateChartSize(v) {
        if (!canvas) return;
        canvas.width = v;
        canvas.height = window.innerHeight;
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
        menuLeftPos.subscribe((v) => updateChartSize(v));
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
            console.log(queryValue);
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
        <button on:click={() => {currentEntry.update((e) => `${e} [${Chart.ticker}|${Chart.i}|${selectedT}|${Chart.pm}] `)}}>Entry</button>
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
        /*flex-grow: 1;*/

    }
	.menu {
        position: absolute;
        color: white; 
        background-color: var(--c2); 
        padding: 10px; 
        border-radius: 5px; 
        text-align: left; 
        box-sizing: border-box;
        z-index: 1000;
        font-size: 16px; 
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
        font-family: Arial, sans-serif; 
        border: 2px solid var(--c3); 
    }

    .menu button {
        display: block; 
        margin: 5px 0; 
        background-color: var(--c1); 
        color: var(--f1); 
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        text-align: left; 
        width: 100%; 
        box-sizing: border-box; 
        transition: background-color 0.3s; 
        cursor: pointer; 
    }

    .menu button:hover {
        background-color: #505760; 
    }

    .query {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: var(--c2); 
        border: 2px solid var(--c3);
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        box-sizing: border-box;
        z-index: 2000;
        font-size: 16px; 
        color: var(--f1);
        font-family: Arial, sans-serif; 
        text-transform: uppercase; 
    }
    .value {
        font-size: 16pt; 
    }
    .label {
        margin-top: 10px; 
        font-size: 14pt; 
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
