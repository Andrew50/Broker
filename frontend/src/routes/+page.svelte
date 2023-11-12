<script>

    import { writable } from 'svelte/store';
    import {onMount} from 'svelte';
    import {ColorType, CrosshairMode} from 'lightweight-charts';
    import {Chart, CandlestickSeries,TimeScale} from 'svelte-lightweight-charts';



    let match_data_store = writable()
    let match_data;
    match_data_store.subscribe((value) => {
    match_data = value
    });
    
    let screener_data_store = writable()
    let screener_data;
    screener_data_store.subscribe((value) => {
    screener_data = value
    });

    export let chart_data_store = writable([
        {time: '2018-10-19', open: 180.34, high: 180.99, low: 178.57, close: 179.85}
    ]);
    let chart_data;
    chart_data_store.subscribe((value) => {
    chart_data = value
    });



    let innerWidth;
    let innerHeight;
    let isMatch = false;
    let isScreener = false;

    let TickerBox;
	let popup = false;
	let TickerBoxValue = '';
	let chartTicker;
	let TickerBoxVisible = "none";
    let value = 'An input.';

    function toggleMatch() {
    isMatch = !isMatch;
    isScreener = false; 
    }
    function toggleScreener() {
    isScreener = !isScreener;
    isMatch = false; 
    }

    let ticker = "AAPL";
    let tf = "1d";
    let dt = "2023-10-03";
    // let chart_ticker = "AAPL";
    // let chart_tf = "1d";
    // let chart_dt = "";
    // let timeScale;
    let key;


    
    export let sample_data = [
  {time: '2018-10-19', open: 180.34, high: 180.99, low: 178.57, close: 179.85}
]
    // task list: chart-get match-get trainer-get trainer-set screener-get study-get study-set settings-set
	
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



    async function startTask(bind_variable,func=false) {
        event.preventDefault(); // Prevent the default form submission
        const formData = new FormData(event.target);
        let formValues = Array.from(formData.values()).join('-');
        let args;
        if (func){
            args = `${func}-${formValues}`;
        }else{
            args = formValues
        }
        const url = `http://localhost:5057/fetch/${args}`;
        try{
        console.log('request sent',url)
        const response = await fetch(url, {method: 'POST',headers: {'Content-Type': 'application/json'},});
        if (!response.ok) {throw new Error('POST response not ok')}
        const responseData = await response.json();
        const task_id = responseData.task_id;
        const checkStatus = async () => {
            const response = await fetch(`http://localhost:5057/poll/${task_id}`);
            if (!response.ok){throw new Error('GET response not ok')}
                const responseData = await response.json();
                const status = responseData.status
                if (responseData.status === 'done') {
                    clearInterval(intervalId);
                    bind_variable.set(responseData.result);
                    console.log(responseData.result);
                }else if(status === 'failed'){
                    clearInterval(intervalId);
                    bind_variable.set('failed')
                }
        };
        const intervalId = setInterval(checkStatus, 500); // Check every 2 seconds
        }catch{
        bind_variable.set(null);
        }
    }

    
    const options = {
        layout: {background: {type: ColorType.Solid,color: '#000000',},textColor: 'rgba(255, 255, 255, 0.9)',},
        grid: {vertLines: {color: 'rgba(197, 203, 206, 0.5)',},horzLines: {color: 'rgba(197, 203, 206, 0.5)',},},
        crosshair: {mode: CrosshairMode.Magnet,},
        rightPriceScale: {borderColor: 'rgba(197, 203, 206, 0.8)',},timeScale: {borderColor: 'rgba(197, 203, 206, 0.8)',},
    }
    
    function onKeydown(event) {
			if (/^[a-zA-Z]$/.test(event.key.toLowerCase()) && popup == false) {
			TickerBoxVisible = "block"
			popup = true;
			TickerBoxValue += event.key.toUpperCase();
			event.preventDefault();
			TickerBox.focus();
			}
			if(event.key == "Enter"){
				TickerBoxVisible = "none"
				chartTicker = TickerBoxValue;
				TickerBoxValue = '';
				popup = false;
				
			} 
			TickerBox.focus();
	}
</script>

<svelte:window 
    on:keydown={onKeydown} 
    bind:innerWidth
    bind:innerHeight
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
        z-index: 1000;
        font-size:40pt;
        text-transform:uppercase;
    }
    .match-button {
    position: fixed;
    right: 20px;
    top: 20px; /* You can adjust the top position as needed */
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    }
    .screener-button {
    position: fixed;
    right: 20px;
    top: 120px; /* You can adjust the top position as needed */
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    }
    .container {
    margin-right: 20px;
    }
    table {
    width: 100%;
    border-collapse: collapse;
    }
    .popout-menu {
    display: none;
    position: fixed;
    right: 70px; /* Offset from the right side */
    top: 0; /* You can adjust the top position as needed */
    background-color: #f9f9f9;
    min-width: 3px;
    box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
    }
    .popout-menu.visible {
    display: block;
    }
</style>

<div class="container">
  <div class="button-container">
    <button class="match-button" on:click={toggleMatch}>
        <div>M</div>
        <div>A</div>
        <div>T</div>
        <div>C</div>
        <div>H</div>
    </button>
    <button class="screener-button" on:click={toggleScreener}>
        <div>S</div>
        <div>C</div>
        <div>R</div>
        <div>E</div>
        <div>E</div>
        <div>N</div>
        <div>E</div>
        <div>R</div>
    </button>
<!--     <button class="screener-button" on:click={toggleStudy}>
        <div>S</div>
        <div>T</div>
        <div>U</div>
        <div>D</div>
        <div>Y</div>
    </button>
    <button class="screener-button" on:click={toggleTrainer}>
        <div>A</div>
        <div>C</div>
        <div>C</div>
        <div>I</div>
        <div>N</div>
        <div>E</div>
        <div>R</div>
    </button>
    <button class="screener-button" on:click={toggleStudy}>
        <div>S</div>
        <div>T</div>
        <div>U</div>
        <div>D</div>
        <div>Y</div>
    </button> -->





    <div class="popout-menu"  style="min-height: {innerHeight}px;" class:visible={isMatch}>
      {#if isMatch}
                    <form on:submit|preventDefault={() => startTask('Match-get',match_data)}>
                    <div class="form-group">
                    <input type="text" id="ticker" bind:value="{ticker}" name="ticker" placeholder="Enter Ticker" required>
                    </div>
                    <div class="form-group">
                    <input type="text" id="tf" bind:value="{tf}" name="tf" placeholder="Enter TF" required>
                    </div>
                    <div class="form-group">
                    <input type="text" id="dt" bind:value="{dt}" name="dt" placeholder="Enter Date Time">
                    </div>
                    <div class="form-group">
                    <input type="submit" value="FETCH">
                    </div>
                    </form>
                    <table>
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Name</th>
                        </tr>
                      </thead>
                      <tbody>
                        {#each $match_data as item}
                          <tr>
                            <td>{item.id}</td>
                            <td>{item.name}</td>
                          </tr>
                        {/each}
                      </tbody>
                    </table>
      {/if}
    </div>
    <div class="popout-menu"  style="min-height: {innerHeight}px;" class:visible={isScreener}>

    {#if isScreener}
        <form on:submit|preventDefault={() => startTask('Screener-get',screener_data)}>
                    
        <div class="form-group">
        <input type="submit" value="Screen">
        </div>
        </form>
         <div>
         this is the letter {key}   
         </div>
         
    {/if}
    </div>
  </div>
</div>
<Chart width={innerWidth - 300}  height={innerHeight - 40} {...options}>
    <CandlestickSeries
        data={sample_data}
        reactive={true}
        upColor="rgba(0,255, 0, 1)"
        downColor="rgba(255, 0, 0, 1)"
        borderDownColor="rgba(255, 0, 0, 1)"
        borderUpColor="rgba(0,255, 0, 1)"
        wickDownColor="rgba(255, 0, 0, 1)"
        wickUpColor="rgba(0,255, 0, 1)"
    />
</Chart>
{chartTicker}
<a href="/test">test</a>

<input class = 'input-overlay' 
	bind:this={TickerBox} 
	bind:value={TickerBoxValue} 
	style ="display: {TickerBoxVisible};"
    use:resizeInputOnDynamicContent
					
/>



