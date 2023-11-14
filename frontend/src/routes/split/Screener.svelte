 

<div class="popout-menu"  style="min-height: {innerHeight}px;" class:visible={visible}>

    {#if visible}
        <form on:submit|preventDefault={() => startTask(screener_data_store,'Screener-get')}>
                    
        <div class="form-group">
        <input type="submit" value="Screen">
        </div>
        </form>
         <div>
         this is the letter {key}   
         </div>
         
    {/if}
    
</div>


<style>
    .screener-button {
    position: fixed;
    right: 20px;
    top: 120px; /* You can adjust the top position as needed */
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    }

</style>

<script>
    export let visible = false;
    import {match_data_store, screener_data_store, fetch} from './store.js';
</script>

