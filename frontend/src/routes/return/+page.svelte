<script>
    import { writable } from 'svelte/store';



    

    let data1 = writable()
    let data1val;
    data1.subscribe((value) => {
    data1val = value
    });
    async function startTask(bind_variable) {
      const url = 'http://localhost:5057/groups/group1';
      console.log(url);
        const response = await fetch(url, {method: 'POST',headers: {'Content-Type': 'application/json'},});
        if (response.ok) {
            const responseData = await response.json();
            const task_id = responseData.task_id;
            waitForResult(task_id, bind_variable);
        } else {
            console.error('Request failed for Task 1:', response.statusText);
            bind_variable.set(null);
        }
    }
    async function waitForResult(taskId, bind_variable) {
        const checkStatus = async () => {
            const response = await fetch(`http://localhost:5057/poll/${taskId}`);
            if (response.ok) {
                const responseData = await response.json();
                if (responseData.status === 'done') {
                    clearInterval(intervalId);

                    bind_variable.set(responseData.result);
                }
            } else {
                clearInterval(intervalId);
                console.error(`Failed to get task status for Task ID ${taskId}`);
            }
        };
        const intervalId = setInterval(checkStatus, 500); // Check every 2 seconds
    }
</script>
<style>
</style>
<div>
<form on:submit={(event) => startTask(data1)}>
     <input type="submit" value="FETCH">
</form> 
  <p>Result: {data1val}</p>
</div>