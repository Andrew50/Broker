import staticAdapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: staticAdapter({
			// default options are shown
			pages: 'build',
			assets: 'build',
			fallback: null
		}),
		// ...
	}
};

export default config;