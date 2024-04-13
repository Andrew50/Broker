<script>
    import Annotate from './Annotate.svelte'
/*    import Match from './Match.svelte'
    import Screener from './Screener.svelte'
    import Trainer from './Trainer.svelte'
    import Study from './Study.svelte'
    import Account from './Account.svelte'
    import Settings from './Settings.svelte'
    import Watchlist from './Watchlist.svelte'
    */
    import Chart from './Chart.svelte'
    import {auth_data} from '../../store.js'
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { get } from 'svelte/store';
    import { browser } from '$app/environment';
    import './style.css';

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
        goto('/login');
    }


</script>

<div class="button-container">
    
    <button class="button {active_menu == 'annotate' ? 'active' : ''}" on:click={() =>toggle_menu('annotate')}>
        <im class="icon" src="/annotate.png" alt="" />
    </button>
<!--
    <button class="button {active_menu == 'watchlist' ? 'active' : ''}" on:click={() =>toggle_menu('watchlist')}>
        <im class="icon" src="/watchlist.png" alt="" />
    </button>
    <button class="button {active_menu == 'match' ? 'active' : ''}" on:click={() =>toggle_menu('match')}>
        <img class="icon" src="/match.png" alt="" />
    </button>
    <button class="button {active_menu == 'screener' ? 'active' : ''}" on:click={() =>toggle_menu('screener')}>
        <img class="icon" src="/screener.png" alt="" />
    </button>
    <button class="button {active_menu == 'trainer' ? 'active' : ''}" on:click={() =>toggle_menu('trainer')}>
        <img class="icon" src="/trainer.png" alt="" />
    </button>
    <button class="button {active_menu == 'study' ? 'active' : ''}" on:click={() =>toggle_menu('study')}>
        <img class="icon" src="/study.png" alt="" />
    </button>
    <button class="button {active_menu == 'account' ? 'active' : ''}" on:click={() =>toggle_menu('account')}>
        <img class="icon" src="/account.png" alt="" />
    </button>
    <button class="button {active_menu == 'settings' ? 'active' : ''}" on:click={() =>toggle_menu('settings')}>
        <im class="icon" src="/settings.png" alt="" />
    </button>
    -->
    
</div>
<Annotate visible = {active_menu == 'annotate'}/>
<!--
<Watchlist visible = {active_menu == 'watchlist'}/>
<Match visible = {active_menu == 'match'}/>
<Screener visible = {active_menu == 'screener'}/>
<Trainer visible = {active_menu == 'trainer'}/>
<Study visible = {active_menu == 'study'}/>
<Account visible = {active_menu == 'account'}/>
<Settings visible = {active_menu == 'settings'}/>
-->
<Chart/>


