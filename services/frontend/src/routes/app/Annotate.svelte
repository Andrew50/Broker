<script>
    import {annotations} from "../../store.js";
    export let visible = false;
    import List from "./list.svelte";
    let innerHeight;
</script>

<div class="popout-menu" style="min-height: {innerHeight}px;" class:visible>
    {#if visible}
        <List 
            headers = {["Date","Ticker","Setup"]}
            data = {annotations}
            func = "Annotation"
            useDelete = {true}
            visible = {visible}
        />
        
    {/if}
</div>

<style>
    @import "./style.css";
</style>
