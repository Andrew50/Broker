<script>

    import { writable } from 'svelte/store';
    import {onMount} from 'svelte';
    import {ColorType, CrosshairMode} from 'lightweight-charts';
    import {Chart, CandlestickSeries,TimeScale} from 'svelte-lightweight-charts';
    export let match_data = writable([])
    export let data1 = 'None';
    export let taskId1 = null;
    export let taskStatus1 = writable('Not started');
    //export let taskResult1 = writable(null);


    let innerWidth;
    let innerHeight;
    let isMatch = false;
    let isScreener = false;
    let isStudy = false;
    let isTrainer = false;
    let isAccount = false;
    let isBroker = false;
    let isSettings = false;



     // $: {
     //    if (chart_data.length > 0 && CandlestickSeries) {
     //      CandlestickSeries.setData($chart_data);
     //        }
     //      }

    function toggleMatch() {
    isMatch = !isMatch;
    isScreener = false; 
    }
    function toggleScreener() {
    isScreener = !isScreener;
    isMatch = false; 
    }
    // function toggleScreener() {
    // isScreener = !isMatch;
    // isMatch = false; 
    // }
    // function toggleScreener() {
    // isScreener = !isScreener;
    // isMatch = false; 
    // }
    
    let ticker = "AAPL";
    let tf = "1d";
    let dt = "2023-10-03";
    let chart_ticker = "AAPL";
    let chart_tf = "1d";
    let chart_dt = "";
    let timeScale;

    export let chart_data = writable([
  {time: '2018-10-19', open: 180.34, high: 180.99, low: 178.57, close: 179.85}
]);

    export let sample_data = [
  {time: '2018-10-19', open: 180.34, high: 180.99, low: 178.57, close: 179.85}
]
    // task list: chart-get match-get trainer-get trainer-set screener-get study-get study-set settings-set



    async function startTask(task,bind_variable) {
        const queryParams = new URLSearchParams({ ticker, tf, dt }).toString();
      const url = `http://127.0.0.1:5000/api/${task}?${queryParams}`;
      console.log(url);
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        });
        if (response.ok) {
            const responseData = await response.json();
            taskId1 = responseData.task_id;
            taskStatus1.set('Pending');
            waitForResult(taskId1, taskStatus1, bind_variable);
        } else {
            console.error('Request failed for Task 1:', response.statusText);
            data1 = 'Failed to start task 1';
        }
    }

    async function waitForResult(taskId, statusStore, bind_variable) {
        const checkStatus = async () => {
            const response = await fetch(`http://127.0.0.1:5000/api/status/${taskId}`);
            if (response.ok) {
            const responseData = await response.json();
            if (responseData.status === 'done') {
                clearInterval(intervalId);
                statusStore.set('Done');
                bind_variable.set(responseData.result);
                console.log('Unpacked Response:', responseData);
                console.log('Unpacked Response:', responseData.result);
            }
            } else {
            clearInterval(intervalId);
            console.error(`Failed to get task status for Task ID ${taskId}`);
            }
        };
        const intervalId = setInterval(checkStatus, 2000); // Check every 2 seconds
    }
    const options = {
        layout: {background: {type: ColorType.Solid,color: '#000000',},textColor: 'rgba(255, 255, 255, 0.9)',},
        grid: {vertLines: {color: 'rgba(197, 203, 206, 0.5)',},horzLines: {color: 'rgba(197, 203, 206, 0.5)',},},
        crosshair: {mode: CrosshairMode.Magnet,},
        rightPriceScale: {borderColor: 'rgba(197, 203, 206, 0.8)',},timeScale: {borderColor: 'rgba(197, 203, 206, 0.8)',},
    }
</script>

<svelte:window  
	bind:innerWidth
    bind:innerHeight
  />

<style>
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
  .popout-menu button {
    width: 100%;
    padding: 10px;
    border: none;
    text-align: left;
  }
  .popout-menu button:hover {
    background-color: #ddd;
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
    <button class="screener-button" on:click={toggleStudy}>
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
    </button>





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
<form on:submit={startTask('Chart-get',chart_data)}>
     <input type="text" id="ticker" bind:value ={chart_ticker} name="ticker" placeholder="Enter Ticker" required>
     <input type="text" id="tf" bind:value ={chart_tf} name="tf" placeholder="Enter TF" required>
      <input type="text" id="dt" bind:value ={chart_dt} name="dt" placeholder="Enter Date Time">
     <input type="submit" value="FETCH">
</form> 


<a href="/test2">test2</a>



