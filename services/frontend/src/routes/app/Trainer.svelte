<script>
    import { writable } from "svelte/store";
    import {
        setups_list,
        chartQuery,
        request,
    } from "../../store.js";
    let selectedRow = writable(null);
    let errorMessage, selected_setup = "";
    let training = false;
    let trainerQueue = writable([]);

    function newSetup() {
        setups_list.update((list) => {
            list.push([]);
            return list;
        });
    }

    function deleteSetup(name) {
        setups_list.update((list) => {
            // Find the index of the setup array that matches the given name
            const index = list.findIndex((setup) => setup[0] === name);
            if (index > -1) {
                list.splice(index, 1); // Remove the found setup
            }
            return list;
        });
        request(null,true, "delete setup", name);
    }

    function rowClickHandler(i,setup) {
        selectedRow.set(i);
        console.log($selectedRow);
        selected_setup = setup;
    }

    function train_all() {
        $setups_list.forEach((setup) => {
            request(null, true,"Trainer-train", setup[0]);
        });
    }
</script>

{#if training}
    <p>Training...</p>
    <div>
        <button on:click={() => {training = false}}>
            Back
        </button>
    </div>
{:else}
<div>
    <table class="table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Score</th>
                <th>Interval</th>
                <th>Bars</th>
                <th>Threshold</th>
                <th>Dolvol</th>
                <th>ADR</th>
                <th>MCap</th>
            </tr>
        </thead>
        <tbody>
            {#each $setups_list as setup, i}
                <tr  on:click={() => rowClickHandler(i,setup[0])}>
                    <td class:selected={i == $selectedRow}>{setup[1]}</td>
                    <td class:selected={i == $selectedRow}>{setup[2]}</td>
                    <td class:selected={i == $selectedRow}>{setup[3]}</td>
                    <td class:selected={i == $selectedRow}>{setup[4]}</td>
                    <td class:selected={i == $selectedRow}>{setup[5]}</td>
                    <td class:selected={i == $selectedRow}>{setup[6]}</td>
                    <td class:selected={i == $selectedRow}>{setup[7]}</td>
                    <td class:selected={i == $selectedRow}>{setup[8]}</td>
                </tr>
            {/each}
        </tbody>
</div>

<div class="setup-actions">
    {#if selected_setup}
        <button on:click={() => {training = true}}>
            Train
        </button>
        <button on:click={() => {}}>
            Delete
        </button>
        <button on:click={() => {errorMessage = request(null,true,'trainModel',selected_setup)[1]}}>
            -- Train Model --
        </button>
    {/if}
    <button on:click={newSetup}>New Setup</button>
</div>
{/if}

{#if errorMessage}
    <p class="error-message">{errorMessage}</p>
{/if}

<style>
    .error-message {
        color: red;
    }
    .table {
        width: 100%;
    }
    .selected {
        background: var(--c2);
    }
    th {
        cursor: pointer;
        font-size: 10px;
    }
    td {
        padding: 5px;
        font-size: 14px;
    }
</style>
