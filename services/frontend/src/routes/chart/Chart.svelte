<script>
	import "./style.css";
	import { onMount } from "svelte";
	import { chart2 } from "./chart2.js";
	import { chart_data, request} from "../store.js";
	let innerWidth;
	let innerHeight;
    let ticker = "MSFT";
	let tf = "1d";
	let dt = null;
    let bars = 100;
    let pm = false;
	let Chart;
	let queryValue = "";
    let queryError = "";
    let queryLabel;
	let chartContainer;
	const options = {
        widthOffset: typeof window != 'undefined' ? window.innerWidth * 0.25 : 0,
		heightOffset: 0,
		margin: 30,
		candleWidth: 10,
	};
	onMount(() => {
		Chart = new chart2(chartContainer, chart_data, options);
		chart_data.subscribe((value) => {
			Chart.updateData(value);
		});
	});

	function resizeInputOnDynamicContent(node) {
		const measuringElement = document.createElement("div");
		document.body.appendChild(measuringElement);
		function duplicateAndSet() {
			const styles = window.getComputedStyle(node);
			measuringElement.innerHTML = node.value;
			measuringElement.style.fontSize = styles.fontSize;
			measuringElement.style.fontFamily = styles.fontFamily;
			measuringElement.style.paddingLeft = styles.paddingLeft;
			measuringElement.style.paddingRight = styles.paddingRight;
			measuringElement.style.boxSizing = "border-box";
			measuringElement.style.border = styles.border;
			measuringElement.style.width = "max-content";
			measuringElement.style.position = "absolute";
			measuringElement.style.top = "0";
			measuringElement.style.left = "-9999px";
			measuringElement.style.overflow = "hidden";
			measuringElement.style.visibility = "hidden";
			measuringElement.style.whiteSpace = "pre";
			measuringElement.style.height = "0";
			node.style.width = `${measuringElement.offsetWidth * 1.5}px`;
		}
		duplicateAndSet();
		const observer = new MutationObserver(duplicateAndSet);
		observer.observe(node, {
			attributes: true,
			childList: true,
			subtree: true,
		});
		node.addEventListener("input", duplicateAndSet);
		return {
			destroy() {
				observer.disconnect(node);
				node.removeEventListener("input", duplicateAndSet);
			},
		};
	}

    function classifyInput(input){
        if (queryValue) {
        return /^[0-9]$/.test(input[0]) ? "Interval" : "Ticker";
        }else{
            return null;
        }
    }
	function onKeydown(event) {
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
                    request(chart_data,true, "getChart", ticker,tf,dt,bars,pm).then((value) => {
                        queryError = value;
                    });
                    break;
                case "Interval":
                    tf = queryValue;
                    request(chart_data,true, "getChart", ticker,tf,dt,bars,pm).then((value) => {
                        queryError = value;
                    });
                    break;
                case null:
                    queryError = "Invalid Input";
                    break;
            }
			queryValue = "";
		}
	}
</script>

{#if queryError}
    <div class="queryError">
        {queryError}
    </div>
{/if}


<svelte:window on:keydown={onKeydown} bind:innerWidth bind:innerHeight />

<div bind:this={chartContainer} id="chartContainer"></div>

{#if queryValue}
    <div class="input-overlay">
        <div class="value">{queryValue}</div>
        {#if queryLabel}
            <div class="label">{queryLabel}</div>
        {/if}
    </div>
{/if}

<style>
	.input-overlay {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		background-color: rgba(
			255,
			255,
			255,
			0.5
		); 
        padding: 20px;
		border-radius: 10px;
		text-align: center;
		box-sizing: border-box;
		z-index: 2000;
		font-size: 40pt;
		text-transform: uppercase;
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
</style>
