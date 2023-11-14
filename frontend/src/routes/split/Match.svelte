.match-button {
    position: fixed;
    right: 20px;
    top: 20px; /* You can adjust the top position as needed */
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    }





    <div class="popout-menu"  style="min-height: {innerHeight}px;" class:visible={isMatch}>
      {#if isMatch}
                    <form on:submit|preventDefault={() => startTask(match_data_store,'Match-get')}>
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
                    {#if match_data.length > 0}
                    <table>
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Name</th>
                        </tr>
                      </thead>
                      <tbody>
                        {#each match_data as item}
                          <tr>
                            <td>{item.id}</td>
                            <td>{item.name}</td>
                          </tr>
                        {/each}
                      </tbody>
                    </table>
                    {/if}
      {/if}
    </div>