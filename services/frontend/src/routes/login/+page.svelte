<script>
    import Header from '../header.svelte';
  import { goto } from '$app/navigation';
  import { writable } from 'svelte/store';
  import {auth_data,setups_list,settings,request} from '../../store.js'

  let username = '';
  let password = '';
  let errorMessage = '';

  function handleKeydown(event) {
    if (event.key === 'Enter') {
      signIn(username, password);
    }
  }

  async function signIn(username, password) {
    let [response, err] = await request(null,false,'login', username, password);


    if (err){
        errorMessage = err;
    }
    else{

        auth_data.set(response.token);
        settings.set(response.settings);
        setups_list.set(response.setups);
        //watchlist_data.set(response.watchlists);
        // watchlist_data.update(data => {
        // response.watchlists.forEach(key => {
        //     data[key] = []; // Set each key with an empty list
         //});
    //return data;
        await goto('/app');
    }
}

  async function signUp(username, password) {
    _, errorMessage = request(null,false,'signup', username, password);
    await signIn(username, password); // Automatically sign in after account creation
}
</script>

<Header />
<main>
  <div class="container">
    <input type="text" placeholder="Username" bind:value={username} on:keydown={handleKeydown} />
    <input type="password" placeholder="Password" bind:value={password} on:keydown={handleKeydown} />
    <button on:click={() => signIn(username, password)}>Sign In</button>
<!--    <button on:click={() => signUp(username, password)} class="create-account-btn">Create Account</button>-->
    <p class="error-message">{errorMessage}</p>
    {#if errorMessage}
      <p class="error-message">{errorMessage}</p>
    {/if}
  </div>
</main>

<style>
  main {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: var(--c2);
    position: absolute;
    left: 0;
    right: 0;
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
    color: var(--f1);
    background-color: var(--c1);
    border: none;
  }
  input:focus {
    outline: none;
  }

  button {
    background-color: var(--c3);
    color: var(--f1);
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


  .error-message {
    color: red;
    margin-top: 10px;
  }
</style>
