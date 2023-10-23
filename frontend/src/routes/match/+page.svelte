

<div class ="index">
    <body>
        <h1>Match</h1>
        <form>
            <label for="ticker">Ticker:</label>
            <input type="text" id="ticker" name="ticker" placeholder="Enter Ticker" required><br><br>

            <label for="datetime">Datetime:</label>
            <input type="datetime-local" id="datetime" name="datetime" required><br><br>

            <label for="timeframe">Timeframe:</label>
            <input type="text" id="timeframe" name="timeframe" placeholder="Enter Timeframe" required><br><br>

            <input type="submit" value="Submit">
        </form>
    </body>
    <div id="message"></div>
    <button on:click={fetchData}>
	ping server
    </button>

</div>


<script>
  export let data = 'dog2';

  async function fetchData() {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/data', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
          // Add any other headers if necessary
        }
      });
      const responseData = await response.json();
      data = JSON.parse(responseData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }

  // Call the fetchData function when the component is mounted
  fetchData();
</script>

<main>
  {#if data}
    <h1>Data from the server:{data}</h1>
  {:else}
    <p>Loading data...</p>
  {/if}
</main>

<style>
  /* Add your styles here */
</style>