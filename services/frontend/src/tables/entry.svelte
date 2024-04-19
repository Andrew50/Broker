<script>
    import { writable } from 'svelte/store';
    import { currentEntry } from '../store.js';

    let editor; // Reference to the contenteditable div
    let content = writable(""); // Store to hold the raw text

    // Function to update the content within the contenteditable div
    function updateContent(inputText) {
        const regex = /\[(.*?)\|(.*?)\|(.*?)\]/g;
        const innerHTML = inputText.replace(regex, (match, ticker, time, interval) => {
            return `<button class='dynamic-button' onclick='runFunction("${ticker}", "${time}", "${interval}")'>${ticker}</button>`;
        });
        content.set(innerHTML); // Store the formatted HTML
    }

    // Subscribe to currentEntry for changes
    //$: $currentEntry, updateContent($currentEntry);

    // Function to insert a match and update the entry
    function insertMatch(matchString) {
        let currentText = editor.innerText;
        let selection = document.getSelection();
        if (!selection.rangeCount) return;

        let range = selection.getRangeAt(0);
        range.deleteContents();
        range.insertNode(document.createTextNode(matchString));

        currentEntry.set(editor.innerText); // Update the entry with new text
        updateContent(editor.innerText); // Re-parse and update the content

        setTimeout(() => {
            editor.focus(); // Refocus the editor
            const pos = range.endOffset;
            setCaretPosition(pos); // Restore caret position
        }, 0);
    }

    // Set caret position function
    function setCaretPosition(pos) {
        const setPos = document.createRange();
        const set = window.getSelection();
        setPos.selectNodeContents(editor);
        setPos.setStart(editor.childNodes[0], pos);
        setPos.collapse(true);
        set.removeAllRanges();
        set.addRange(setPos);
    }

    // Function to log button actions
    function runFunction(ticker, time, interval) {
        console.log(`Ticker: ${ticker}, Time: ${time}, Interval: ${interval}`);
    }
    window.runFunction = runFunction; // Make function globally accessible
</script>

<div contenteditable="true" class="editable"/>


<style>
    .editable {
        min-height: 50px;
        padding: 10px;
        overflow: auto;
        max-width: 100%;
        text-align: left;
        direction: ltr;
        vertical-align: top;
        white-space: normal;
        word-wrap: break-word;

    }
    .editable:focus {
        outline: none;
    }
    .dynamic-button {
        padding: 2px 5px;
        margin: 0 2px;
        cursor: pointer;
    }
</style>

