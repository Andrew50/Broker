<div class ="index">
    <body>
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

<main>
  <h1>Data from the server:</h1>
  <table>
    <thead>
      <tr>
        <th>Ticker</th>
        <th>Datetime</th>
        <th>Score</th>
      </tr>
    </thead>
    <tbody>
      {#each data as row (row.column1)}
        <tr>
          <td>{row.column1}</td>
          <td>{row.column2}</td>
          <td>{row.column3}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</main>

{#if isLoading}
  <p>Loading...</p>
{:else}
  <main>
  <h1>Data from the server:</h1>
  <table>
    <thead>
      <tr>
        <th>Ticker</th>
        <th>Datetime</th>
        <th>Score</th>
      </tr>
    </thead>
    <tbody>
      {#each data as row (row.column1)}
        <tr>
          <td>{row.column1}</td>
          <td>{row.column2}</td>
          <td>{row.column3}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</main>
{/if}
 
<script>
  export let data = 'dog2';
  let isLoading = false;
  let userInput = '';
  let ticker = '';
  let tf = '';
  let dt = '';
  async function fetchData() {
    try {
      isLoading = true;
      
          
      userInput = ticker.concat('.',dt,'.',tf)
      console.log(userInput)
      const url = `http://127.0.0.1:5000/api/data?inputString=${userInput}`

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
          // Add any other headers if necessary
        }
      });
      const responseData = await response.json();
      console.log('Response from the server:', responseData)
      data = responseData;
      
    } catch (error) {
      console.error('Error fetching data:', error);
    }finally{
        isLoading = false
    }

    
  }

  async function postData() {
  try {

    const postData = { key: 'value' }; // Modify the data you want to send

    const response = await fetch('http://127.0.0.1:5000/api/data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData), // Convert data to JSON
    });

    const responseData = await response.json();
    console.log('Response from the server:', responseData);
  } catch (error) {
    console.error('Error sending data:', error);
  }
}

  // Call the fetchData function when the component is mounted
  fetchData();
</script>




<style>
  /* Add your styles here */
</style>