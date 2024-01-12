
<script>
    import { chart_data,  backend_request, match_data} from '../store.js';
    export let visible = false;
    let innerHeight
</script>




<div class="popout-menu"  style="min-height: {innerHeight}px;" class:visible={visible}>
    {#if visible}

        <p>account<p/>
    {/if}
</div>

<style>
@import './style.css';
</style>