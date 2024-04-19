<script>
    import { journalData } from '../../store.js';
    import List from '../../tables/list.svelte';
</script>

<List headers={['Date']} data={journalData} func='Journal' useDelete={false}/>

<style>
    @import "../../global.css";
</style>
