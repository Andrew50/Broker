<script>
    import { writable } from 'svelte/store';
    import { setups_list,  data_request } from '../store.js';

    export let visible = false;

    let setupName = '';
    let setupTimeframe = '';
    let setupLength = 0;
    
    // Function to handle the creation of a new setup
    function createSetup() {
        setupLength = parseInt(setupLength);
    if (setupName && !$setups_list.includes(setupName) && setupLength > 0 && setupTimeframe != '') {
        setups_list.update(list => {
            list.push([setupName,setupTimeframe,setupLength]);
            return list;
        });
        data_request(null, "create setup", setupName, setupTimeframe, setupLength);
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
    function selectSetup(setup) {
        setupName= setup[0]
        setupTimeframe= setup[1]
        setupLength = setup[2]
        // Assuming setupTimeframe needs to be fetched or set here
    }
</script>

<div class="popout-menu" class:visible={visible}>
    {#if visible}
    
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Time Frame</th>
                <th>Length</th>
            </tr>
        </thead>
        <tbody>
            {#each $setups_list as setup}
                <tr on:click={() => selectSetup(setup)}>
                    <td>{setup[0]}</td>
                    <td>{setup[1]}</td>
                    <td>{setup[2]}</td>
                </tr>
            {/each}
        </tbody>
    </table>
        





        <div class="controls">
            <div>
            <input class = "inp" type="text" placeholder="Setup Name" bind:value={setupName} />
            
            <input class = "inp" type="text" placeholder="Setup Timeframe" bind:value={setupTimeframe} />
            <input class = "inp" type="text" placeholder="Setup Length" bind:value={setupLength} />
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
