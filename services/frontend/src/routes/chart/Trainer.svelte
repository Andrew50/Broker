<script>
    import { writable } from "svelte/store";
    import {
        setups_list,
        chart_data,
        private_request,
        backend_request,
    } from "../store.js";
    import Table from "./Table.svelte";
    export let visible = false;
    import { onMount } from "svelte";

    let setupName = "";
    let setupTimeframe = "";
    let setupLength = 0;
    let helper_store = writable({});
    //let scores = {};
    let errorMessage = "";
    let selected_setup = "";
    let instance_queue = {};
    let current_instance = writable([]);
    let training = false;

    try {
        setups_list.forEach((setup) => {
            instance_queue[setup[0]] = [];
        });
    } catch {}
    // Function to handle the creation of a new setup
    function createSetup() {
        setupLength = parseInt(setupLength);
        if (!setupName || !setupLength > 0 || !setupTimeframe != "") {
            errorMessage = "Empty Input";
        } else if ($setups_list.some((subArray) => subArray[0] === setupName)) {
            errorMessage = "Duplicate Setup";
        } else {
            setups_list.update((list) => {
                list.push([setupName, setupTimeframe, setupLength]);
                return list;
            });
            private_request(
                null,
                "create setup",
                setupName,
                setupTimeframe,
                setupLength,
            );
        }
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
        private_request(null, "delete setup", name);
    }
    helper_store.subscribe((value) => {
        Object.keys(value).forEach((st) => {
            const newScore = value[st].score;

            setups_list.update((list) => {
                return list.map((setup) => {
                    if (setup[0] === st) {
                        setup[4] = newScore;
                    }
                    return setup;
                });
            });
        });
    });

    current_instance.subscribe((value) => {
        private_request(chart_data, "chart", ...value);
    });

    function select_setup(setup) {
        selected_setup = setup;
        private_request(current_instance, "get instance", selected_setup);
        // Assuming setupTimeframe needs to be fetched or set here
    }

    function label_instance(value) {
        private_request(
            null,
            "set sample",
            selected_setup,
            ...$current_instance,
            value,
        );
        //instance_queue[selected_setup].shift()
        private_request(current_instance, "get instance", selected_setup);
    }
</script>

<div class="popout-menu" class:visible>
    {#if visible}
        <div>
            <Table
                headers={["Name", "TF", "Length", "Samples", "Score"]}
                rows={$setups_list}
                onRowClick={select_setup}
                clickHandlerArgs={["Name"]}
            />
        </div>

        {#if errorMessage}
            <p class="error-message">{errorMessage}</p>
            <!-- Display the error message -->
        {/if}

        {#if selected_setup == ""}
            <div class="setup-details">
                <!-- Additional content for when a setup is selected -->

                <div class="controls">
                    <input
                        class="inp"
                        type="text"
                        placeholder="Setup Name"
                        bind:value={setupName}
                    />

                    <input
                        class="inp"
                        type="text"
                        placeholder="Setup Timeframe"
                        bind:value={setupTimeframe}
                    />
                    <input
                        class="inp"
                        type="text"
                        placeholder="Setup Length"
                        bind:value={setupLength}
                    />
                </div>
                <div>
                    <button on:click={createSetup}>Create Setup</button>
                    <button on:click={() => deleteSetup(setupName)}
                        >Delete Setup</button
                    >
                </div>
            </div>
        {/if}

        {#if selected_setup}
            <button
                on:click={() =>
                    backend_request(null, "Trainer-train", selected_setup)}
                >Train</button
            >
            <p>Is this a {selected_setup}?</p>
            <div>
                <button on:click={() => label_instance(true)}> Yes </button>
                <button on:click={() => label_instance(false)}> No </button>
                <button
                    on:click={() => {
                        selected_setup = "";
                    }}
                >
                    Back
                </button>
            </div>
        {/if}
    {/if}
</div>

<style>
    @import "./style.css";
    .inp {
        width: 100px;
    }
    .error-message {
        color: red;
    }
    .setup-details {
        margin-top: 20px; /* Adjust as needed */
        /* Additional styling for the setup details section */
    }
    /* ... other styles ... */
</style>
