export let match_data_store = writable([])
export let match_data = [];
match_data_store.subscribe((value) => {
    match_data = value
});

import { writable } from 'svelte/store';
import { onMount } from 'svelte';

let screener_data_store = writable()
let screener_data;
screener_data_store.subscribe((value) => {
    screener_data = value
});




export let chart_data_store = writable([
    { time: '2018-10-19', open: 180.34, high: 180.99, low: 178.57, close: 179.85 }
]);


export let chart_data;




chart_data_store.subscribe((value) => {
    console.log(value)
    try { chart_data = JSON.parse(value) }
    catch { chart_data = value }
});


async function startTask(bind_variable, func = false, args = false) {
    if (!args) {

        event.preventDefault(); // Prevent the default form submission
        const formData = new FormData(event.target);
        args = Array.from(formData.values()).join('_');
    }
    if (func) {
        args = `${func}_${args}`;
    }
    const url = `http://localhost:5057/fetch/${args}`;
    try {
        console.log('request sent', url)
        const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, });
        if (!response.ok) { throw new Error('POST response not ok') }
        const responseData = await response.json();
        const task_id = responseData.task_id;
        const checkStatus = async () => {
            const response = await fetch(`http://localhost:5057/poll/${task_id}`);
            if (!response.ok) { throw new Error('GET response not ok') }
            const responseData = await response.json();
            const status = responseData.status
            if (responseData.status === 'done') {
                clearInterval(intervalId);
                console.log(responseData.result);

                bind_variable.set(responseData.result);
            } else if (status === 'failed') {
                clearInterval(intervalId);
                bind_variable.set('failed')
            }
        };
        const intervalId = setInterval(checkStatus, 200); // Check every 2 seconds
    } catch {
        bind_variable.set(null);
    }
}




