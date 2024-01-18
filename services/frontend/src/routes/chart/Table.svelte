<script>
    import { get } from "svelte/store"; // To get values from Svelte stores
    import { watchlist_data } from "../store.js";
    let contextMenuVisible = false;
    let contextMenuPosition = { x: 0, y: 0 };
    let selectedItem = null; // To store the clicked item
    let selectedWatchlist;

    // Function to handle right-click on a table row
    function handleRowRightClick(event, item) {
        event.preventDefault(); // Prevent default context menu
        contextMenuVisible = true;
        contextMenuPosition = { x: event.clientX, y: event.clientY };
        selectedItem = item; // Store the clicked item
    }

    // Function to close the context menu
    function closeContextMenu() {
        contextMenuVisible = false;
    }

    // Function to add item to selected watchlist
    function addToWatchlist(watchlistName) {
        if (selectedItem && watchlistName) {
            watchlist_data.update((current) => {
                return {
                    ...current,
                    [watchlistName]: [
                        ...current[watchlistName],
                        [selectedItem[0]],
                    ],
                };
            });
            closeContextMenu();
        }
    }

    $: watchlistKeys = Object.keys(get(watchlist_data));

    export let headers = []; // Array of header names
    export let rows = []; // Array of row data
    export let onRowClick; // Function to handle row click
    export let clickHandlerArgs = [];

    function handleRowClick(item) {
        if (typeof onRowClick === "function") {
            // Resolve dynamic arguments based on the item's values
            const resolvedArgs = clickHandlerArgs.map((arg) =>
                headers.includes(arg) ? item[headers.indexOf(arg)] : arg,
            );

            onRowClick(...resolvedArgs);
        }
    }
</script>

{#if contextMenuVisible}
    <div
        class="context-menu"
        style="top: {contextMenuPosition.y}px; left: {contextMenuPosition.x}px;"
    >
        {#each watchlistKeys as key}
            <button on:click={() => addToWatchlist(key)}>{key}</button>
        {/each}
        <button on:click={closeContextMenu}>Close</button>
    </div>
{/if}

{#if rows.length > 0}
    <div class="scrollable-table">
        <table>
            <thead>
                <tr>
                    {#each headers as header}
                        <th>{header}</th>
                    {/each}
                </tr>
            </thead>
            <tbody>
                {#each rows as item}
                    <tr
                        on:click={() => handleRowClick(item)}
                        on:contextmenu={(event) =>
                            handleRowRightClick(event, item)}
                    >
                        {#each item as cell}
                            <td>{cell}</td>
                        {/each}
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
{/if}

<style>
    .scrollable-table {
        overflow-y: auto;
        max-height: 400px; /* Adjust this value based on your needs */
    }
    .context-menu {
        position: absolute;
        background-color: white;
        border: 1px solid #ccc;
        padding: 10px;
        z-index: 10;
        display: flex;
        flex-direction: column;
    }

    .context-menu button {
        margin-top: 5px; /* Spacing between buttons */
        /* Additional button styles */
    }
</style>
