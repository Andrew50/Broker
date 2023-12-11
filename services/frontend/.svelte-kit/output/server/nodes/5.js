

export const index = 5;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/stable/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/5.1d310254.js","_app/immutable/chunks/index.575d8db5.js","_app/immutable/chunks/index.9a5a6444.js","_app/immutable/chunks/candlestick-series.7c4e71b6.js"];
export const stylesheets = ["_app/immutable/assets/5.aefe0cbd.css"];
export const fonts = [];
