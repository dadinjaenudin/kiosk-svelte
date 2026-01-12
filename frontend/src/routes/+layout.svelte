<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import '../app.css';
	import { initializeTenantContext, currentTenant, tenantReady, hasToken } from '$lib/stores/tenant.js';
	import { masterDataService } from '$lib/services/masterDataService';
	import { networkService } from '$lib/services/networkService';
	import { serviceWorkerManager } from '$lib/services/serviceWorkerManager';
	
	let loading = true;
	
	onMount(async () => {
		if (browser) {
			// Register Service Worker for offline support
			try {
				const swRegistered = await serviceWorkerManager.register();
				if (swRegistered) {
					console.log('✅ Service Worker registered successfully');
				}
			} catch (error) {
				console.error('❌ Service Worker registration failed:', error);
			}
			
		// Network service starts monitoring automatically on initialization
		// No need to call startMonitoring()
			if (hasToken()) {
				// Initialize tenant context
				const success = await initializeTenantContext();
				if (!success) {
					console.warn('Failed to initialize tenant context');
				}
			}
			
			// Pre-fetch master data if online
			const status = networkService.getStatus();
			if (status.mode === 'online') {
				try {
					console.log('🔄 Pre-fetching master data...');
					await masterDataService.preFetchData();
					console.log('✅ Master data synced successfully');
				} catch (error) {
					console.error('❌ Master data sync failed:', error);
					// App tetap jalan, gunakan cached data
				}
			} else {
				console.log('📴 Offline mode - using cached master data');
			}
			
			loading = false;
		}
	});
</script>

{#if loading}
	<div class="loading-screen">
		<div class="spinner"></div>
		<p>Loading...</p>
	</div>
{:else}
	<slot />
{/if}

<style>
	.loading-screen {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100vh;
		background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
		color: white;
	}
	
	.spinner {
		width: 50px;
		height: 50px;
		border: 4px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
	
	.loading-screen p {
		margin-top: 20px;
		font-size: 16px;
		font-weight: 500;
	}
</style>
