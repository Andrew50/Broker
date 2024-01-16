<script>
    import { chart_data, private_request, match_data } from "../store.js";
    export let visible = false;
    let innerHeight;
</script>

<div class="popout-menu" style="min-height: {innerHeight}px;" class:visible>
    {#if visible}
        <p>settings</p>
        <p />
    {/if}
</div>

<style>
    @import "./style.css";
</style>
