<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { screener_data, setups_list, backend_request } from '../store.js';

    let ticker = '';
    let datetime = '';
    let selectedSetups = [];

    export let visible = false;
    let innerWidth;
    let innerHeight;
    // Function to handle checkbox changes
    function handleCheckboxChange(setup, event) {
        if (event.target.checked) {
            selectedSetups.push(setup[0]);
        } else {
            selectedSetups = selectedSetups.filter(s => s !== setup);
        }
    }
    // ... [rest of your script] ...
</script>

<div class="popout-menu" style="min-height: {innerHeight}px;" class:visible={visible}>
    {#if visible}
        <!-- Display setups_list as a checklist above the inputs -->
        {#each $setups_list as setup}
            <label class="setup-item">
                <input type="checkbox" on:change={(e) => handleCheckboxChange(setup, e)}>
                {setup.join(' - ')}
            </label>
        {/each}

        <form on:submit|preventDefault={() => backend_request(screener_data,'Screener-get',ticker,datetime,selectedSetups)} class="input-form">
            <div class="form-group">
                <label for="ticker">Ticker:</label>
                <input type="text" id="ticker" bind:value={ticker} placeholder="Ticker">
            </div>
            <div class="form-group">
                <label for="datetime">Datetime:</label>
                <input type="text" id="datetime" bind:value={datetime} placeholder="YYYY-MM-DD HH:MM">
            </div>
            <input type="submit" value="Screen">
        </form>

        <div class="screener-data">
            <!-- Display screener_data -->
            {#each $screener_data as dataRow}
                <div>{dataRow[0]} - {dataRow[1]}</div>
            {/each}
        </div>
    {/if}
</div>

<style>
    @import './style.css';
    .popout-menu {
        /* Your existing styles */
    }
    .screener-data {
        overflow-y: auto;
        max-height: 200px; /* Adjust as needed */
    }
    .input-form {
        display: flex;
        flex-direction: column;
        gap: 10px; /* Spacing between form elements */
    }
    .form-group {
        display: flex;
        flex-direction: column;
    }
    .setup-item {
        /* Add styling for checklist items here */
    }
    /* Add other styles as needed */
</style>
