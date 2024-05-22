import { writable } from 'svelte/store';
import { get } from 'svelte/store';
import { goto } from "$app/navigation";
export let menuLeftPos = writable();
export let annotateData = writable([]);
export let journalData = writable([]);
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
    const url = new URL(window.location.origin);
    url.port = 5057;
    base_url = url.toString();
    base_url = base_url.substring(0,base_url.length - 1);


/*    if (window.location.hostname === 'localhost') {
        base_url = 'http://localhost:5057'; //dev
    } else {
        base_url = window.location.origin; //prod
    }*/
}

export function logout() {
    auth_data.set(null);
    goto('/');
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
export function autoLoad(bind_variable, buffer, func, args, currentPos){
    let loop = true;
    let timeoutID;
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
                bind_variable.update((b) =>  [...b, ...new_data]);
            }
        }
        if (loop){
            timeoutID = setTimeout(load, 1000);
        }
    }
    load();
    return () => {
        loop = false
        clearTimeout(timeoutID);
    };
}
