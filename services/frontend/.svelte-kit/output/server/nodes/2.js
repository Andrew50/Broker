

export const index = 2;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/2.9ca1a5d9.js","_app/immutable/chunks/index.575d8db5.js","_app/immutable/chunks/navigation.abc9e600.js","_app/immutable/chunks/singletons.ceda8c2c.js","_app/immutable/chunks/index.9a5a6444.js"];
export const stylesheets = ["_app/immutable/assets/2.49ac5cd1.css"];
export const fonts = [];
