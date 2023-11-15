<script>
    import Match from './Match.svelte'
    import Screener from './Screener.svelte'
    import Chart from './Chart.svelte'

    let match_visibility = false;
    let screener_visibility = false;

    function toggle_match() {
    match_visibility = !match_visibility;
    screener_visibility = false; 
    }
    function toggle_screener() {
    screener_visibility = !screener_visibility;
    match_visibility = false; 
    }
</script>

<div class="button-container">
    <button class="match-button" on:click={toggle_match}>
        <div>M</div>
        <div>A</div>
        <div>T</div>
        <div>C</div>
        <div>H</div>
    </button>
    <button class="screener-button" on:click={toggle_screener}>
        <div>S</div>
        <div>C</div>
        <div>R</div>
        <div>E</div>
        <div>E</div>
        <div>N</div>
        <div>E</div>
        <div>R</div>
    </button>
</div>

<Match visible={match_visibility} />
<Screener visible={screener_visibility} />
<Chart/>

<style>
    .match-button {
    position: fixed;
    right: 20px;
    top: 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    }
    .screener-button {
    position: fixed;
    right: 20px;
    top: 120px;
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    }
</style>
