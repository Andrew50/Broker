<script>
    import { writable } from 'svelte/store';
    import { setups_list,  backend_request, data_request } from '../store.js';
    import Table from './Table.svelte'
    export let visible = false;

    let setupName = '';
    let setupTimeframe = '';
    let setupLength = 0;
    let helper_store = writable({});
    let scores = {};
    let errorMessage = '';
    let selected_setup = '';
    let instance_queue = {};


    setups_list.forEach(setup => {
        instance_queue[setup[0]] = [];
    });
    
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

    function select_setup(setup) {
        selected_setup = setup;
        // Assuming setupTimeframe needs to be fetched or set here
    }

    async function load_instance(){
         const checkStatus = async () => {

            try{
                current_instance = instance_queue[selected_setup][0]
                data_request(chart_data,'chart',...current_instance)

                clearInterval(intervalId);
            }catch{}
        const intervalId = setInterval(checkStatus, 100); // Check every x milliseconds



    }

    function fetch_instance(){
        data_request(null,'setup queue',selected_setup).then((new_instances) => {
            instance_queue[selected_setup] = instance_queue[selected_setup].concat(new_instances)})
        
        
    }

    function label_instance(instance,value){
        backend_request(null,'set sample',selected_setup,value,instance)
        instance_queue[selected_setup].shift()
        load_next_instance()
    }


</script>

<div class="popout-menu" class:visible={visible}>
    {#if visible}
    {#if selected_setup == ''}
    {#if errorMessage} <!-- Check if there's an error message -->
            <p class="error-message">{errorMessage}</p> <!-- Display the error message -->
        {/if}
  
    <Table 
            headers={['Name','TF','Length','Samples','Score']} 
            rows={$setups_list} 
            onRowClick={select_setup}
            clickHandlerArgs={['Name']} />




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
        {#if selected_setup != ''}
            <div class ="trainer">

                <p> Is ths a {selected_setup} <p>
                <button on:click={() => label_instance(current_instance,true)}> Yes  </button>
                <button on:click={() => label_instance(current_instance,false)}> No </button>
                <button on:click={() => {selected_setup = ''}}> Back </button>

            </div>
        {/if}

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
