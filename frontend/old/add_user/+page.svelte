
<p>Task started<p/>









<script>
function checkTaskStatus(taskId) {
  fetch(`/task_status/${taskId}`)     
    .then(response => response.json())
    .then(data => {
      if (data.status === 'SUCCESS') {
        alert('Task finished: ' + data.result);
      } else if (data.status === 'FAILURE') {
        alert('Task failed');
      } else {
        setTimeout(() => checkTaskStatus(taskId), 1000);
      }
    })
    .catch(error => console.error('Error:', error));
}

// Start polling when the page loads
document.addEventListener('DOMContentLoaded', () => {
  const taskId = '...';  // You need to set this to the actual task ID
  checkTaskStatus(taskId);
});
</script>