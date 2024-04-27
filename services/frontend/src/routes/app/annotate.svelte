<script>
    import {annotateData} from "../../store.js";
    export let visible = false;
    import List from "../../tables/list.svelte";
</script>

<List 
    headers = {["Date","Ticker","Setup"]}
    data = {annotateData}
    func = "Annotation"
    useDelete = {true}
/>
        

<style>
    @import "../../global.css";
</style>

