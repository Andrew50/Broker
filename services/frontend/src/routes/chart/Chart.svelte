<script>
	import "./style.css";
	import { onMount } from "svelte";
	import { chart } from "./chart.js";
	import { chart2 } from "./chart2.js";
	import { chart_data, private_request, backend_request } from "../store.js";
	import Account from "./Account.svelte";
// hi
	let innerWidth;
	let innerHeight;
	let ticker = "AAPL";
	let tf = "1d";
	let dt;

	let TickerBox;
	let popup = false;
	let TickerBoxValue = "";
	let TickerBoxVisible = "none";

	let errorMessage = "";
	let chartContainer;
	const options = {
		widthOffset: 500,
		heightOffset: 20,
		margin: 30,
		candleWidth: 10,
	};
	let Chart;
	onMount(() => {
		Chart = new chart2(chartContainer, chart_data, options);
		chart_data.subscribe((value) => {
			// console.log("chart_data", value);
			// if (!Array.isArray(value)) {
			// 	value = [];
			// }
			Chart.updateData(value);
		});
		//innerWidth.subscribe((value) => {Chart.updateInnerWidth(value)});
		//innerHeight.subscribe((value) => {Chart.updateInnerHeight(value)});
	});

	function resizeInputOnDynamicContent(node) {
		const measuringElement = document.createElement("div");
		document.body.appendChild(measuringElement);

		/** duplicate the styles of the existing node, but
		remove the measuring element from the viewport. */
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
		/** listen to any style changes */
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

	function onKeydown(event) {
		if (
			/^[a-zA-Z]$/.test(event.key.toLowerCase()) &&
			!popup &&
			!(
				document.activeElement.tagName === "INPUT" &&
				document.activeElement.type === "text"
			) &&
			!(
				document.activeElement.tagName === "TEXTAREA" &&
				document.activeElement.type === "textarea"
			)
		) {
			TickerBoxVisible = "block";
			popup = true;
			TickerBoxValue += event.key;
			event.preventDefault();
			TickerBox.focus();
		} else if (event.key == "Enter") {
			TickerBoxVisible = "none";
			ticker = TickerBoxValue.toUpperCase();
			private_request(chart_data, "chart", ticker)
			.then(result => {
				errorMessage = result;
				console.log(errorMessage)
			})
			.catch(error => {
				errorMessage = error.message;
			});

			// if (! $chart_data) {
			// 	errorMessage = "Ticker Unavailable"}
			TickerBoxValue = "";
			popup = false;
		}
		TickerBox.focus();
	}
</script>
<div>test</div>
<div bind:this={chartContainer} id="chartContainer"></div>

{#if errorMessage}
    <div class="error-message">
        {errorMessage}
    </div>
{/if}


<svelte:window on:keydown={onKeydown} bind:innerWidth bind:innerHeight />


<input
	class="input-overlay"
	bind:this={TickerBox}
	bind:value={TickerBoxValue}
	style="display: {TickerBoxVisible};"
	use:resizeInputOnDynamicContent
/>

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
		); /* 50% opacity white background */
		padding: 20px;
		border-radius: 10px;
		text-align: center;
		box-sizing: border-box;
		z-index: 2000;
		font-size: 40pt;
		text-transform: uppercase;
	}
    .error-message {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10000; /* High z-index to ensure it's on top */
    color: #D8000C; /* Modified error color for better visibility */
    background-color: #FFD2D2; /* Light red background for contrast */
    padding: 20px 40px; /* Increased padding for a larger appearance */
    border-radius: 10px; /* Larger border radius for a softer look */
    border: 2px solid #D8000C; /* Thicker border */
    box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.7); /* More pronounced shadow for depth */
    font-size: 20px; /* Larger font size for better readability */
    font-weight: bold; /* Bold font for emphasis */
    text-align: center;
    max-width: 600px; /* Fixed max-width for consistent sizing */
    word-wrap: break-word;
    box-sizing: border-box; /* Ensures padding doesn't affect the overall width */
}

</style>
