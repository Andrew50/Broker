<svelte:window 
    on:keydown={onKeydown} 
    bind:innerWidth
    bind:innerHeight
/>

<script>
	
	import './style.css';
	import { onMount } from 'svelte';
	import {chart} from './chart.js';
	import {chart2} from './chart2.js';
	import {chart_data, backend_request, data_request} from '../store.js';
    import Account from './Account.svelte';

	let innerWidth;
    let innerHeight;
	let ticker = "AAPL";
    let tf = "1d";
    let dt;

	let TickerBox;
	let popup = false;
	let TickerBoxValue = '';
	let TickerBoxVisible = "none";

    

	
	let chartContainer;
	const options = {
		widthOffset: 500,
		heightOffset: 20 ,
		margin: 30,
		candleWidth: 10
	}
	let Chart
	onMount(() => {
    Chart = new chart2(
      chartContainer,
      chart_data,
      options
    );
	chart_data.subscribe((value) => {Chart.updateData(value)});
	});

	function resizeInputOnDynamicContent(node) {
		
		const measuringElement = document.createElement('div');
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
			measuringElement.style.boxSizing = 'border-box';
			measuringElement.style.border = styles.border;
			measuringElement.style.width='max-content';
			measuringElement.style.position = 'absolute';
			measuringElement.style.top = '0';
			measuringElement.style.left = '-9999px';
			measuringElement.style.overflow = 'hidden';
			measuringElement.style.visibility = 'hidden';
 			measuringElement.style.whiteSpace = 'pre';
			measuringElement.style.height = '0';
			node.style.width = `${(measuringElement.offsetWidth)*1.5}px`;
		}
		duplicateAndSet();
		/** listen to any style changes */
		const observer = new MutationObserver(duplicateAndSet)
		observer.observe(node, { attributes: true, childList: true, subtree: true });
		
		node.addEventListener('input', duplicateAndSet);
		return {
			destroy() {
					observer.disconnect(node);
					node.removeEventListener('input', duplicateAndSet)
			}
		}
	}

    

    function onKeydown(event) {
			if (/^[a-zA-Z]$/.test(event.key.toLowerCase()) && !popup && !(document.activeElement.tagName === 'INPUT' && document.activeElement.type === 'text')&& !(document.activeElement.tagName === 'TEXTAREA' && document.activeElement.type === 'textarea')) {
			TickerBoxVisible = "block"
			popup = true;
			TickerBoxValue += event.key;
			event.preventDefault();
			TickerBox.focus();
			}
			else if(event.key == "Enter" ){
				TickerBoxVisible = "none"
				ticker = TickerBoxValue.toUpperCase();
                data_request(chart_data,'chart', ticker);
				TickerBoxValue = '';
				popup = false;
				
			}
			TickerBox.focus();
	}
	 

</script>

<div bind:this={chartContainer} id="chartContainer" ></div>

<input class = 'input-overlay' 
	bind:this={TickerBox} 
	bind:value={TickerBoxValue} 
	style ="display: {TickerBoxVisible};"
    use:resizeInputOnDynamicContent
/>
		
<style>
	.input-overlay{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: rgba(255, 255, 255, 0.5); /* 50% opacity white background */
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-sizing: border-box;
        z-index: 2000;
        font-size: 40pt;
        text-transform:uppercase;
    }
</style>