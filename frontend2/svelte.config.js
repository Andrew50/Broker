import adapter from '@sveltejs/adapter-static';

export default {
  kit: {
    // ... other configurations
    target: '#svelte',
    adapter: adapter(),
    vite: {
      server: {
        proxy: {
          '/api': 'http://localhost:5000', // Proxy API requests to Flask backend
        },
      },
    },
  },
};