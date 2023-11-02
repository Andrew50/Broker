<script>
  import { writable } from 'svelte/store';
  
  export let data1 = 'None';
  export let taskId1 = null;
  export let taskStatus1 = writable('Not started');
  export let taskResult1 = writable(null);

  export let data2 = 'None';
  export let taskId2 = null;
  export let taskStatus2 = writable('Not started');
  export let taskResult2 = writable(null);
  
  async function startTask1() {
      const url = "http://127.0.0.1:5000/api/match";
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

  async function startTask2() {
      const url = "http://127.0.0.1:5000/api/match";
      const requestData = {
          ticker: 'AAPL',
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
          taskId2 = responseData.task_id;
          taskStatus2.set('Pending');
          waitForResult(taskId2, taskStatus2, taskResult2);
      } else {
          console.error('Request failed for Task 2:', response.statusText);
          data2 = 'Failed to start task 2';
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

    const intervalId = setInterval(checkStatus, 2000); // Check every 2 seconds
  }
</script>

<form on:submit|preventDefault={startTask1}>
  <input type="submit" value="Start Async Task 1">
</form>

<p>Task 1 ID: {taskId1}</p>
<p>Task 1 Status: {$taskStatus1}</p>
<p>Task 1 Result: {JSON.stringify($taskResult1)}</p>

<form on:submit|preventDefault={startTask2}>
  <input type="submit" value="Start Async Task 2">
</form>

<p>Task 2 ID: {taskId2}</p>
<p>Task 2 Status: {$taskStatus2}</p>
<p>Task 2 Result: {JSON.stringify($taskResult2)}</p>



<!-- <script>
  import { writable } from 'svelte/store';
  
  export let data = 'None';
  export let taskId = null;
  export let taskStatus = writable('Not started');
  export let taskResult = writable(null);
  
  async function startTask() {
      const url = "http://127.0.0.1:5000/api/match";
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
          taskId = responseData.task_id;
          taskStatus.set('Pending');
          waitForResult(taskId);
      } else {
          console.error('Request failed:', response.statusText);
          data = 'Failed to start task';
      }
  }

  async function waitForResult(taskId) {
    const checkStatus = async () => {
      const response = await fetch(`http://127.0.0.1:5000/api/status/${taskId}`);
      if (response.ok) {
        const responseData = await response.json();
        if (responseData.status === 'done') {
          clearInterval(intervalId);
          taskStatus.set('Done');
          taskResult.set(responseData.result);
        }
      } else {
        clearInterval(intervalId);
        console.error('Failed to get task status');
      }
    };

    const intervalId = setInterval(checkStatus, 2000); // Check every 2 seconds
  }
</script>

<form on:submit|preventDefault={startTask}>
  <input type="submit" value="Start Async Task">
</form>

<p>Task ID: {taskId}</p>
<p>Task Status: {$taskStatus}</p>
<p>Task Result: {JSON.stringify($taskResult)}</p>

 -->