<script>
import { writable } from 'svelte/store';
    class Task{
        constructor(func){
            this.func = func;
            this.status = 'new';
            this.store = writable(null);
            //this.value = null;
            
            // this.store.subscribe((value) => {
            // this.value = value;
            // console.log(value);
            // });
        }

        
        async pull(){
            //try{
                const url = `http://localhost:5057/${this.func}`;
                const response = await fetch(`http://localhost:5057/${this.func}`, {method: 'POST',headers: {'Content-Type': 'application/json'},});
                //if (!response.ok){throw new Error('POST response not ok')}
                const response_data = await response.json()
                const task_id = response_data.task_id;

                const checkStatus = async () => {
                    const response = await fetch(`http://localhost:5057/poll/${task_id}`);
                    //if (!response.ok){throw new Error('GET response not ok')}
                    const response_data = await response.json();
                    if (response_data.status === 'done') {
                        clearInterval(interval);
                        this.store.set(response_data.result);
                        return response_data.result;
                    }
                };
                const interval = setInterval(checkStatus, 500);
          //  }catch{
        //            console.error('Request failed for Task 1:', response.statusText);
        //            this.store.set(null);
         //   }
        }
    }
  
    let data1 = new Task('groups/group1')
    let data2 = 'blank';



</script>
<style>
</style>
<div>
<form on:submit={(event) => data1.pull()}>
     <input type="submit" value="FETCH">
</form> 
  <p>Result: {data1.store.get}</p>
</div>




