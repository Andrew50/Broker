<script>
    import {
        screener_data,
        setups_list,
        chartQuery,
        request,
    } from "../../store.js";
    import Table from "../../tables/table.svelte";
    import { writable, get } from "svelte/store";
    let selectedSetups = writable(get(setups_list).map((subArray) => subArray[1]));

    function toggleSetup(setupName) {
        selectedSetups.update((current) => {
            const index = current.indexOf(setupName);
            if (index !== -1) {
                // Remove setup if it's already selected
                return current.filter((_, i) => i !== index);
            } else {
                // Add setup if it's not already selected
                return [...current, setupName];
            }
        });
        console.log($selectedSetups);
    }
</script>


<div>
    {#each $setups_list as setup}
        <button
            class="setup-item {$selectedSetups.includes(setup[1]) ? 'selected' : ''  }"
            on:click={() => toggleSetup(setup[1])}
        >
        {setup[1]}
        </button>
    {/each}
</div>
<div>
    <button
        on:click={() => request(screener_data, true, "getScreener", get(selectedSetups)) }> Screen 
    </button>
</div>
<Table
    headers={["Ticker", "Setup", "Value"]}
    data={screener_data}
    onRowClick={request}
    clickHandlerArgs={[chartQuery, "chart", "Ticker", "1d"]}
/>

<style>
    @import "../../global.css";
    .setup-item {
        display: block;
        background-color: var(--c2);
        border: none;
        padding-left: 0.5rem;
        margin: 0.5rem;
        padding: 0.3rem;
    }
    .setup-item.selected {
        background-color: var(--c1);
    }
    div {
        display: flex;
        flex-wrap: wrap;
    }
    button {
        background-color: var(--c3);
        color: var(--f1);
        cursor: pointer;
        border-color: var(--c3);
        border-radius: 2px;
        border-style: solid;
        margin: 0.4rem;
    }

    button:hover {
        background-color: var(--c2);
    }


</style>
