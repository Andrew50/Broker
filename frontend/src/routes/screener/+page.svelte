<div class ="index">
    <body>
        <a href="/">Home</a>
        <h1>Match</h1>
        <form on:submit={fetchData}>
            <label for="ticker">Ticker:</label>
            <input type="text" id="ticker" bind:value ={ticker} name="ticker" placeholder="Enter Ticker" required><br><br>
            <label for="datetime">Datetime:</label>
            <input type="text" bind:value ={dt} id="datetime" name="datetime" required><br><br>
            <label for="timeframe">Timeframe:</label>
            <input type="text" id="timeframe" bind:value ={tf} name="timeframe" placeholder="Enter Timeframe" required><br><br>
            <input type="submit" value="Submit">
        </form>
    </body>
    <div


<script>

</script>


<style></style>