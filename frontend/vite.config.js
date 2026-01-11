import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
	plugins: [
		sveltekit(),
		VitePWA({
			registerType: 'autoUpdate',
			includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
			// Use custom service worker with Workbox
			srcDir: 'src',
			filename: 'service-worker.js',
			strategies: 'injectManifest',
			injectManifest: {
				globPatterns: ['**/*.{js,css,html,ico,png,svg,webp,woff,woff2}'],
			},
			manifest: {
				name: 'POS F&B Kiosk',
				short_name: 'POS Kiosk',
				description: 'Enterprise Point of Sale System for Food & Beverage',
				theme_color: '#ffffff',
				background_color: '#ffffff',
				display: 'fullscreen',
				orientation: 'landscape',
				icons: [
					{
						src: 'pwa-192x192.png',
						sizes: '192x192',
						type: 'image/png'
					},
					{
						src: 'pwa-512x512.png',
						sizes: '512x512',
						type: 'image/png'
					},
					{
						src: 'pwa-512x512.png',
						sizes: '512x512',
						type: 'image/png',
						purpose: 'any maskable'
					}
				]
			},
			devOptions: {
				enabled: true,
				type: 'module'
			}
		})
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
	}
});
