

export const index = 6;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/test/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/6.DxhWUTfa.js","_app/immutable/chunks/scheduler.VY-UclLW.js","_app/immutable/chunks/index.QBX9jeLG.js","_app/immutable/chunks/index.kYg0fxAy.js"];
export const stylesheets = [];
export const fonts = [];
