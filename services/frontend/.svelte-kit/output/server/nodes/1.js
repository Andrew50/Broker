

export const index = 1;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/fallbacks/error.svelte.js')).default;
export const imports = ["_app/immutable/nodes/1.7425qcHF.js","_app/immutable/chunks/scheduler.VY-UclLW.js","_app/immutable/chunks/index.QBX9jeLG.js","_app/immutable/chunks/singletons.8HDxCJlS.js","_app/immutable/chunks/index.kYg0fxAy.js"];
export const stylesheets = [];
export const fonts = [];
