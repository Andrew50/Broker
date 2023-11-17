<script>
    let innerWidth; 
    let innerHeight
    export let visible = false;
    import {screener_data, backend_request, chart_data} from './store.js';
</script>

<div class="popout-menu"  style="min-height: {innerHeight}px;" class:visible={visible}>

    {#if visible}
        <form on:submit|preventDefault={() => backend_request(screener_data,'Screener-get')}>
                    
        <div class="form-group">
        <input type="submit" value="Screen">
        </div>
        </form>
    {/if}
    
</div>


<style>
    /* .screener-button {
    position: fixed;
    right: 20px;
    top: 120px;  You can adjust the top position as needed 
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    } */
    .popout-menu {
    display: none;
    position: fixed;
    right: 70px; /* Offset from the right side */
    top: 0; /* You can adjust the top position as needed */
    background-color: #f9f9f9;
    min-width: 3px;
    box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
    }
    .popout-menu.visible {
    display: block;
    }

</style>



