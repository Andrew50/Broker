<script>
  import { goto } from '$app/navigation';
  import { writable } from 'svelte/store';
  import {backend_request} from '../store.js'
    import Chart from '../chart/Chart.svelte';

  let username = '';
  let password = '';
  const errorMessage = writable('');

  async function signIn() {
    // Placeholder for actual sign-in logic
    back
    const isValid = username === 'user' && password === 'pass'; // Example validation, replace with real logic

    if (isValid) {
      await goto('/chart');
    } else {
      errorMessage.set('Invalid credentials');
      password = ''; // Clear the password field
    }
  }

  function navigateToCreateAccount() {
    goto('/create-account'); // Navigate to the create account page
  }
</script>

<main>
  <div class="container">
    <h1>Sign In</h1>
    <input type="text" placeholder="Username" bind:value={username} />
    <input type="password" placeholder="Password" bind:value={password} />
    <button on:click={signIn}>Sign In</button>
    <button on:click={navigateToCreateAccount} class="create-account-btn">Create Account</button>
    <p class="error-message">{$errorMessage}</p>
  </div>
</main>

<style>
  main {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f0f0f0;
  }

  .container {
    text-align: center;
  }

  input {
    display: block;
    margin: 10px auto;
    padding: 8px;
    font-size: 16px;
    border-radius: 5px;
    border: 1px solid #ccc;
    width: 80%;
  }

  button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
    margin-top: 10px;
    width: 80%;
  }

  button:hover {
    background-color: #0056b3;
  }

  .create-account-btn {
    background-color: #28a745; /* Green color for create account button */
    margin-top: 5px;
  }

  .create-account-btn:hover {
    background-color: #218838; /* Darker shade for hover effect */
  }

  .error-message {
    color: red;
    margin-top: 10px;
  }
</style>
