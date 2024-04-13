import { writable } from 'svelte/store';
import { get } from 'svelte/store';
export let annotations = writable([]);
export let screener_data = writable([]);
export let chartQuery = writable([]);
export let match_data = writable([[], [], []]);
export let auth_data = writable(null);
export let setups_list = writable([]);
export let currentEntry = writable("");
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
export function logout() {
    auth_data.set(null);
    goto('/auth');
}

export function toDT(timestamp, format = 1) {
    // Create a Date object in UTC
    const date = new Date(timestamp);
    let options;
    switch (format) {
        case 1:
            // Format the date as a local date string
            return date.toLocaleDateString('en-US');
        case 2:
            options = {
                year: 'numeric', month: 'numeric', day: 'numeric',
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                hour12: false,  // This will remove AM/PM
            };
            return new Intl.DateTimeFormat('en-US', options).format(date);
        case 3:
            options = {
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                hour12: false,  // This will remove AM/PM
            };
            return new Intl.DateTimeFormat('en-US', options).format(date);
    }
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
    let argsObj = {};
    for (let i = 0; i < args.length; i++){
        argsObj[`a${i+1}`] = args[i];
    }
    const payload = {
        func: func,
        args: argsObj
    };
    const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
    });
    let result, err;
    if (response.ok){
        result = await response.json();
        err = null;
    }else{
        result = null;
        err = await response.text();
    }
    console.log('request:', payload,'result:', result, 'error:', err);
    if (bind_variable == null){
        return [result, err];
    }else{
        if (err == null){
            bind_variable.set(result);
        }
        return err;
    }
}

//args for reqest = [index, buffer, ...args]
export async function autoLoad(bind_variable, buffer, func, args, currentPos){
    let loop = true;
    async function load(){
        const current_data = get(bind_variable);
        console.log('autoloading');
        if (currentPos() + buffer >= current_data.length){
            const index = current_data.length > 0 ? current_data[current_data.length - 1][0] : null;
            let [new_data, error] = await request(null, true, func,index, buffer, ...args);
            if (error != null){
                console.log('error:', error);
            }else if (new_data == null || new_data.length == 0){
                loop = false;
            }else{
                bind_variable.set([...current_data, ...new_data]);
            }
        }
        if (loop){
            setTimeout(load, 1000);
        }
    }
    load();
    return () => {loop = false};
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
