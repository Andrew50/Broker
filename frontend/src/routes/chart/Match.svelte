<script>
    import { chart_data,  backend_request, match_data} from './store.js';
    let ticker = 'JBL'
    let tf = '1d' 
    let dt = '2023-10-03'
    export let visible = false;
    let innerWidth; 
    let innerHeight
</script>

<div class="popout-menu"  style="min-height: {innerHeight}px;" class:visible={visible}>
    {#if visible}
        <form on:submit|preventDefault={() => backend_request(match_data,'Match-get',ticker,tf,dt)}>
            <div class="form-group">
                <input type="text" id="ticker" bind:value="{ticker}" name="ticker" placeholder="Enter Ticker" required>
            </div>
            <div class="form-group">
                <input type="text" id="tf" bind:value="{tf}" name="tf" placeholder="Enter TF" required>
            </div>
            <div class="form-group">
                <input type="text" id="dt" bind:value="{dt}" name="dt" placeholder="Enter Date Time">
            </div>
            <div class="form-group">
                <input type="submit" value="FETCH">
            </div>
        </form>
        {#if $match_data.length > 0}
            <table>
                <thead>
                    <tr>
                        <th>Ticker Symbol</th>
                        <th>Timestamp</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    {#each $match_data as item}
                         <tr on:click={() => backend_request(chart_data,'Chart-get',item[0],item[1],'1d')}><!--will have to get fixed at some point[' -->
                            <td>{item[0]}</td> <!-- Ticker Symbol -->
                            <td>{item[1]}</td> <!-- Timestamp -->
                            <td>{item[2]}</td> <!-- Value -->
                        </tr>
                    {/each}
                </tbody>
            </table>
        {/if}




    {/if}
</div>

<style>
    .popout-menu {
    display: none;
    position: fixed;
    right: 70px;
    top: 0;
    background-color: #f9f9f9;
    min-width: 3px;
    box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
    }
    .popout-menu.visible {
    display: block;
    }
</style>




    