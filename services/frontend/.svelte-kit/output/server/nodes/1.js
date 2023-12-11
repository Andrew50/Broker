

export const index = 1;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/fallbacks/error.svelte.js')).default;
export const imports = ["_app/immutable/nodes/1.604bd456.js","_app/immutable/chunks/index.575d8db5.js","_app/immutable/chunks/singletons.a6407fd4.js","_app/immutable/chunks/index.9a5a6444.js"];
export const stylesheets = [];
export const fonts = [];
