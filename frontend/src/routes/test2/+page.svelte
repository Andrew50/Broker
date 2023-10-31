
<script>
    export let data = 'None';
    export let taskId = null;
    export let taskStatus = 'Not started';
    export let taskResult = null;

    async function startTask() {
        const url = "http://127.0.0.1:5000/api/enqueue";
        const requestData = { value: "someValue" }; // Include the necessary data
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData) // Send the data as JSON
        });

        if (response.ok) {
            const responseData = await response.json();
            taskId = responseData.task_id; // Assuming the backend sends a task_id
            taskStatus = 'Pending';
            console.log('Task ID:', taskId);
        } else {
            console.error('Request failed:', response.statusText);
            data = 'Failed to start task';
        }
    }

    async function checkTaskStatus() {
        if (!taskId) {
            alert('No task has been started yet!');
            return;
        }

        const url = `http://127.0.0.1:5000/result/${taskId}`;
        const response = await fetch(url);

        if (response.ok) {
            const responseData = await response.json();
            taskStatus = responseData.status;
            if (taskStatus === 'finished') {
                taskResult = responseData.result;
            }
            console.log('Task Status:', taskStatus);
            console.log('Task Result:', taskResult);
        } else {
            console.error('Request failed:', response.statusText);
        }
    }
</script>

<form on:submit|preventDefault={startTask}>
    <input type="submit" value="Start Async Task">
</form>

<button on:click={checkTaskStatus}>Check Task Status</button>

<p>Task ID: {taskId}</p>
<p>Task Status: {taskStatus}</p>
<p>Task Result: {JSON.stringify(taskResult)}</p>



<!-- <form on:submit|preventDefault={test}>
    <input type="submit" value="ASYNC">
</form>

<p>{data}</p>

<script>
    export let data = 'None';

    async function test() {
        const url = "http://127.0.0.1:5000/api/enqueue";
        const requestData = { value: "someValue" }; // Include the necessary data
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData) // Send the data as JSON
        });

        if (response.ok) {
            const responseData = await response.json();
            data = responseData.task_id; // Assuming the backend sends a task_id
            console.log('Task ID:', data);
        } else {
            console.error('Request failed:', response.statusText);
            data = 'Failed to get task ID';
        }
    }
</script>
 -->