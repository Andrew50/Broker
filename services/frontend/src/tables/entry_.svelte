<script>

    import { writable } from 'svelte/store';
    import { currentEntry } from '../store.js';
    let parsedItems = writable([]);

    function autoResize(node) {
        // Resize function
        const resize = () => {
            node.style.height = 'auto';
            node.style.height = `${node.scrollHeight}px`;
        };

        // Initial resize
        resize();

        // Subscribe to changes in currentEntry and resize
        const unsubscribe = currentEntry.subscribe(_ => {
            // Ensure changes are reflected in the DOM
            requestAnimationFrame(() => {
                resize();
            });
        });

        return {
            destroy() {
                unsubscribe(); // Clean up the subscription
            }
        };
    }

    // Subscribe to currentEntry and call autoResize after the DOM updates
    $: if ($currentEntry) {
        parseText($currentEntry);
    }

    function parseText(inputText) {
        const regex = /\[(.*?)\|(.*?)\|(.*?)\]/g;
        let items = [];
        let match;
        while ((match = regex.exec(inputText)) !== null) {
            items.push({
                ticker: match[1],
                time: match[2],
                interval: match[3]
            });
        }

        parsedItems.set(items);
    }

</script>

{#each $parsedItems as item}
    <button on:click={() => {console.log(item)}}>
        {item.ticker}
    </button>
{/each}


<textarea use:autoResize bind:value={$currentEntry} placeholder="Type here..." rows="1"></textarea>

<style>

    textarea {
        width: 100%;
        min-height: 50px;
        background: var(--c2); /* Dark grey for textarea */
        color: var(--f1);
        border: none;
        resize: none;
        overflow: hidden;
        box-sizing: border-box;
        line-height: 1.2;
        padding: 10px; /* Smaller padding for textarea */
    }
    textarea:focus {
        outline: none;
    }
    button {
        margin: 5px;
        padding: 5px 10px;
    }
</style>
