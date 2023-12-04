
<script>
    import { chart_data, data_request,setups_list} from '../store.js';
    export let visible = false;
    let innerHeight
    import { get } from 'svelte/store';

    let selected_st = get(setups_list)[0][0]
    function change_st(){
        annotation = ''
    }

    let annotation;
    let current_instance = writable();



    function next(){

        data_request(current_instance,'study',annotation,...get(current_instance))

        annotation = ''
    }



</script>

<div class="popout-menu"  style="min-height: {innerHeight}px;" class:visible={visible}>
    {#if visible}

        <div>
        <select bind:value={selected_st} on:change={change_st}>
            <option disabled selected value="">Select a watchlist</option>
            {#each $setups_list as key}
                <option value={key[0]}>{key[0]}</option>
            {/each}
        </select>
        <div>
        <textarea bind:value={annotation} class="large-textarea" placeholder="Enter text here"></textarea>
        </div>
        <div>
        <button on:click={next}>Next</button>
       </div>
        </div>
    {/if}
</div>


<style>
@import './style.css';
.large-textarea {
        width: 100%; /* Full width */
        height: 200px; /* Starting height, can be adjusted */
        padding: 10px; /* Padding for text area */
        font-size: 1em; /* Font size */
        /* Additional styling as needed */
        box-sizing: border-box; /* Include padding and border in the element's total width and height */
        resize: vertical; /* Allow vertical resizing, remove this line if resizing is not needed */
    }
</style>