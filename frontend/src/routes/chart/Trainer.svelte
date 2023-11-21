<script>
    import { writable } from 'svelte/store';
    import { setups_list,  data_request } from '../store.js';

    export let visible = false;

    let setupName = '';
    let setupTimeframe = '';
    
    // Function to handle the creation of a new setup
    function createSetup() {
    if (setupName && !$setups_list.includes(setupName)) {
        setups_list.update(list => {
            list.push(setupName);
            return list;
        });
        data_request(null, "create setup", setupName, setupTimeframe);
    }
}


    // Function to handle the deletion of a setup
    function deleteSetup(name) {
    setups_list.update(list => {
        const index = list.indexOf(name);
        if (index > -1) {
            list.splice(index, 1);
            return list;
        }
        return list;
    });
    data_request(null, "delete setup", name);
}


    // Function to autofill the control area
    function selectSetup(name) {
        setupName = name;
        // Assuming setupTimeframe needs to be fetched or set here
    }
</script>

<div class="popout-menu" class:visible={visible}>
    {#if visible}
        <table>
            {#each $setups_list as setup}
                <tr on:click={() => selectSetup(setup)}>
                    <td>{setup}</td>
                </tr>
            {/each}
        </table>

        <div class="controls">
            <div>
            <input class = "inp" type="text" placeholder="Setup Name" bind:value={setupName} />
            
            <input class = "inp" type="text" placeholder="Setup Timeframe" bind:value={setupTimeframe} />
            </div>
            <div>
            <button on:click={createSetup}>Create Setup</button>
            <button on:click={() => deleteSetup(setupName)}>Delete Setup</button>
            </div>
        </div>
    {/if}
</div>

<style>
@import './style.css';
.inp{
    width: 100px;
}
</style>
