<script>
    import { writable } from 'svelte/store';


    export let data1 = 'None';
    export let taskId1 = null;
    export let taskStatus1 = writable('Not started');
    let data = writable();



    async function startTask(bind_variable) {
      const url = 'http://localhost:5057/groups/group1';
      console.log(url);
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
        });
        if (response.ok) {
            const responseData = await response.json();
            taskId1 = responseData.task_id;
            taskStatus1.set('Pending');
            waitForResult(taskId1, taskStatus1, bind_variable);
        } else {
            console.error('Request failed for Task 1:', response.statusText);
            data1 = 'Failed to start task 1';
        }
    }

    async function waitForResult(taskId, statusStore, bind_variable) {
        const checkStatus = async () => {
            const response = await fetch(`http://localhost:5057/get/${taskId}`);
            if (response.ok) {
            const responseData = await response.json();
            if (responseData.status === 'done') {
                clearInterval(intervalId);
                statusStore.set('Done');
                bind_variable.set(responseData.result);
                console.log('Unpacked Response:', responseData);
                console.log('Unpacked Response:', responseData.result);
            }
            } else {
            clearInterval(intervalId);
            console.error(`Failed to get task status for Task ID ${taskId}`);
            }
        };
        const intervalId = setInterval(checkStatus, 2000); // Check every 2 seconds
    }
    
</script>

<style>
  
</style>

<div>
<form on:submit={startTask(data)}>
     
     <input type="submit" value="FETCH">
</form> 
</div>


<div>
<p>{data}</p>
</div>




