<script>
    import { writable } from 'svelte/store';

    let data1 = writable()
    let data1val;
    data1.subscribe((value) => {
    data1val = value
    });

    async function startTask(bind_variable,func) {
        event.preventDefault(); // Prevent the default form submission
        const formData = new FormData(event.target);
        let formValues = Array.from(formData.values()).join('-');
        let args = `${func}-${formValues}`;

        const url = `http://localhost:5057/fetch/${args}`;
        try{
        console.log('request sent',url)
        const response = await fetch(url, {method: 'POST',headers: {'Content-Type': 'application/json'},});
        if (!response.ok) {throw new Error('POST response not ok')}
        const responseData = await response.json();
        const task_id = responseData.task_id;
        const checkStatus = async () => {
            const response = await fetch(`http://localhost:5057/poll/${task_id}`);
            if (!response.ok){throw new Error('GET response not ok')}
                const responseData = await response.json();
                if (responseData.status === 'done') {
                    clearInterval(intervalId);
                    bind_variable.set(responseData.result);
                    console.log(responseData.result);
                }
        };
        const intervalId = setInterval(checkStatus, 500); // Check every 2 seconds
        }catch{
        bind_variable.set(null);
        }
    }

</script>
<style>
</style>
<div>
<form on:submit={(event) => startTask(data1,'Chart_get')}>
<div>
        <input type="text" name="ticker" placeholder="Ticker" required>
        </div>
        <div>
        <input type="text" name="datetime" placeholder="Datetime" required>
        </div>
        <div>
        <input type="text" name="timeframe" placeholder="Timeframe" required>
        </div>
        
     <input type="submit" value="FETCH">
</form> 
  <p>Result: {data1val}</p>
</div>