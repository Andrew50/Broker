<svelte:window 
    on:keydown={onKeydown} 
    bind:innerWidth
    bind:innerHeight
/>

<script>
//change
    import { ColorType, CrosshairMode } from 'lightweight-charts';
    import { Chart, CandlestickSeries } from 'svelte-lightweight-charts';
    import { chart_data } from '../store.js';

    let innerWidth, innerHeight;
    let ticker = "AAPL";
    let TickerBoxValue = '';
    let TickerBoxVisible = false;

    const options = {
        layout: { background: { type: ColorType.Solid, color: '#000000' }, textColor: 'rgba(255, 255, 255, 0.9)' },
        grid: { vertLines: { color: 'rgba(197, 203, 206, 0.5)' }, horzLines: { color: 'rgba(197, 203, 206, 0.5)' } },
        crosshair: { mode: CrosshairMode.Magnet },
        rightPriceScale: { borderColor: 'rgba(197, 203, 206, 0.8)' },
        timeScale: { borderColor: 'rgba(197, 203, 206, 0.8)' }
    };

    function onKeydown(event) {
        if (event.key === "Enter" && TickerBoxVisible) {
            ticker = TickerBoxValue;
            data_request(chart_data, 'chart', ticker);
            TickerBoxVisible = false;
            TickerBoxValue = '';
        }
    }
</script>




<Chart width={innerWidth - 500} height={innerHeight - 20} {...options} on:click={() => TickerBoxVisible = true}>
    {#if $chart_data && Array.isArray($chart_data) && $chart_data.length > 0}
        <CandlestickSeries data={$chart_data}
        reactive={true}
        upColor="rgba(0,255, 0, 1)"
        downColor="rgba(255, 0, 0, 1)"
        borderDownColor="rgba(255, 0, 0, 1)"
        borderUpColor="rgba(0,255, 0, 1)"
        wickDownColor="rgba(255, 0, 0, 1)"
        wickUpColor="rgba(0,255, 0, 1)" />
    {:else}
        <!-- Show loading or placeholder content here -->
    {/if}
</Chart>


<Chart width={innerWidth - 500} height={innerHeight - 20} {...options} on:click={() => TickerBoxVisible = true}>
    {#if $chart_data && Array.isArray($chart_data) && $chart_data.length > 0}
        <CandlestickSeries data={$chart_data}
        reactive={true}
        upColor="rgba(0,255, 0, 1)"
        downColor="rgba(255, 0, 0, 1)"
        borderDownColor="rgba(255, 0, 0, 1)"
        borderUpColor="rgba(0,255, 0, 1)"
        wickDownColor="rgba(255, 0, 0, 1)"
        wickUpColor="rgba(0,255, 0, 1)" />
    {/if}
</Chart>

{#if TickerBoxVisible}
    <input class='input-overlay' bind:value={TickerBoxValue} on:keydown={onKeydown} />
{/if}

<style>
    .input-overlay {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: rgba(255, 255, 255, 0.5);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-sizing: border-box;
        z-index: 2000;
        font-size: 40pt;
        text-transform: uppercase;
    }
</style>
<!-- 


<Chart width={innerWidth - 500} height={innerHeight - 20} {...options} on:click={onChartClick} 
    on:blur={onChartBlur}>
    {#if $chart_data && Array.isArray($chart_data) && $chart_data.length > 0}
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
{/if}

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
    font-size: 40pt;
    text-transform:uppercase;
    }
</style> -->