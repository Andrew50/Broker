
<h1>This is a title </h1>   
<script>
  import './styles.css';
  import { onMount } from 'svelte';
  import {chart} from './chart.js';

  let chartContainer;
  const options = {
      size: 250,
      axesLabels: ["kilometres", 'price'],
      styles: {
        basic: 'gray',
        sport: 'red'
      }
  };
  const ticker = [];
  onMount(() => {
    const Chart = new chart(
      chartContainer,
      ticker,
      options
    );
  });

</script>

<div bind:this={chartContainer} id="chartContainer" ></div>
