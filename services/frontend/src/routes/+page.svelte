<script>
  import { goto } from "$app/navigation";

  function signIn() {
    goto("/auth"); // Replace '/signin' with the actual route to your sign-in page
  }
</script>

<main class="main-container">
  <div class="container">
    <h1 class="title" style="font-size: 32px;">EdgeFinder</h1>
    <h1 class="title" style="font-size: 32px;">wokring</h1>
    <button
      class="sign-in-button"
      on:click={signIn}
      style="padding: 15px 30px; font-size: 20px;">Sign In</button
    >
  </div>
</main>

<style>
  .main-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f0f0f0; /* Example background color */
  }

  .container {
    text-align: center;
  }

  .title {
    color: #333; /* Example text color */
    margin-bottom: 20px;
  }

  .sign-in-button {
    background-color: #007bff; /* Example button color */
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .sign-in-button:hover {
    background-color: #0056b3; /* Darker shade for hover effect */
  }
</style>
