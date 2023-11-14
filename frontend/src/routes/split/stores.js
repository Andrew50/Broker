
export let chart_data_store = writable([
{time: '2018-10-19', open: 180.34, high: 180.99, low: 178.57, close: 179.85}
    ]);
    export let chart_data;
chart_data_store.subscribe((value) => {
        console.log(value)
try{chart_data = JSON.parse(value)}
    catch{chart_data = value}
});








