

export const index = 3;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/auth/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/3.7b20c42d.js","_app/immutable/chunks/index.575d8db5.js","_app/immutable/chunks/navigation.cba65cff.js","_app/immutable/chunks/singletons.a6407fd4.js","_app/immutable/chunks/index.9a5a6444.js","_app/immutable/chunks/store.c3d4df30.js"];
export const stylesheets = ["_app/immutable/assets/3.26c0b357.css"];
export const fonts = [];
