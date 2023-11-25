

<!-- usage in other scripts-->
<!-- <script>
    
    import { chart_data, match_data } from '../store.js';
    import { backend_request } from '../path/to/backend_request';

    function getChartData(item) {
        backend_request(chart_data, 'Chart-get', item[0], item[1], '1d');
    }
    import CustomTable from './CustomTable.svelte';
</script>

<CustomTable 
    headers={['Ticker Symbol', 'Timestamp', 'Value']} 
    rows={$match_data} 
    onRowClick={getChartData} />
 -->



<script>
    export let headers = []; // Array of header names
    export let rows = [];    // Array of row data
    export let onRowClick;   // Function to handle row click

    function handleRowClick(item) {
        if (typeof onRowClick === 'function') {
            // Resolve dynamic arguments based on the item's values
            const resolvedArgs = clickHandlerArgs.map(arg => 
                headers.includes(arg) ? item[headers.indexOf(arg)] : arg
            );

            onRowClick(...resolvedArgs);
        }
    }
</script>

{#if rows.length > 0}
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
{/if}
