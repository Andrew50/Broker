<script>
    import { onMount } from "svelte";
    import { dataset_dev } from "svelte/internal";
    import { writable } from "svelte/store";
    import {
        screener_data,
        setups_list,
        private_request,
        backend_request,
        chart_data,
    } from "../store.js";
    import Table from "./Table.svelte";

    let ticker = "";
    let datetime = "";
    // let selectedSetups = writable([]);
    //console.log(setups_list.get)
    let selectedSetups = new Set($setups_list.map((subArray) => subArray[0]));
    console.log("god", selectedSetups);
    export let visible = false;
    let innerWidth;
    let innerHeight;
    // Function to handle checkbox changes
    //     onMount(() => {
    //     selectedSetups.set($setups_list.map(setup => setup[0]));
    // });

    // When updating selectedSetups, use the store's update method
    function handleCheckboxChange(setup, event) {
        if (event.target.checked) {
            selectedSetups.add(setup);
        } else {
            selectedSetups.delete(setup);
        }
        console.log(selectedSetups);
        // selectedSetups.update(currentSelected => {
        //     if (event.target.checked) {
        //         return [...currentSelected, setup[0]];
        //     } else {
        //         return currentSelected.filter(s => s !== setup);
        //     }
        // });
    }
    // ... [rest of your script] ...
</script>

<div class="popout-menu" style="min-height: {innerHeight}px;" class:visible>
    {#if visible}
        <!-- Display setups_list as a checklist above the inputs -->
        {#each $setups_list as setup}
            <div>
                <label class="setup-item">
                    <input
                        type="checkbox"
                        checked
                        on:change={(e) => handleCheckboxChange(setup[0], e)}
                    />
                    {setup[0]}
                    <!-- {setup.join(' - ')} -->
                </label>
            </div>
        {/each}

        <form
            on:submit|preventDefault={() =>
                backend_request(screener_data, "Screener-get", selectedSetups)}
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
        </form>

        <Table
            headers={["Ticker", "Setup", "Value"]}
            rows={$screener_data}
            onRowClick={private_request}
            clickHandlerArgs={[chart_data, "chart", "Ticker", "1d"]}
        />
        <!-- <div class="screener-data">
            <!-- Display screener_data -->
        <!--      {#each $screener_data as dataRow}
                <div>{dataRow[0]} - {dataRow[1]}</div>
            {/each} -->
        <!-- </div> -->
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
