<script>
    import { writable } from 'svelte/store';
    import { setups_list,  backend_request, data_request } from '../store.js';

    export let visible = false;

    let setupName = '';
    let setupTimeframe = '';
    let setupLength = 0;
    let helper_store = writable({});
    let scores = {};
    let errorMessage = '';
    
    // Function to handle the creation of a new setup
    function createSetup() {
        setupLength = parseInt(setupLength);
        if (!setupName || !setupLength > 0 || !setupTimeframe != '' ){
            errorMessage = 'Empty Input'
        }
        else if($setups_list.some(subArray => subArray[0] === setupName)) {
            errorMessage = 'Duplicate Setup';
        
                
        }else{
            setups_list.update(list => {
                    list.push([setupName,setupTimeframe,setupLength]);
                    return list;
                });
                data_request(null, "create setup", setupName, setupTimeframe, setupLength);
        }
    }
function deleteSetup(name) {
    setups_list.update(list => {
        // Find the index of the setup array that matches the given name
        const index = list.findIndex(setup => setup[0] === name);
        if (index > -1) {
            list.splice(index, 1); // Remove the found setup
        }
        return list;
    });
    data_request(null, "delete setup", name);
}
   

   helper_store.subscribe(value => {
    Object.keys(value).forEach(st => {
        const newScore = value[st].score;

        setups_list.update(list => {
            return list.map(setup => {
                if (setup[0] === st) {
                    setup[4] = newScore;
                }
                return setup;
            });
        });
    });
});
    

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
    {#if errorMessage} <!-- Check if there's an error message -->
            <p class="error-message">{errorMessage}</p> <!-- Display the error message -->
        {/if}
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Time Frame</th>
                <th>Length</th>
                <th>Sample Size</th>
                <th>Score</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {#each $setups_list as setup}
                <tr on:click={() => selectSetup(setup)}>
                    <td>{setup[0]}</td>
                    <td>{setup[1]}</td>
                    <td>{setup[2]}</td>
                    <td>{setup[3]}</td>
                    <td>{setup[4]}<td>
                    <td><button on:click={() =>backend_request(helper_store,'Trainer-train',setup[0])}>Train</button></td>
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
.error-message {
        color: red; /* Style for the error message */
    }
</style>
