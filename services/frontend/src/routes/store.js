//import { bind } from 'svelte/internal';
import { writable } from 'svelte/store';
import { get } from 'svelte/store';
export let screener_data = writable([]);
export let chart_data = writable([]);
export let match_data = writable([[], [], []]);
export let auth_data = writable(null);
export let setups_list = writable([]);
export let watchlist_data = writable({});
export let settings = writable({});
export const focus = writable(null);
let base_url;

if (typeof window !== 'undefined') {
    if (window.location.hostname === 'localhost') {
        base_url = 'http://localhost:5057';
    } else {
        base_url = window.location.origin;
    }
}
function logout() {
    auth_data.set(null);
    goto('/auth');
}

function getAuthHeaders() {
    const token = get(auth_data);
    //return token ? { 'Authorization': `Bearer ${token}` } : {};
    return token ? { 'Authorization': token} : {};
}

export async function request(bind_variable, isPrivate, func, ...args) {
    let url;
    let headers;
    if (isPrivate){
        url = `${base_url}/private`;
        headers = { 'Content-Type': 'application/json', ...getAuthHeaders() };
    }else{
        url = `${base_url}/public`;
        headers = { 'Content-Type': 'application/json' };
    }
    args = args.map(arg => arg != null ? arg.toString() : arg);
    const payload = {
        function: func,
        arguments: args
    };
    console.log('Request sent to:', url, 'func:', func, 'args:', args);
    const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
    });
    let result = await response.json();
    console.log('result: ', result);
    if (bind_variable == null) {
        if (response.ok) {
            return [result, null]
        }else{
            return [null, result]
        }
    }
    else{
        if (response.ok) {
            bind_variable.set(result);
            return null
        }else{
            return result //this is an error message from backend
        }
    }
}

//export async function public_request(bind_variable, func, ...args) {
//    const url = `${base_url}/public`;
//    const payload = {
//        function: func,
//        arguments: args
//    };
//    console.log('Request sent to:', url, 'func:', func, 'args:', args);
//    try {
//        const response = await fetch(url, {
//            method: 'POST',
//            headers: {
//                'Content-Type': 'application/json'
//            },
//            body: JSON.stringify(payload) // Send the payload as a stringified JSON in the body
//        });
//        if (!response.ok) {
//            const errorText = await response.text();
//            throw new Error(`error: ${errorText}`);
//        }
//        let result = await response.json();
//        //result = JSON.parse(result); // Attempt to parse if result is a stringified JSON
//        console.log('result: ', result);
//        if (bind_variable == null) {
//            return result
//        }else {
//            bind_variable.set(result);
//        }
//    }
//    catch (error) {
//        console.error('Error during backend request:', error);
//        bind_variable.set(null);
//    }
//}
//
//export async function private_request(bind_variable, func, ...args) {
//    const url = `${base_url}/private`;
//    const payload = {
//        function: func,
//        arguments: args
//    };
//    console.log('Request sent to:', url, 'func:', func, 'args:', args);
//    try {
//        const response = await fetch(url, {
//            method: 'POST',
//            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
//            body: JSON.stringify(payload)
//        });
//        let result = await response.json();
//        result = JSON.parse(result); // Attempt to parse if result is a stringified JSON
//        console.log('result: ', result);
//        bind_variable.set(result);
//    } catch (error) {
//        console.error('Error during backend request:', error);
//        bind_variable.set(null);
//        return error;
//    }
//}

//export async function backend_request(bind_variable, func, ...args) {
//    const url = `${base_url}/backend`;
//    const payload = {
//        function: func,
//        arguments: args
//    };
//    console.log('Request sent to:', url, 'func:', func, 'args:', args);
//    try {
//        const response = await fetch(url, {
//            method: 'POST',
//            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
//            body: JSON.stringify(payload)
//        });
//        const task_id = JSON.parse(await reponse.json());
//        console.log('polling');
//        let result;
//        const checkStatus = async () => {
//            const response = await fetch(`${base_url}/poll/${task_id}`);
//            result = await response.json();
//            result = JSON.parse(result); // Attempt to parse if result is a stringified JSON
//            console.log('poll result: ', result);
//            if (result == 'running' || !result) {
//            } else {
//                bind_variable.set(result);
//                console.log('result: ', result);
//
//                console.log('result type : ', typeof result);
//
//                clearInterval(intervalId);
//            }
//        };
//        const intervalId = setInterval(checkStatus, 500); // Check every .2 seconds
//
//    } catch (error) {
//        console.error('Error during backend request:', error);
//        bind_variable.set(null);
//    }
//
//}
