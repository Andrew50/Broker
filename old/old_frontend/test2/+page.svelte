<script>
	let innerWidth = window.innerWidth;
	let innerHeight = window.innerHeight;
	import { onMount } from 'svelte';
	
	let TickerBox;
	let popup = false;
	let TickerBoxValue = '';
	let chartTicker;
	let TickerBoxVisible = "none";
	
	function onKeydown(event) {
			if (/^[a-zA-Z]$/.test(event.key.toLowerCase()) && popup == false) {
			TickerBoxVisible = "block"
			popup = true;
			TickerBoxValue += event.key;
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
        }
    </style>
<h1>
	{chartTicker}
</h1>
        <input class = 'input-overlay' 
					bind:this={TickerBox} 
					bind:value={TickerBoxValue} 
					placeholder="Search something..."
					style ="display: {TickerBoxVisible};"
					
		/>

