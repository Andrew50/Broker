<div class ="index">
    <body>
     
        <form on:submit={fetchData}>
          
            <input type="submit" value="Submit">
        </form>
    </body>
    <div id="message"></div>
    <p>{len} tasks in the queue</p>
    <p> {task_id}</p>
</div>



<script>
  let data = '';
  let len = 0;
  let task_id = 'none';

  function tester(){
      console.log('test function is called.')
  }
  async function fetchData() {
  try {
    const url = 'http://localhost:5057/groups/group1';
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    data = await response.json();
    console.log('Response from the server:', data);
    len = data.job
    task_id = data.task_id
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}
</script>

<style>

</style>