<script>
  import { goto } from '$app/navigation';

  function signIn() {
    goto('/auth'); // Replace '/signin' with the actual route to your sign-in page
  }
</script>

<main>
  <div class="container">
    <h1>EdgeFinder</h1>
    <button on:click={signIn}>Sign In</button>
  </div>
</main>

<style>
  main {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f0f0f0; /* Example background color */
  }

  .container {
    text-align: center;
  }

  h1 {
    color: #333; /* Example text color */
    margin-bottom: 20px;
  }

  button {
    background-color: #007bff; /* Example button color */
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
  }

  button:hover {
    background-color: #0056b3; /* Darker shade for hover effect */
  }
</style>
