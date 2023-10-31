<!-- <h1>Candlestick Chart</h1> -->
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
<form on:submit={fetchData}>
     <input type="text" id="ticker" bind:value ={ticker} name="ticker" placeholder="Enter Ticker" required>
     <input type="text" id="tf" bind:value ={tf} name="ticker" placeholder="Enter TF" required>
      <input type="text" id="dt" bind:value ={dt} name="ticker" placeholder="Enter Date Time">
     <input type="submit" value="FETCH">
</form>

<script>

    var windowWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    var windowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

    // Output the width and height
    console.log("Window Width: " + windowWidth + " pixels");
    console.log("Window Height: " + windowHeight + " pixels");

    import {onMount} from 'svelte';
    import {ColorType, CrosshairMode} from 'lightweight-charts';
    import {Chart, CandlestickSeries,TimeScale} from 'svelte-lightweight-charts';
    let ticker = "";
    let tf = "";
    let dt = "";
    let timeScale;
    var data = [
    { time: 1635528600000, open: 100, high: 110, low: 90, close: 105 },
    { time: 1635528660000, open: 105, high: 115, low: 95, close: 100 },
    // Add more candlestick data points for each minute
    ];

    async function fetchData() {
        const url = `http://127.0.0.1:5000/api/get?ticker=${ticker}&tf=${tf}&dt=${dt}`;

        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        const responseData = await response.json();
        data = responseData;
        data.forEach(function(dataPoint) {
            // Parse the date-time string and convert it to milliseconds
            var dateTimeInMilliseconds = new Date(dataPoint.time).getTime();

            // Update the 'time' property with milliseconds
            dataPoint.time = dateTimeInMilliseconds;
        });
        CandlestickSeries.setData(data);
        console.log('Unpacked Response:', data);
    }

    const options = {
        width: windowWidth - 300,
        height: windowHeight,
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
            autoScale: true,
            timeVisible: true,

        },
    }
    
</script>
