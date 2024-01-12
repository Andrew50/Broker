import nodeAdapter from '@sveltejs/adapter-node';

const config = {
	kit: {
		// Use the Node adapter
		adapter: nodeAdapter({
			// default options are shown
			//out: 'build',
			//precompress: false,
			//envPrefix: ''
		}),
		// ...other configurations
	}
};

export default config;
