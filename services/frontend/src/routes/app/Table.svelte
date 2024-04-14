<script>
    import { get } from "svelte/store"; // To get values from Svelte stores
    import { watchlist_data } from "../../store.js";
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
        const resolvedArgs = clickHandlerArgs.map((arg) =>
            headers.includes(arg) ? item[headers.indexOf(arg)] : arg,
        );
        if (typeof onRowClick === "function") {

            onRowClick(...resolvedArgs);
        }else{
            onRowClick.set(resolvedArgs);
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
        max-height: 80vh; /* Adjust this value based on your needs */
        border-collape: collapse;
        width: 100%;
        background-color: #f4f4f8;

    }
    table {
        border-spacing: 0;
        width: 100%;
    }
    th, td {
        text-align: left;
        padding: 8px;
        border-bottom: 1px solid #e0e0e0; /* Soft separator for rows */
        border-right: 1px solid #e0e0e0; /* Soft separator for columns */
    }
    th {
        background-color: #3a3b3c; /* Dark grey background for headers */
        color: white;
    }
    tbody tr:hover {
        background-color: #d0d3d4; /* Lighter shade for hover effect */
    }

    /* Context menu styles */
    .context-menu {
        position: absolute;
        background-color: #4a4b4c; /* Dark grey background */
        border: 1px solid #ccc;
        padding: 10px;
        z-index: 10;
        display: flex;
        flex-direction: column;
        border-radius: 5px; /* Rounded corners for the context menu */
    }
    .context-menu button {
        margin-top: 5px; /* Spacing between buttons */
        background-color: #5a5b5c; /* Slightly lighter grey for buttons */
        color: white;
        border: none;
        padding: 8px;
        border-radius: 3px; /* Rounded corners for buttons */
        cursor: pointer;
    }
    .context-menu button:hover {
        background-color: #6a6b6c; /* Hover effect for buttons */
    }
    .context-menu button:first-child {
        margin-top: 0;
    }
</style>
