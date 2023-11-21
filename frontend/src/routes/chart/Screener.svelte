<script>
    let innerWidth; 
    let innerHeight
    export let visible = false;
    import {screener_data, backend_request, chart_data} from '../store.js';
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
@import './style.css';
</style>



