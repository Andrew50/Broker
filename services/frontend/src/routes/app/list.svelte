<script>
    export let headers; // Array of header names
    export let data; // Array of row data
    export let func; // Function to handle row click
    export let useDelete;
    export let visible;
    import {request,autoLoad,currentEntry,toDT} from "../../store.js";
    import {onMount} from 'svelte';
    let visibleAnnotationID = null;
    let stop = () => {};

    $: if (visible ){
        stop = autoLoad(data,50,'getAnnotations',[],() =>
        {
            //get current table location
            const table = document.querySelector('.list');
            let current = 0;
            if (table != null){
                const rows = table.querySelectorAll('#list-table tr');
                if (rows.length > 0){
                    const scrollPos = table.scrollTop;
                    const row_height = rows[rows.length -1].offsetHeight;
                    current = Math.floor(scrollPos / row_height);
                }
            }
            return current;
        });
    }
    else{
        stop();
    }

    function autoResize(event){
        event.target.style.height = 'auto';
        event.target.style.height = (event.target.scrollHeight) + 'px';
    }

    onMount(() => {
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach((textarea) => {
            textarea.style.height = textarea.scrollHeight + 'px';
        });
    });

    function saveRow(i){
        const entry = $currentEntry;
        if (entry != ""){
            const row = $data[i];
            const id = row[row.length - 1];
            data.update((a) => {
                a[i][row.length-2] = true;
                return a;
            });
            request(null,true,`set${func}`,id,entry);
        }

    }

    function handleRowClick(row){
        currentEntry.set('');
        const id = row[row.length - 1];
        if(visibleAnnotationID == id){
            visibleAnnotationID = null;
        }else{
            visibleAnnotationID = id;
            if(row[row.length - 2]){
                currentEntry.set(null);
                request(currentEntry,true,`get${func}Entry`,id);
            }
        }
    }

    function deleteRow(i){
        row = $data[i];
        request(null,true,`del${func}`,row[row.length - 1]);
        data.update((a) => {a.splice(i,1);return a;});
    }
</script>

{#if $data.length}
    <div class="list">
        <table id="list-table">
            <thead>
                <tr>
                    {#each headers as header}
                        <th>{header}</th>
                    {/each}
                </tr>
            </thead>
            {#if $data.length}
                <tbody>
                    {#each $data as row, i}
                        <tr class:clean-green={!row[row.length - 2]} on:click={() => handleRowClick(row)}>
                            <td>{toDT(row[0])}</td> <!-- Date -->
                            {#each row.slice(1,row.length - 2) as cell}
                                <td>{cell}</td>
                            {/each}
                      </tr>
                      {#if visibleAnnotationID == row[row.length - 1]}
                        <tr class="text-entry">
                          <td colspan= {headers.length}>
                            <textarea bind:value={$currentEntry} on:input={autoResize} placeholder="Type here..." rows="1"></textarea>
                            <div class="button-row">
                              <button on:click|stopPropagation={() => saveRow(i)}>Save</button>
                              {#if useDelete}
                                <button on:click|stopPropagation={() => deleteRow(i)}>Delete</button>
                              {/if}
                            </div>
                          </td>
                        </tr>
                      {/if}
                    {/each}
                </tbody>
            {/if}
        </table>
    </div>
{/if}

<style>
    @import "./style.css";

    .list {
        overflow-y: auto;
        height: 100%;
        text-align: center;
        font-family: 'Arial', sans-serif;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        background: #333; /* Dark grey for all table parts */
    }

    table thead tr th {
        background: #333; /* Dark grey for headers */
        color: white;
        border-bottom: 1px solid white; /* White line between header and rows */
    }

    table tbody tr {
        border-bottom: 1px solid grey; /* White line between rows */
    }

    .clean-green {
        background-color: #5e5e5e; /* Light green rows */
    }

    textarea {
        width: 100%;
        min-height: 50px;
        background: #333; /* Dark grey for textarea */
        color: white;
        border: none;
        resize: none;
        overflow: hidden;
        box-sizing: border-box;
        line-height: 1.2;
        padding: 10px; /* Smaller padding for textarea */
    }

    .button-row {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 5px;
    }

    .button-row button {
        background: #333; /* Dark grey for buttons */
        color: white;
        border: none;
        cursor: pointer;
        padding: 5px 10px; /* Smaller buttons */
    }
</style>
