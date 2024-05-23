<!-- app/+page.svelte -->
<script>
    import Annotate from './annotate.svelte'
    import Screener from './screener.svelte'
    import Journal from './journal.svelte'
    import Chart from './chart.svelte'
    import Trainer from './trainer.svelte'
    import {auth_data,menuLeftPos} from '../../store.js'
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';
    import { get } from 'svelte/store';
    let active_menu = '';
    let min, max, close, pix, thresh;

    $: if ($auth_data == null && browser) {
        goto('/login');
    }
    $: {
        if (browser) {
            pix = window.innerWidth;
            min = pix * 0.3;
            max = pix * 0.85;
            close = pix * 0.95;
            thresh = close;
        } 
    }
    function toggle_menu(menuName) {
        if (active_menu == menuName) {
            active_menu = ''; 
            menuLeftPos.set(close);
        } else {
            active_menu = menuName;
            if (get(menuLeftPos) > max) {
                menuLeftPos.set(max);
            }
        }
    }
    let resizing = false;
    function startResize(event) {
        event.preventDefault();  
        resizing = true;
        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResize);
    }
    function resize(event) {
        if (resizing) {
            let l = event.clientX;
            console.log(thresh);
            console.log("d",event.clientX)
            /*if (event.clientX > thresh) {
                l = close;
                active_menu = '';
            }*/
            //else 
            if (event.clientX > max) {
                l = max;
            }
            else if (event.clientX < min) {
                l = min;
            }
            menuLeftPos.set(l);
        }
    }
    function stopResize(event) {
        if (resizing) {
            document.removeEventListener('mousemove', resize);
            document.removeEventListener('mouseup', stopResize);
            resizing = false;
        }
    }

</script>

<div class="page">
    <div  class="container">
        <Chart/>
        <div on:mousedown={startResize} class="resize-handle"></div>
        <div class="menu-container" style="left: {$menuLeftPos}px">
            {#if active_menu == 'annotate'}
                <Annotate/>
            {:else if active_menu == 'screener'}
                <Screener/>
            {:else if active_menu == 'journal'}
                <Journal/>
            {:else if active_menu == 'trainer'}
                <Trainer/>
            {/if}

        </div>
    </div>
    <div class="button-container">
        <button class="button {active_menu == 'annotate' ? 'active' : ''}" on:click={() =>toggle_menu('annotate')}>
            <im class="icon" src="/annotate.png" alt="" />
        </button>
        <button class="button {active_menu == 'screener' ? 'active' : ''}" on:click={() =>toggle_menu('screener')}>
            <img class="icon" src="/screener.png" alt="" />
        </button>
        <button class="button {active_menu == 'journal' ? 'active' : ''}" on:click={() =>toggle_menu('journal')}>
            <img class="icon" src="/journal.png" alt="" />
        </button>
        <button class="button {active_menu == 'trainer' ? 'active' : ''}" on:click={() =>toggle_menu('trainer')}>
            <img class="icon" src="/trainer.png" alt="" />
        </button>
    </div>
</div>


<style>
    @import "../../global.css";
    .container {
        display: flex;
        width: 96vw;
        height: 100%;
        flex-direction: row;
        flex-grow: 1;
        position: relative;
        overflow: visible;
    }
    .menu-container,  .button-container, .resize-handle {
        height: 100%;
        overflow: hidden;
    }
    .menu-container {
        background-color: var(--c2);
        z-index: 1;
        flex-direction: column;
    }
    .resize-handle {
        width: 1vw;
        cursor: ew-resize;
        background-color: var(--c2);
        z-index: 2;
    }
    .resize-handle:hover {
        background-color: var(--c4);
    }
    .button-container {
        align-items: center;
        width: 4vw;
        height: 100%;
        top: 0;
        right: 0;
        z-index: 3;
        background-color: var(--c1);
        flex-direction: column;
        justify-content: start;
        position: absolute;
    }
    .button.active {
        border-left-color: transparent;
        background-color: var(--c2);
    }
    .button {
        width: 4vw;
        height: 4vw;
        background-color: var(--c1);
        border: none; 
        padding: 0; 
        cursor: pointer;
        border-radius: 0; 
        font-size: 1.5vw;
        transition: background-color 0.1s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .button:hover{
        background-color: var(--c2); 
    }
    .icon {
        width: 60%;
        height: 60%;
    }
</style>
