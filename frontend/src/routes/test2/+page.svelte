<form on:submit={test}>
     <input type="submit" value="ASYNC">
</form>

<p>{data}</p>

<script>
export let data = 'None'
    async function test() {
        
        const url = "http://127.0.0.1:5000/api/test2";
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        const responseData = await response.json();
        
        data = responseData.message
        console.log('Unpacked Response:', data);
    }






</script>