import { bind } from 'svelte/internal';
import { writable } from 'svelte/store';

export let screener_data = writable()

export let chart_data = writable([])

export let match_data = writable([[], [], []])

export let auth_data = writable(null)

export async function data_request(func, ...args) {
    const url = `http://localhost:5057/data`;
    const payload = {
        function: func,
        arguments: args
    };

    try {
        console.log('Request sent to:', url);

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload) // Send the payload as a stringified JSON in the body
        });

        if (!response.ok) {
            throw new Error('POST response not ok');
        }
        let result = response.json();
            return result
        //    try {
        //        result = JSON.parse(result); // Attempt to parse if result is a stringified JSON
        //    } catch {
        //        // Result might already be in a proper JSON format or another parsing error occurred
        //}
        return result
        
    }
    catch{

    }
}


export async function backend_request(bind_variable, func, ...args) {
    const url = `http://localhost:5057/backend`;
    const payload = {
        function: func,
        arguments: args
    };

    try {
        console.log('Request sent to:', url);

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload) // Send the payload as a stringified JSON in the body
        });

        if (!response.ok) {
            throw new Error('POST response not ok');
        }

        const responseData = await response.json();
        const task_id = responseData.task_id;
        const checkStatus = async () => {
            const statusResponse = await fetch(`http://localhost:5057/poll/${task_id}`);
            if (!statusResponse.ok) {
                throw new Error('GET response not ok');
            }

            const statusData = await statusResponse.json();
            if (statusData.status === 'done') {
                clearInterval(intervalId);
                console.log(statusData.result);
                let result = statusData.result;
                try {
                    result = JSON.parse(result); // Attempt to parse if result is a stringified JSON
                } catch {
                    // Result might already be in a proper JSON format or another parsing error occurred
                }
                bind_variable.set(result);
            } else if (statusData.status === 'failed') {
                clearInterval(intervalId);
                bind_variable.set('failed');
            }
        };

        const intervalId = setInterval(checkStatus, 200); // Check every .2 seconds
    } catch (error) {
        console.error('Error during backend request:', error);
        bind_variable.set(null);
    }
}

//export async function backend_request(bind_variable, func, ...args) {
//    const query = `${func}_${args.join('_')}`
//    const url = `http://localhost:5057/backend/${query}`;
//    try {
//        console.log('request sent', url)
//        const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, });
//        if (!response.ok) {throw new Error('POST response not ok') }
//        const responseData = await response.json();
//        const task_id = responseData.task_id;
//        const checkStatus = async () => {
//            const response = await fetch(`http://localhost:5057/poll/${task_id}`);
//            if (!response.ok) { throw new Error('GET response not ok') }
//            const responseData = await response.json();
//            const status = responseData.status
//            if (responseData.status === 'done') {
//                clearInterval(intervalId);
//                console.log(responseData.result);
//                let result = await responseData.result
//                try { result =  await JSON.parse(result) }
//                catch { }
//                bind_variable.set(result);
//            } else if (status === 'failed') {
//                clearInterval(intervalId);
//                bind_variable.set('failed')
//            }
//        };
//        const intervalId = setInterval(checkStatus, 200); // Check every .2 seconds
//    } catch {
//        bind_variable.set(null);
//    }
//}




