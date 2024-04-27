<script>
    export let headers; // Array of header names
    export let data; // Array of row data
    export let func; // Function to handle row click
    export let useDelete;
    import {request,autoLoad,currentEntry,toDT} from "../store.js";
    import {onMount,onDestroy} from 'svelte';
    import Entry from './entry.svelte';
    let visibleAnnotationID = null;
    let stopAutoLoad = () => {};


    onMount(() => {
        stopAutoLoad = autoLoad(data,50,`get${func}s`,[],() =>
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
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach((textarea) => {
            textarea.style.height = textarea.scrollHeight + 'px';
        });
        console.log('stop is',stop);
    });
    onDestroy(() => {
        stopAutoLoad();
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
        const row = $data[i];
        request(null,true,`del${func}`,row[row.length - 1]);
        data.update((a) => {a.splice(i,1);return a;});
    }
</script>

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
                    <tr class:finished={row[row.length - 2]} on:click={() => handleRowClick(row)}>
                        <td>{toDT(row[0])}</td> <!-- Date -->
                        {#each row.slice(1,row.length - 2) as cell}
                            <td>{cell}</td>
                        {/each}
                  </tr>
                  {#if visibleAnnotationID == row[row.length - 1]}
                    <tr class="text-entry">
                      <td colspan= {headers.length}>
 <!--                       <textarea bind:value={$currentEntry} placeholder="Type here..." rows="1"></textarea> -->
                        <Entry />
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

<style>
    @import "../global.css";

    .list {
        overflow-y: auto;
        height: 100%;
        text-align: center;
        color: var(--f1);
        overflow-x: hidden;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        background: var(--c2); /* Dark grey for all table parts */
    }

    table thead tr th {
        background: var(--c2); /* Dark grey for headers */
        color: var(--f2);
        border-bottom: 1px solid var(--c4); /* White line between header and rows */
        padding: 5px;
    }

    table tbody tr {
        border-bottom: 1px solid var(--c4); /* White line between rows */
        background: var(--c3); /* Dark grey for rows */
    }

    .finished {
        background: var(--c2);
    }

    .text-entry {
        background: var(--c2); /* Dark grey for text entry */
    }
        


    textarea {
        width: 100%;
        min-height: 50px;
        background: var(--c2); /* Dark grey for textarea */
        color: var(--f1);
        border: none;
        resize: none;
        overflow: hidden;
        box-sizing: border-box;
        line-height: 1.2;
        padding: 10px; /* Smaller padding for textarea */
    }
    textarea:focus {
        outline: none;
    }

    .button-row {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 5px;
        background: var(--c2); /* Dark grey for buttons */
    }

    .button-row button {
        background: var(--c2); /* Dark grey for buttons */
        color: var(--f1);
        border: none;
        cursor: pointer;
        padding: 5px 10px; /* Smaller buttons */
    }
</style>
