import { writable } from 'svelte/store';

export let screener_data = writable()

export let chart_data = writable([])

export let match_data = writable([[],[],[]])

export async function data_request
export async function backend_request(bind_variable, func, ...args) {
    const query = `${func}_${args.join('_')}`
    const url = `http://localhost:5057/backend/${query}`;
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
        const intervalId = setInterval(checkStatus, 200); // Check every .2 seconds
    } catch {
        bind_variable.set(null);
    }
}




