<script>
    import { chart_data, setups_list, backend_request } from "../../store.js";
    export let visible = false;
    let innerHeight;
    import { get } from "svelte/store";

    let selected_st = "";

    let annotation;
    let current_instance = writable(["", "1d", ""]);

    import { writable } from "svelte/store";

    function next() {
        console.log(get(current_instance));
        data_request(
            current_instance,
            "study",
            selected_st,
            ...get(current_instance),
            annotation,
        );

        annotation = "";
    }
</script>

<div class="popout-menu" style="min-height: {innerHeight}px;" class:visible>
    {#if visible}
        <div>
            <div>
                <select bind:value={selected_st} on:change={next}>
                    <option disabled selected value=""
                        >Select a watchlist</option
                    >
                    {#each $setups_list as key}
                        <option value={key[0]}>{key[0]}</option>
                    {/each}
                </select>
                <button
                    on:click={() =>
                        backend_request(null, "Study-get", selected_st)}
                    >Fetch [dev]</button
                >
            </div>

            <div>
                <textarea
                    bind:value={annotation}
                    class="large-textarea"
                    placeholder="Enter text here"
                ></textarea>
            </div>
            <div>
                <button on:click={next}>Next</button>
            </div>
        </div>
    {/if}
</div>

<style>
    @import "./style.css";
    .large-textarea {
        width: 100%; /* Full width */
        height: 200px; /* Starting height, can be adjusted */
        padding: 10px; /* Padding for text area */
        font-size: 1em; /* Font size */
        /* Additional styling as needed */
        box-sizing: border-box; /* Include padding and border in the element's total width and height */
        resize: vertical; /* Allow vertical resizing, remove this line if resizing is not needed */
    }
</style>
