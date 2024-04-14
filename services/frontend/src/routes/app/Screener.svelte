<script>
    import { onMount } from "svelte";
    import { dataset_dev } from "svelte/internal";
    import { writable } from "svelte/store";
    import {
        screener_data,
        setups_list,
        chartQuery,
        request,
    } from "../../store.js";
    import Table from "./Table.svelte";
    let ticker = "";
    let datetime = "";
    let selectedSetups = new Set($setups_list.map((subArray) => subArray.setup_name));
    export let visible = false;
    let innerWidth;
    let innerHeight;
    function handleCheckboxChange(setup, event) {
        if (event.target.checked) {
            selectedSetups.add(setup);
        } else {
            selectedSetups.delete(setup);
        }
    }
</script>

<div class="popout-menu" style="min-height: {innerHeight}px;" class:visible>
    {#if visible}
        {#each $setups_list as setup}
            <div>
                <label class="setup-item">
                    <input
                        type="checkbox"
                        checked
                        on:change={(e) => handleCheckboxChange(setup.setup_name, e)}
                    />
                    {setup.setup_name}
                    <!-- {setup.join(' - ')} -->
                </label>
            </div>
        {/each}
        <button
            on:click={() =>
                request(screener_data, true, "getScreener", [
                    ...selectedSetups,
                ])
            }> Screen </button>
        <Table
            headers={["Ticker", "Setup", "Value"]}
            rows={$screener_data}
            onRowClick={request}
            clickHandlerArgs={[chartQuery, "chart", "Ticker", "1d"]}
        />
    {/if}
</div>

<style>
    @import "./style.css";
    .popout-menu {
        /* Your existing styles */
    }
    /*  .screener-data {
        overflow-y: auto;
        max-height: 200px; /* Adjust as needed 
    } */
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
        <!--<form
            on:submit|preventDefault={() =>
                request(screener_data, true,"getScreener", [
                    ...selectedSetups,
                ])}
            class="input-form"
        >
            <div class="form-group">
                <label for="ticker">Ticker:</label>
                <input
                    type="text"
                    id="ticker"
                    bind:value={ticker}
                    placeholder="Ticker"
                />
            </div>
            <div class="form-group">
                <label for="datetime">Datetime:</label>
                <input
                    type="text"
                    id="datetime"
                    bind:value={datetime}
                    placeholder="YYYY-MM-DD HH:MM"
                />
            </div>
            <input type="submit" value="Screen" />
        </form> -->
