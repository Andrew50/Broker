


<script>
    export let headers = []; // Array of header names
    export let rows = [];    // Array of row data
    export let onRowClick;   // Function to handle row click
    export let clickHandlerArgs = [];

    function handleRowClick(item) {
        if (typeof onRowClick === 'function') {
            // Resolve dynamic arguments based on the item's values
            const resolvedArgs = clickHandlerArgs.map(arg => 
                headers.includes(arg) ? item[headers.indexOf(arg)] : arg
            );
            console.log('args',resolvedArgs)

            onRowClick(...resolvedArgs);
        }
    }
</script>

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
                <tr on:click={() => handleRowClick(item)}>
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
</style>
