

export const index = 2;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/2.b5f87b3a.js","_app/immutable/chunks/index.575d8db5.js","_app/immutable/chunks/navigation.cba65cff.js","_app/immutable/chunks/singletons.a6407fd4.js","_app/immutable/chunks/index.9a5a6444.js"];
export const stylesheets = ["_app/immutable/assets/2.49ac5cd1.css"];
export const fonts = [];
