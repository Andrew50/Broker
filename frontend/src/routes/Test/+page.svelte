<!-- <h1>Candlestick Chart</h1> -->
<Chart {...options}>
    <CandlestickSeries
        data={data}
        reactive={true}
        upColor="rgba(255, 144, 0, 1)"
        downColor="#000"
        borderDownColor="rgba(255, 144, 0, 1)"
        borderUpColor="rgba(255, 144, 0, 1)"
        wickDownColor="rgba(255, 144, 0, 1)"
        wickUpColor="rgba(255, 144, 0, 1)"
    />
</Chart>
<form on:submit={fetchData}>
     <input type="text" id="ticker" bind:value ={ticker} name="ticker" placeholder="Enter Ticker" required>
     <input type="text" id="tf" bind:value ={tf} name="ticker" placeholder="Enter TF" required>
      <input type="text" id="dt" bind:value ={dt} name="ticker" placeholder="Enter Date Time">
     <input type="submit" value="FETCH">
</form>

<script>
    import {onMount} from 'svelte';
    import {ColorType, CrosshairMode} from 'lightweight-charts';
    import {Chart, CandlestickSeries} from 'svelte-lightweight-charts';
    let ticker = "";
    let tf = "";
    let dt = "";
    let data = [
        {time: '2018-10-19', open: 180.34, high: 180.99, low: 178.57, close: 179.85},
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
        data = responseData 
        console.log('Unpacked Response:', data);
    }

    const options = {
        width: 600,
        height: 300,
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
            mode: CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
        },
        timeScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
            timeVisible: true,
            secondsVisible: false,
        },
    }
    
    

</script>
