<div class ="index">
    <body>
        <a href="/">Home</a>
        <h1>Match</h1>
        <form on:submit={fetchData}>
            <label for="ticker">Ticker:</label>
            <input type="text" id="ticker" bind:value ={ticker} name="ticker" placeholder="Enter Ticker" required><br><br>
            <label for="datetime">Datetime:</label>
            <input type="text" bind:value ={dt} id="datetime" name="datetime" required><br><br>
            <label for="timeframe">Timeframe:</label>
            <input type="text" id="timeframe" bind:value ={tf} name="timeframe" placeholder="Enter Timeframe" required><br><br>
            <input type="submit" value="Submit">
        </form>
    </body>
    <div id="message"></div>
</div>


{#if isLoading}
  <p>Loading...</p>
{:else}
  <main>
 <!--  <h1>Data from the server:</h1> -->
  {#if data.length > 0}
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Datetime</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {#each data as row}
          <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
          </tr>
            {/each}
        </tbody>
      </table>
    {/if}
</main>
{/if} 

 
<script>
  export let data = [];
  let isLoading = false;
  let userInput = '';
  let ticker = '';
  let tf = '';
  let dt = '';

  function tester(){
      console.log('test function is called.')
  }
  async function fetchData() {
  try {
    isLoading = true;
    
    const url = `http://127.0.0.1:5000/api/match?ticker=${ticker}&dt=${dt}&tf=${tf}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const responseData = await response.json();
    console.log('Response from the server:', responseData);
    data = responseData.data;
    console.log('Unpacked Response:', data);
    isLoading = false; 

  } catch (error) {
    console.error('Error fetching data:', error);
    isLoading = false;
  }
}
</script>

<style>

</style>