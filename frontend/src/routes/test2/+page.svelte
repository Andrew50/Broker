<script>
    export let data = 'None';
    export let taskId = null;
    export let taskStatus = 'Not started';
    export let taskResult = null;

    async function startTask() {
        const url = "http://127.0.0.1:5000/api/add";
        const requestData = {
            num1: 10,
            num2: 20
        }; // JSON object with the required format
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData) // Send the data as JSON
        });
        if (response.ok) {
            const responseData = await response.json();
            taskId = responseData.id; // Assuming the backend sends a task_id
            taskStatus = 'Pending';
            console.log('Task ID:', taskId);
        } else {
            console.error('Request failed:', response.statusText);
            data = 'Failed to start task';
        }
    }
    
</script>

<form on:submit|preventDefault={startTask}>
    <input type="submit" value="Start Async Task">
</form>

<p>Task ID: {taskId}</p>
<p>Task Status: {taskStatus}</p>
<p>Task Result: {JSON.stringify(taskResult)}</p>

