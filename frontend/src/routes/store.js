import { bind } from 'svelte/internal';
import { writable } from 'svelte/store';
import { get } from 'svelte/store';

export let screener_data = writable([])

export let chart_data = writable([])

export let match_data = writable([[], [], []])

export let auth_data = writable(null)

export let setups_list = writable([])

export let settings = writable({})


function logout() {
    auth_data.set(null);
    goto('/auth');
}

function getAuthHeaders() {
    const token = get(auth_data);
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}


export async function public_request(bind_variable, func, ...args) {
    const url = `http://localhost:5057/public`;
    const payload = {
        function: func,
        arguments: args
    };

    try {
        console.log('Request sent to:', url);
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload) // Send the payload as a stringified JSON in the body
        });

        if (!response.ok) {
            throw new Error('POST response not ok');
        }
        let result = await response.json();
        try {
            result = JSON.parse(result); // Attempt to parse if result is a stringified JSON
        } catch (error) { }
        if (bind_variable == null) {
            return result
        }
        else {
            bind_variable.set(result);
        }


    }
    catch (error) {
        console.error('Error during backend request:', error);
        bind_variable.set(null);
    }
}












export async function data_request(bind_variable,func, ...args) {
    const url = `http://localhost:5057/data`;
    const payload = {
        function: func,
        arguments: args
    };

    try {
        console.log('Request sent to:', url);
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders() },
            body: JSON.stringify(payload) // Send the payload as a stringified JSON in the body
        });

        if (!response.ok) {
            throw new Error('POST response not ok');
        }
        let result = await response.json();
        try {
            result = JSON.parse(result); // Attempt to parse if result is a stringified JSON
        } catch (error){}
        if (bind_variable == null) {
            return result
        }
        else {
            bind_variable.set(result);
        }

        
    }
     catch (error) {
    console.error('Error during backend request:', error);
    bind_variable.set(null);
}
}

export async function backend_request(bind_variable, func, ...args) {
    const url = `http://localhost:5057/backend`;
    const payload = {
        function: func,
        arguments: args
    };
    console.log(args)
    try {
        console.log('Request sent to:', url);

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
},
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
                console.log(result)
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

