import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: process.env.VITE_PORT || 5173,  // Use 5173 in Docker, 5175 locally
		host: '0.0.0.0',
		proxy: {
			'/api': {
				target: process.env.VITE_API_URL || 'http://localhost:8001',
				changeOrigin: true,
				configure: (proxy, options) => {
					proxy.on('error', (err, req, res) => {
						console.log('proxy error', err);
					});
					proxy.on('proxyReq', (proxyReq, req, res) => {
						console.log('🔄 Proxying:', req.method, req.url, '→', options.target + req.url);
					});
					proxy.on('proxyRes', (proxyRes, req, res) => {
						console.log('📡 Proxy response:', proxyRes.statusCode, req.url);
					});
				}
			}
		}
	}
});
