<form on:submit={test}>
     <input type="submit" value="FETCH">
</form>


<script>
    async function test() {
        const url = "http://127.0.0.1:5000/api/run-task";
        console.log('requested celery thing');
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        const responseData = await response.json();
        data = responseData 
        console.log('Unpacked Response:', data);
    }


</script>