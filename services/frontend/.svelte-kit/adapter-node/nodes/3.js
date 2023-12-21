

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/auth/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/3.Fd5TwDDL.js","_app/immutable/chunks/scheduler.VY-UclLW.js","_app/immutable/chunks/index.QBX9jeLG.js","_app/immutable/chunks/navigation.CfJo0_JX.js","_app/immutable/chunks/singletons.8HDxCJlS.js","_app/immutable/chunks/index.kYg0fxAy.js","_app/immutable/chunks/store.B2EyIDYf.js"];
export const stylesheets = ["_app/immutable/assets/3.LnfLVtl2.css"];
export const fonts = [];
