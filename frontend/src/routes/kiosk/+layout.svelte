<script lang="ts">
	import { onMount } from 'svelte';
	import { preloadCode } from '$app/navigation';
	import KioskHeader from '$lib/components/kiosk/KioskHeader.svelte';
	import { socketService } from '$lib/services/socketService';
	import { networkStatus } from '$lib/services/networkService';
	
	// Preload all kiosk routes when layout mounts
	onMount(() => {
		console.log('🚀 Preloading all kiosk routes...');
		// Preload all kiosk pages for offline navigation
		preloadCode('/kiosk/idle');
		preloadCode('/kiosk/products');
		preloadCode('/kiosk/cart');
		preloadCode('/kiosk/checkout');
		preloadCode('/kiosk/success-offline');
		console.log('✅ Kiosk routes preloaded');
		
		// Initialize Socket.IO connections
		console.log('🔌 Initializing Socket.IO connections...');
		
		// Always connect to Local Sync Server for LAN communication
		(async () => {
			try {
				await socketService.connectLocal();
				console.log('✅ Local Sync Server connected');
			} catch (error) {
				console.warn('⚠️ Local Sync Server connection failed (will auto-retry):', error);
			}
		})();
		
		// Connect to Central Server if online
		const unsubscribe = networkStatus.subscribe(async (status) => {
			if (status.isOnline && status.mode === 'online') {
				try {
					await socketService.connectCentral();
					console.log('✅ Central Server connected');
				} catch (error) {
					console.warn('⚠️ Central Server connection failed (will auto-retry):', error);
				}
			}
		});
		
		return () => {
			unsubscribe();
		};
	});
</script>

<div class="kiosk-layout">
	<KioskHeader />
	<main class="kiosk-main">
		<slot />
	</main>
</div>

<style>
	.kiosk-layout {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background: #f9fafb;
	}
	
	.kiosk-main {
		flex: 1;
		width: 100%;
	}
</style>
