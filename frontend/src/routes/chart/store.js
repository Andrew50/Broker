import { writable } from 'svelte/store';

//export let screener_data;
export let screener_data = writable()
//screener_data_store.subscribe((value) => {screener_data = value});

//export let chart_data;
export let chart_data = writable([])
//chart_data_store.subscribe((value) => { chart_data = try_parse(value)});

export let match_data = writable([[],[],[]])
//export let match_data = [];
//match_data_store.subscribe((value) => {match_data = try_parse(value)});

//function try_parse(value) {
//    try { return JSON.parse(value) }
//    catch { return value }
//}
export async function backend_request(bind_variable, func, ...args) {
    //if (!args) {

    //    event.preventDefault(); // Prevent the default form submission
    //    const formData = new FormData(event.target);
    //    args = Array.from(formData.values()).join('_');
    //}
    //if (func) {
    //    args = `${func}_${args}`;
    //}

    const query = `${func}_${args.join('_')}`
    console.log(func)
    console.log(args)
    const url = `http://localhost:5057/fetch/${query}`;
    try {
        console.log('request sent', url)
        const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, });
        if (!response.ok) {throw new Error('POST response not ok') }
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
                let result = await responseData.result
                try { result =  await JSON.parse(result) }
                catch { }
                bind_variable.set(result);
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



