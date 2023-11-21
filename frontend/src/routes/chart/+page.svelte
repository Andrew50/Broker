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
    <button class="button match-button" on:click={toggle_match}>
        <div>M</div>
        <div>A</div>
        <div>T</div>
        <div>C</div>
        <div>H</div>
    </button>
    <button class="button screener-button" on:click={toggle_screener}>
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
    .button-container {
        position: fixed;
        right: 20px;
        top: 20px;
    }

    .button {
        background-color: #007bff; /* Blue color, consistent with theme */
        color: white;
        border: none;
        padding: 10px 20px;
        margin-bottom: 10px;
        cursor: pointer;
        border-radius: 5px;
        font-size: 16px;
        transition: background-color 0.3s;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .button:hover {
        background-color: #0056b3; /* Darker shade for hover effect */
    }

    .match-button {
        /* Additional styling specific to match button if needed */
    }

    .screener-button {
        /* Additional styling specific to screener button if needed */
    }
</style>
