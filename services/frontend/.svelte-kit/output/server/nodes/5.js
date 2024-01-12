

export const index = 5;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/stable/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/5.riFRZxXu.js","_app/immutable/chunks/scheduler.VY-UclLW.js","_app/immutable/chunks/index.QBX9jeLG.js","_app/immutable/chunks/candlestick-series.ckzwoZw9.js","_app/immutable/chunks/index.kYg0fxAy.js"];
export const stylesheets = ["_app/immutable/assets/5.0qXp_g_K.css"];
export const fonts = [];
