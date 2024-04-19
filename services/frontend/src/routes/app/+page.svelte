<!-- app/+page.svelte -->
<script>
    import Annotate from './annotate.svelte'
    import Screener from './screener.svelte'
    import Journal from './journal.svelte'
    import Chart from './chart.svelte'
    import Trainer from './trainer.svelte'
    import {auth_data,sidebarWidth} from '../../store.js'
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';
    import { get } from 'svelte/store';
    let active_menu = '';

    function toggle_menu(menuName) {
        if (active_menu == menuName) {
            active_menu = ''; 
            sidebarWidth.set(0);
        } else {
            active_menu = menuName;
            if (get(sidebarWidth) < 15) {
                sidebarWidth.set(15);
            }
        }
    }

    $: if ($auth_data == null && browser) {
        goto('/login');
    }
    let resizing = false;
    function startResize(event) {
        event.preventDefault();  // Prevent other interactions like text selection
        resizing = true;
        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResize);
    }

    function resize(event) {
        if (resizing) {
            const d = Math.max(15, Math.min(40, 95 - (event.clientX / window.innerWidth) * 100));
            sidebarWidth.set(d);
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
    <div class="menu-container" style="width: {$sidebarWidth}vw">
        {#if active_menu == 'annotate'}
            <Annotate/>
        {/if}
        {#if active_menu == 'screener'}
            <Screener/>
        {/if}
        {#if active_menu == 'journal'}
            <Journal/>
        {/if}
        {#if active_menu == 'trainer'}
            <Trainer/>
        {/if}
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
</div>


<style>
    @import "../../global.css";
    .page {
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        position: absolute;
        background-color: var(--c1);
        overflow: hidden;
    }
    .container {
        display: flex;
        width: 100%;
        height: 100%;
        flex-direction: row;
    }
    .menu-container,  .button-container, .resize-handle {
        height: 100vh;
        overflow: hidden;
    }
    .menu-container {
        background-color: var(--c2);
        z-index: 1;
        flex-direction: column;
    }
    .resize-handle {
        width: 1%;
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
        background-color: var(--c1);
        flex-direction: column;
        justify-content: start;
    }
    .button.active {
        border-left-color: transparent;
        background-color: var(--c2);
    }
    .button {
        width: 4vw; /* Width of the button */
        height: 4vw; /* Height of the button, equal to the width to make it square */
        background-color: var(--c1); /* Blue color, consistent with theme */
        border: none; /* Remove border */
        padding: 0; /* No padding needed, as width and height are fixed */
        cursor: pointer;
        border-radius: 0; /* Adjust as needed */
        font-size: 1.5vw; /* Adjust font size to fit inside the button */
        transition: background-color 0.1s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .button:hover{
        background-color: var(--c2); /* Darker shade for hover effect */
    }
    .icon {
        width: 60%;
        height: 60%;
    }
</style>
