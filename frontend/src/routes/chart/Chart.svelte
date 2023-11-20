<svelte:window 
    on:keydown={onKeydown} 
    bind:innerWidth
    bind:innerHeight
/>

<script>

	import {ColorType, CrosshairMode} from 'lightweight-charts';
    import {Chart, CandlestickSeries} from 'svelte-lightweight-charts';
	import {chart_data, backend_request} from '../store.js';

	let innerWidth;
    let innerHeight;
	let ticker = "AAPL";
    let tf = "1d";
    let dt;

	let TickerBox;
	let popup = false;
	let TickerBoxValue = '';
	let TickerBoxVisible = "none";

	const options = {
        layout: {background: {type: ColorType.Solid,color: '#000000',},textColor: 'rgba(255, 255, 255, 0.9)',},
        grid: {vertLines: {color: 'rgba(197, 203, 206, 0.5)',},horzLines: {color: 'rgba(197, 203, 206, 0.5)',},},
        crosshair: {mode: CrosshairMode.Magnet,},
        rightPriceScale: {borderColor: 'rgba(197, 203, 206, 0.8)',},timeScale: {borderColor: 'rgba(197, 203, 206, 0.8)',},
    }

	function resizeInputOnDynamicContent(node) {
		const measuringElement = document.createElement('div');
		document.body.appendChild(measuringElement);
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
    let chartFocused = false;

    function onChartClick() {chartFocused = true}

    function onChartBlur() {
    chartFocused = false;
        TickerBoxVisible = "none";
    }

    function onKeydown(event) {
    if (chartFocused) {
        popup = true;
        if (!popup && /^[a-zA-Z]$/.test(event.key.toLowerCase())) {
            TickerBoxVisible = "block";
            popup = true;
            TickerBox.focus();
        }
        if (popup) {
            if (event.key == "Enter") {
                ticker = TickerBoxValue;
                backend_request(chart_data, 'Chart-get', ticker);
                closePopup();
            }else{
                TickerBoxVisible = "block"
                const key_press = event.key.toUpperCase();
                console.log(key_press)
                TickerBoxValue += key_press;
		        event.preventDefault();
            }
        }
    } else {
        chartFocused = false;
    }
}

function closePopup() {
    TickerBoxVisible = "none";
    TickerBoxValue = '';
    popup = false;
    chartFocused = false; // Reset focus state
}

</script>

<Chart width={innerWidth - 300} height={innerHeight - 40} {...options} on:click={onChartClick} 
    on:blur={onChartBlur}>
    <CandlestickSeries
        data={$chart_data}
        reactive={true}
        upColor="rgba(0,255, 0, 1)"
        downColor="rgba(255, 0, 0, 1)"
        borderDownColor="rgba(255, 0, 0, 1)"
        borderUpColor="rgba(0,255, 0, 1)"
        wickDownColor="rgba(255, 0, 0, 1)"
        wickUpColor="rgba(0,255, 0, 1)"
    />
</Chart>

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
    font-size:40pt;
    text-transform:uppercase;
    }
</style>