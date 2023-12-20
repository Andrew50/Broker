

export const index = 4;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/chart/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/4.60c8c616.js","_app/immutable/chunks/index.575d8db5.js","_app/immutable/chunks/store.c3d4df30.js","_app/immutable/chunks/index.9a5a6444.js","_app/immutable/chunks/candlestick-series.7c4e71b6.js","_app/immutable/chunks/navigation.abc9e600.js","_app/immutable/chunks/singletons.ceda8c2c.js"];
export const stylesheets = ["_app/immutable/assets/4.10373c0f.css"];
export const fonts = [];
