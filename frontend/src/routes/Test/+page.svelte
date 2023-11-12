<script>
    import { writable } from 'svelte/store';

    let data1 = writable()
    let data1val;
    data1.subscribe((value) => {
    data1val = value
    });

    async function startTask(bind_variable,func=false) {
        event.preventDefault(); // Prevent the default form submission
        const formData = new FormData(event.target);
        let formValues = Array.from(formData.values()).join('-');
        let args;
        if (func){
            args = `${func}-${formValues}`;
        }else{
            args = formValues
        }
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
                const status = responseData.status
                if (responseData.status === 'done') {
                    clearInterval(intervalId);
                    bind_variable.set(responseData.result);
                    console.log(responseData.result);
                }else if(status === 'failed'){
                    clearInterval(intervalId);
                    bind_variable.set('failed')
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
<form on:submit={(event) => startTask(data1)}>
    <div><input type="text" name="func" placeholder="func" required></div>
    <div><input type="text" name="arg1" placeholder="arg1" ></div>
    <div><input type="text" name="arg2" placeholder="arg2" ></div>
    <div><input type="text" name="arg3" placeholder="arg3" ></div>
    <div><input type="text" name="arg4" placeholder="arg4" ></div>
    <div><input type="text" name="arg5" placeholder="arg5" ></div>
    <div><input type="text" name="arg6" placeholder="arg6" ></div>
    <input type="submit" value="FETCH">
</form> 
  <p>Result: {data1val}</p>
</div>