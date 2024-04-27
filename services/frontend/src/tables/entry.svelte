<script>
  import { onMount } from 'svelte';
  if (import.meta.env.SSR) {
    // Server side
} else {
    // Client side
    import('quill').then(Quill => {
        // Use Quill
    });
}
  import { currentEntry, chartQuery } from '../store.js';
  import { browser } from '$app/environment';
  import 'quill/dist/quill.snow.css';

  let editorContainer;

    onMount(() => {
        if (browser) {
            const editor = new Quill(editorContainer, {
            theme: 'snow',
            modules: {
                toolbar: false // Explicitly disable the toolbar
            }
        });
    
        currentEntry.subscribe(value => {
          if (editor.getText() !== value) {
            editor.setText(value); 
          }
        });



    editor.on('text-change', (delta, oldDelta, source) => {
      if (source === 'user' || source === 'api') {
        let text = editor.getText();
        if (source === 'user') {
            currentEntry.set(text); 
        }

        delta.ops.forEach(op => {
          if (typeof op.insert === 'string') {
            const regex = /\[([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\]]+)\]/g;
            let match;
            while ((match = regex.exec(op.insert)) !== null) {
              const [_, ticker, interval, t, pm] = match;
              const index = match.index;
              editor.deleteText(index, match[0].length);
              editor.insertEmbed(index, 'chart', { ticker, interval, t, pm });
            }
          }
        });
      }
    });

    class ChartBlot extends Quill.import('blots/embed') {
      static create(value) {
        let node = super.create();
        node.setAttribute('type', 'button');
        node.className = 'btn';
        node.textContent = `${value.ticker}`; 
        node.onclick = () => chartQuery.set([value.ticker, value.interval, value.t, value.pm]);
        return node;
      }

      static value(node) {
        return {
          ticker: node.dataset.ticker,
          interval: node.dataset.interval,
          t: node.dataset.t,
          pm: node.dataset.pm
        };
      }
    }
    ChartBlot.blotName = 'chart';
    ChartBlot.tagName = 'button';
    Quill.register('formats/chart', ChartBlot);
    }
  });
 
</script>

<div bind:this={editorContainer}></div>

<style>
  .ql-container {
    /*height: 200px;*/
    max-height: 75%;
    width: 100%;
    height: auto;
    overflow-y: auto;
    border: none;
  }
  :global(.btn) {
    background-color: #f1f1f1;
    border: 1px solid #ccc;
    border-radius: 4px;
    color: #333;
    cursor: pointer;
    display: inline-block;
    font-size: 14px;
    margin: 5px;
    padding: 5px 10px;
    text-align: center;
  }
</style>

