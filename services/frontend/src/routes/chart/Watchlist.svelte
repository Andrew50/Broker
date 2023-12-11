<script>
    import { writable, get } from 'svelte/store';
    import { chart_data, data_request, watchlist_data } from '../store.js';
    import Table from './Table.svelte';
    
    export let visible = false;
    let selected_watchlist = '';
    let watchlist_name = '';

    let ticker_name = '';
    // Function to handle the selection of a watchlist
    function selectWatchlist(event) {
        selected_watchlist = event.target.value;
    }

    function create_watchlist(){
        if (watchlist_name != ''){ 
        const currentData = get(watchlist_data);

    // Check if watchlist_name is not in the keys of the watchlist_data
        if (!(watchlist_name in currentData)){
        watchlist_data.update(currentData => {
        return {
            ...currentData, 
            [watchlist_name]: []
        };
        
    });
    watchlist_name = ''
        }}
    }

    function add_ticker(){
        watchlist_data.update(current => {
        return { ...current, [selected_watchlist]: [...current[selected_watchlist], [ticker_name]]};
        });
        data_request(null,'watchlist',ticker_name,selected_watchlist,false)
        ticker_name = ''
    }

    // Get the keys (watchlist names) from watchlist_data store
    $: watchlist_keys = Object.keys($watchlist_data);
</script>

<div class="popout-menu" class:visible={visible}>
    {#if visible}
        <div>
        <select bind:value={selected_watchlist} on:change={selectWatchlist}>
            <option disabled selected value="">Select a watchlist</option>
            {#each watchlist_keys as key}
                <option value={key}>{key}</option>
            {/each}
        </select>
        <input type="text" placeholder="Name" bind:value={watchlist_name} />
        <button on:click={() => create_watchlist()}> Create New </button>
        </div>
        <div>
            <input type="text" placeholder="Ticker" bind:value={ticker_name} />
            <button on:click={() => add_ticker()}> Add Ticker </button>
        </div>
        {#if selected_watchlist}
            <Table 
                headers={['Ticker']} 
                rows={$watchlist_data[selected_watchlist]}
                onRowClick={data_request}
                clickHandlerArgs={[chart_data,'chart','Ticker']} />
        {/if}
    {/if}
</div>

<style>
    @import './style.css';
</style>
