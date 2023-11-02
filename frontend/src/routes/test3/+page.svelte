<script>
  var windowWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
  var windowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
  
  let isMatch = false;
  let isScreener = false;

  function toggleMatch() {
    isMatch = !isMatch;
    isScreener = false; 
  }
  function toggleScreener() {
    isScreener = !isScreener;
    isMatch = false; 
  }
  console.log("Window Width: " + windowWidth + " pixels");
    console.log("Window Height: " + windowHeight + " pixels");
    import { writable } from 'svelte/store';
    import {onMount} from 'svelte';
    import {ColorType, CrosshairMode} from 'lightweight-charts';
    import {Chart, CandlestickSeries,TimeScale} from 'svelte-lightweight-charts';
    export let data1 = 'None';
    export let taskId1 = null;
    export let taskStatus1 = writable('Not started');
    export let taskResult1 = writable(null);
    let ticker = "";
    let tf = "";
    let dt = "";
    let timeScale;
    var data = [
    {time: '2018-10-19', open: 180.34, high: 180.99, low: 178.57, close: 179.85},
    {time: '2018-10-22', open: 180.82, high: 181.40, low: 177.56, close: 178.75},
    {time: '2018-10-23', open: 175.77, high: 179.49, low: 175.44, close: 178.53},
    {time: '2018-10-24', open: 178.58, high: 182.37, low: 176.31, close: 176.97},
    ];
    async function startTask1() {
        const url = "http://127.0.0.1:5000/api/get";
        const requestData = {
            ticker: ticker,
            dt: dt,
            tf: tf
        };
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        if (response.ok) {
            const responseData = await response.json();
            taskId1 = responseData.task_id;
            taskStatus1.set('Pending');
            waitForResult(taskId1, taskStatus1, taskResult1);
        } else {
            console.error('Request failed for Task 1:', response.statusText);
            data1 = 'Failed to start task 1';
        }
    }
    

    async function waitForResult(taskId, statusStore, resultStore) {
        const checkStatus = async () => {
            const response = await fetch(`http://127.0.0.1:5000/api/status/${taskId}`);
            if (response.ok) {
            const responseData = await response.json();
            if (responseData.status === 'done') {
                clearInterval(intervalId);
                statusStore.set('Done');
                CandlestickSeries.setData(responseData.result);
                console.log('Unpacked Response:', responeData.result);
            }
            } else {
            clearInterval(intervalId);
            console.error(`Failed to get task status for Task ID ${taskId}`);
            }
        };

        const intervalId = setInterval(checkStatus, 2000); // Check every 2 seconds
    }

    const options = {
        width: windowWidth - 400,
        height: windowHeight -40,
        layout: {
            background: {
                type: ColorType.Solid,
                color: '#000000',
            },
            textColor: 'rgba(255, 255, 255, 0.9)',
        },
        grid: {
            vertLines: {
                color: 'rgba(197, 203, 206, 0.5)',
            },
            horzLines: {
                color: 'rgba(197, 203, 206, 0.5)',
            },
        },
        crosshair: {
            mode: CrosshairMode.Magnet,
        },
        rightPriceScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
        },
        timeScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',

        },
    }
</script>

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

  .popout-menu {
  display: none;
  position: fixed;
  right: 70px; /* Offset from the right side */
  top: 0; /* You can adjust the top position as needed */
  background-color: #f9f9f9;
  min-width: 320px;
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
    </button>
    <div class="popout-menu"  style="min-height: {windowHeight}px;" class:visible={isMatch}>
      {#if isMatch}
        THIS IS MATCH
      {/if}
    </div>
    <div class="popout-menu"  style="min-height: {windowHeight}px;" class:visible={isScreener}>
      {#if isScreener}
        THIS IS SCREENER
      {/if}
    </div>
  </div>
</div>
<Chart {...options}>
    <CandlestickSeries
        data={data}
        reactive={true}
        upColor="rgba(0,255, 0, 1)"
        downColor="rgba(255, 0, 0, 1)"
        borderDownColor="rgba(255, 0, 0, 1)"
        borderUpColor="rgba(0,255, 0, 1)"
        wickDownColor="rgba(255, 0, 0, 1)"
        wickUpColor="rgba(0,255, 0, 1)"
    />
</Chart>
<form on:submit={startTask1}>
     <input type="text" id="ticker" bind:value ={ticker} name="ticker" placeholder="Enter Ticker" required>
     <input type="text" id="tf" bind:value ={tf} name="ticker" placeholder="Enter TF" required>
      <input type="text" id="dt" bind:value ={dt} name="ticker" placeholder="Enter Date Time">
     <input type="submit" value="FETCH">
</form>



