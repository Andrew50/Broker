<script>
    import Match from './Match.svelte'
    import Screener from './Screener.svelte'
    import Chart from './Chart.svelte'
    import Trainer from './Trainer.svelte'
    import Study from './Study.svelte'
    import Account from './Account.svelte'
    import Settings from './Settings.svelte'
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
    <button class="button match-button" on:click={() =>toggle_menu('match')}>
        <div>M</div>
        <div>A</div>
        <div>T</div>
        <div>C</div>
        <div>H</div>
    </button>
    <button class="button screener-button" on:click={() =>toggle_menu('screener')}>
        <div>S</div>
        <div>C</div>
        <div>R</div>
        <div>E</div>
        <div>E</div>
        <div>N</div>
        <div>E</div>
        <div>R</div>
    </button>
    <button class="button trainer-button" on:click={() =>toggle_menu('trainer')}>
        <div>T</div>
        <div>R</div>
        <div>A</div>
        <div>I</div>
        <div>N</div>
        <div>E</div>
        <div>R</div>
    </button>
    <button class="button study-button" on:click={() =>toggle_menu('study')}>
        <div>S</div>
        <div>T</div>
        <div>U</div>
        <div>D</div>
        <div>Y</div>
    </button>
    <button class="button account-button" on:click={() =>toggle_menu('account')}>
        <div>A</div>
        <div>C</div>
        <div>C</div>
        <div>O</div>
        <div>U</div>
        <div>N</div>
        <div>T</div>
    </button>
    <button class="button settings-button" on:click={() =>toggle_menu('settings')}>
        <div>S</div>
        <div>E</div>
        <div>T</div>
        <div>T</div>
        <div>I</div>
        <div>N</div>
        <div>G</div>
        <div>S</div>
    </button>
</div>

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
        padding: 10px 20px;
        margin-bottom: 10px;
        cursor: pointer;
        border-radius: 5px;
        font-size: 16px;
        transition: background-color 0.3s;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .button:hover {
        background-color: #0056b3; /* Darker shade for hover effect */
    }

    .match-button {
        /* Additional styling specific to match button if needed */
    }

    .screener-button {
        /* Additional styling specific to screener button if needed */
    }
</style>
