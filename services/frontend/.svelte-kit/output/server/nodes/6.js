

export const index = 6;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/test/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/6.3f16f971.js","_app/immutable/chunks/index.575d8db5.js","_app/immutable/chunks/index.9a5a6444.js"];
export const stylesheets = [];
export const fonts = [];
