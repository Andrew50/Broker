//import adapter from '@sveltejs/adapter-auto';
import node from '@sveltejs/adapter-node';
/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		//adapter: adapter()
		adapter: node()
	}
};

export default config;
