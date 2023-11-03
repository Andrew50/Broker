<!-- 

<script>
  import { writable } from 'svelte/store';

  // Stores for input values
  let ticker = 'JBL';
  let dt = '2023-10-03';
  let tf = 'd';

  // Existing stores
  export let taskId1 = null;
  export let taskStatus1 = writable('Not started');
  export let taskResult1 = writable(null);





  async function startTask(result_var) {
      // Encode the query parameters
      //taskResult = null
      const queryParams = new URLSearchParams({ ticker, dt, tf }).toString();
      const url = `http://127.0.0.1:5000/api/get?${queryParams}`;
      const requestData = {
          ticker,
          dt,
          tf
      };
      const response = await fetch(url, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
      });
      if (response.ok) {
          const responseData = await response.json();
          taskId1 = responseData.task_id;
          taskStatus1.set('Pending');
          waitForResult(taskId1, taskStatus1, result_var);
      } else {
          console.error('Request failed for Task 1:', response.statusText);
      }
  }

  async function waitForResult(taskId, statusStore, resultStore) {
    const checkStatus = async () => {
      const response = await fetch(`http://127.0.0.1:5000/api/status/${taskId}`);
      if (response.ok) {
        const responseData = await response.json();
        if (responseData.status === 'done') {
          clearInterval(intervalId);
          statusStore.set('Done');
          resultStore.set(responseData.result);
        }
      } else {
        clearInterval(intervalId);
        console.error(`Failed to get task status for Task ID ${taskId}`);
      }
    };

    const intervalId = setInterval(checkStatus, 2000); 
  }
 
</script>

<form on:submit|preventDefault={startTask(data)}>
  <label for="ticker">Ticker:</label>
  <input id="ticker" type="text" bind:value={ticker}>
  
  <label for="dt">Date Time:</label>
  <input id="dt" type="date" bind:value={dt}>
  
  <label for="tf">Time Frame:</label>
  <input id="tf" type="text" bind:value={tf}>
  
  <input type="submit" value="Start Async Task 1">
</form


<p>Task 1 ID: {taskId1}</p>
<p>Task 1 Status: {$data}</p>
<p>Task 1 Result: {JSON.stringify($data)}</p>


"Running"







<!-- 


<script>
  import { writable } from 'svelte/store';
  
  export let data1 = 'None';
  export let taskId1 = null;
  export let taskStatus1 = writable('Not started');
  export let taskResult1 = writable(null);

  async function startTask1() {
      const url = `http://127.0.0.1:5000/api/get?{ticker}&{tf}&{dt}`;
      const requestData = {
          ticker: 'JBL',
          dt: '2023-10-03',
          tf: 'd'
      };
      const response = await fetch(url, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
      });
      if (response.ok) {
          const responseData = await response.json();
          taskId1 = responseData.task_id;
          taskStatus1.set('Pending');
          waitForResult(taskId1, taskStatus1, taskResult1);
      } else {
          console.error('Request failed for Task 1:', response.statusText);
          data1 = 'Failed to start task 1';
      }
  }



  async function waitForResult(taskId, statusStore, resultStore) {
    const checkStatus = async () => {
      const response = await fetch(`http://127.0.0.1:5000/api/status/${taskId}`);
      if (response.ok) {
        const responseData = await response.json();
        if (responseData.status === 'done') {
          clearInterval(intervalId);
          statusStore.set('Done');
          resultStore.set(responseData.result);
        }
      } else {
        clearInterval(intervalId);
        console.error(`Failed to get task status for Task ID ${taskId}`);
      }
    };

    const intervalId = setInterval(checkStatus, 2000); 
  }
</script>

<form on:submit|preventDefault={startTask1}>
  <input type="submit" value="Start Async Task 1">
</form>

<p>Task 1 ID: {taskId1}</p>
<p>Task 1 Status: {$taskStatus1}</p>
<p>Task 1 Result: {JSON.stringify($taskResult1)}</p>
 --> -->