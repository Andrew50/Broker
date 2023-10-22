<script>
	let count = 0;

	function increment() {
		count += 4;
	}

</script>


<form action="" method="POST">
    <p><input type="text" name="usr" size="10" /></p>
    <p><input type="text" name="password" size="10" /></p>
    <p><input type="submit" value="Send Request" /></p>
</form>


<button on:click={increment}>
  
	Clicked {count}
	{count === 1 ? 'time' : 'times'}
</button>