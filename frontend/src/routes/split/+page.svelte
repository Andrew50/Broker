<script>

    let innerWidth;
    let innerHeight;
    let isMatch = false;
    let isScreener = false;

   

    function toggleMatch() {
    isMatch = !isMatch;
    isScreener = false; 
    }
    function toggleScreener() {
    isScreener = !isScreener;
    isMatch = false; 
    }
    
</script>



<style>
    
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

<!-- <div class="container"> -->
<div class="button-container">
    <button class="match-button" on:click={toggleMatch}>
        <div>M</div>
        <div>A</div>
        <div>T</div>
        <div>C</div>
        <div>H</div>
    </button>
    <button class="screener-button" on:click={toggleScreener}>
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

{chartTicker}
<a href="/test">test</a>


