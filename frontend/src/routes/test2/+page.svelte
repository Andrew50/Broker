<script>
	let innerWidth;
	const adjust = innerWidth -300;
	import { onMount } from 'svelte';
	
	
	
</script>

<svelte:window  
	bind:innerWidth
  />

<div>
	Width: {innerWidth - 300}
</div>