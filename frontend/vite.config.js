import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
// import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
	plugins: [
		sveltekit()
		// PWA Plugin temporarily disabled
	],
	build: {
		rollupOptions: {
			output: {
				manualChunks: (id) => {
					// Bundle all kiosk routes into one chunk to prevent lazy-loading issues when offline
					if (id.includes('src/routes/kiosk')) {
						return 'kiosk';
					}
					// Bundle all kiosk components together
					if (id.includes('src/lib/components/kiosk')) {
						return 'kiosk';
					}
					// Bundle all services together (offline, sync, network)
					if (id.includes('src/lib/services')) {
						return 'kiosk-services';
					}
					// Bundle all stores together
					if (id.includes('src/lib/stores')) {
						return 'kiosk-stores';
					}
				}
			}
		}
	},
	server: {
		host: '0.0.0.0',
		port: 5173,
		proxy: {
			'/api': {
				target: 'http://backend:8000',
				changeOrigin: true,
				secure: false
			}
		}
	},
	preview: {
		host: '0.0.0.0',
		port: 5173,
		proxy: {
			'/api': {
				target: 'http://backend:8000',
				changeOrigin: true,
				secure: false
			}
		}
	}
});
