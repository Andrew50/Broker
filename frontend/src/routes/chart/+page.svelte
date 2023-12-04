<script>
    import Match from './Match.svelte'
    import Screener from './Screener.svelte'
    import Chart from './Chart.svelte'
    import Trainer from './Trainer.svelte'
    import Study from './Study.svelte'
    import Account from './Account.svelte'
    import Settings from './Settings.svelte'
    import Watchlist from './Watchlist.svelte'
    import {auth_data} from '../store.js'
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { get } from 'svelte/store';
    import { browser } from '$app/environment';

    let active_menu = '';

    function toggle_menu(menuName) {
    if (active_menu == menuName) {
        active_menu = ''; // If the same menu is clicked again, close it
    } else {
        active_menu = menuName; // Open the clicked menu and store its name as the active one
    }
    console.log(active_menu)
    }



    $: isAuthenticated = $auth_data !== null;
    $: if (!isAuthenticated && browser) {
        goto('/auth');
    }


</script>

<div class="button-container">
    
    <button class="button" on:click={() =>toggle_menu('watchlist')}>
        <im class="icon" src="/watchlist.png" alt="" />
    </button>
    <button class="button" on:click={() =>toggle_menu('match')}>
        <img class="icon" src="/match.png" alt="" />
    </button>
    <button class="button" on:click={() =>toggle_menu('screener')}>
        <img class="icon" src="/screener.png" alt="" />
    </button>
    <button class="button" on:click={() =>toggle_menu('trainer')}>
        <img class="icon" src="/trainer.png" alt="" />
    </button>
    <button class="button" on:click={() =>toggle_menu('study')}>
        <img class="icon" src="/study.png" alt="" />
    </button>
    <button class="button" on:click={() =>toggle_menu('account')}>
        <img class="icon" src="/account.png" alt="" />
    </button>
    <button class="button" on:click={() =>toggle_menu('settings')}>
        <im class="icon" src="/settings.png" alt="" />
    </button>
    
</div>

<Watchlist visible = {active_menu == 'watchlist'}/>
<Match visible = {active_menu == 'match'}/>
<Screener visible = {active_menu == 'screener'}/>
<Trainer visible = {active_menu == 'trainer'}/>
<Study visible = {active_menu == 'study'}/>
<Account visible = {active_menu == 'account'}/>
<Settings visible = {active_menu == 'settings'}/>
<Chart/>


<style>
    .button-container {
        position: fixed;
        right: 20px;
        top: 20px;
    }

    .button {
        background-color: #007bff; /* Blue color, consistent with theme */
        color: white;
        border: none;
        padding: 10px 10px;
        margin-bottom: 7px;
        cursor: pointer;
        border-radius: 5px;
        font-size: 10px;
        transition: background-color 0.3s;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .button:hover {
        background-color: #0056b3; /* Darker shade for hover effect */
    }
    .icon{
        width:30px;
        height:30px;
    }
  

</style>
