<script>
    import {request,annotations,autoLoad,currentEntry,toDT} from "../../store.js";
    export let visible = false;
    let visibleAnnotationID = null;
    let innerHeight;
    let stop = () => {};
    $: if (visible ){
        stop = autoLoad(annotations,50,'getAnnotations',[],() =>
        {
            //get current table location
            const table = document.querySelector('.annotation-list');
            let current = 0;
            if (table != null){
                const rows = table.querySelectorAll('#annotation tr');
                if (rows.length > 0){
                    const scrollPos = table.scrollTop;
                    const row_height = rows[rows.length -1].offsetHeight;
                    current = Math.floor(scrollPos / row_height);
                }
            }
            return current;
        });
    }
    else{
        stop();
    }

    function saveAnnotation(i){
        const entry = $currentEntry;
        if (entry != ""){
            const id = $annotations[i][4];
            annotations.update((a) => {
                a[i][3] = true;
                return a;
            });
            request(null,true,'setAnnotation',id,entry);
        }

    }
    function handleRowClick(annotation, i){
        currentEntry.set('');
        if(visibleAnnotationID == annotation[4]){
            visibleAnnotationID = null;
        }else{
            visibleAnnotationID = annotation[4];
            if(annotation[3]){
                currentEntry.set(null);
                request(currentEntry,true,'getAnnotationEntry',annotation[4]);
            }
        }
    }
    function deleteAnnotation(i){
        request(null,true,'delAnnotation',$annotations[i][4]);
        annotations.update((a) => {a.splice(i,1);return a;});
    }
</script>

<div class="popout-menu" style="min-height: {innerHeight}px;" class:visible>
    {#if visible}
        <div class="annotation-list">
            <table id="annotation">
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Date</th>
                        <th>Setup</th>
                    </tr>
                </thead>
                {#if $annotations.length}
                    <tbody>
                        {#each $annotations as annotation, i}
                            <tr class:clean-green={!annotation[3]} on:click={() => handleRowClick(annotation, i)}>
                                <td>{annotation[1]}</td> <!-- Ticker -->
                                <td>{toDT(annotation[0])}</td> <!-- Date -->
                                <td>{annotation[2]}</td> <!-- Setup -->
                          </tr>
                          {#if visibleAnnotationID == annotation[4]}
                            <tr class="text-entry">
                              <td colspan="3">
                                <textarea bind:value={$currentEntry} placeholder="Type here..." rows="1"></textarea>
                                <div class="button-row">
                                  <button on:click|stopPropagation={() => saveAnnotation(i)}>Save</button>
                                  <button on:click|stopPropagation={() => deleteAnnotation(i)}>Delete</button>
                                </div>
                              </td>
                            </tr>
                          {/if}
                        {/each}
                    </tbody>
                {/if}
            </table>
        </div>
    {/if}
</div>

<style>
    @import "./style.css";
    .popout-menu {
        /* Styles for your popout menu */
    }

    .annotation-list {
        overflow-y: auto;
        height: 100%;
        font-family: 'Arial', sans-serif; /* Match the font to your screenshot */
    }

    table {
        width: 100%;
        border-collapse: collapse; /* Removes space between buttons */
        background: #1a1a1a; /* Dark theme background */
        color: white; /* Text color */
    }

    table thead tr th {
        background: #000; /* Header background */
        color: #fff;
    }

        /* Style for individual table rows */
#annotation tbody tr {
            margin: 0; /* Remove default margin */
        }

        /* Style for buttons to fill the width and resemble table rows */
#annotation tbody tr button {
            width: 100%;
            display: block;
            text-align: left;
            background-color: #333; /* Button background */
            border: none;
            color: white; /* Button text color */
            padding: 10px; /* Adjust the padding to match your screenshot */
            border-bottom: 1px solid #222; /* Line between buttons */
        }

        /* Active/hover state for buttons */
#annotation tbody tr button:hover,
#annotation tbody tr button:focus {
            background-color: #555;
        }

        /* Styling for the text input */
#annotation input[type="text"] {
            width: calc(100% - 20px); /* Adjust width to account for padding */
            margin: 0;
            padding: 10px;
            border: none;
            background: #222; /* Match to the theme */
            color: white; /* Match to the theme */
        }

        /* Styling for the save/delete buttons */
#annotation tbody tr button {
            background: #444; /* Differentiate from row buttons */
            color: #fff;
            padding: 10px;
            border: none;
            cursor: pointer;
        }

    #annotation tbody tr button-row {
        display: flex;
        justify-content: space-around;
        padding: 5px;
        background: #222; /* Match to the theme of the text entry */
    }

    /* Style individual buttons within the button row */
#annotation tbody tr button-row button {
        flex: 1 1 auto;
        margin: 2px; /* Provides space around buttons */
        padding: 5px 10px; /* Smaller padding */
    }

    /* Adjust the input style */
#annotation input[type="text"] {
        width: 100%; /* Full width */
        box-sizing: border-box; /* Border included in width */
        padding: 8px; /* Adjust as needed */
        margin-bottom: 4px; /* Space between input and buttons */
    }

    /* Set the normal and green row colors */
#annotation tbody tr {
        color: white; /* Default color */
        background: #333; /* Default background */
    }

#annotation tbody tr.clean-green {
        color: white; /* Text color for clean green */
        background: #00A86B; /* A clean green background */
    }

        /* Resize text entry based on text size */
#annotation input[type="text"] {
            font-size: 16px; /* Adjust as needed for your design */
        }

        /* Modify placeholder color if needed */
#annotation input::placeholder {
            color: #666;
        }

        /* Reset appearance of the input to remove browser defaults */
#annotation input[type="text"] {
            background: transparent;
            border: none;
            border-bottom: 1px solid grey; /* If you want an underline effect */
        }

        /* Style for input when it is focused */
#annotation input[type="text"]:focus {
            outline: none;
            border-bottom-color: white; /* Change color when focused */
        }

/* Other existing styles... */

/* Style for text entry and button row */
.text-entry td {
  padding: 0; /* Remove padding to allow input and button to fit well */
  background: #222; /* Background for the input and buttons */
}

.text-entry input[type="text"] {
  width: calc(100% - 10px); /* Full width minus padding */
  padding: 5px;
  margin: 5px;
  border: none;
  outline: none;
  color: white;
  background: #333;
}

.text-entry .button-row {
  display: flex;
  justify-content: center;
  gap: 10px; /* Space between buttons */
  padding: 5px;
  margin: 5px;
}

.text-entry .button-row button {
  padding: 5px 15px; /* Smaller padding */
  background: #444;
  color: #fff;
  border: none;
  cursor: pointer;
}

/* Add a line between each row */
#annotation tr:not(:last-child) {
  border-bottom: 1px solid grey;
}

/* Add specific style for clean-green class */
.clean-green {
  background-color: #00A86B; /* Clean green background color */
  color: white; /* Color for clean green */
}

</style>
