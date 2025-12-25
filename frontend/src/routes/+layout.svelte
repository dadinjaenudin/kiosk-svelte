<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import '../app.css';
	import { initializeTenantContext, currentTenant, tenantReady } from '$lib/stores/tenant.js';
	
	// SvelteKit props (suppress warnings)
	export let data = undefined;
	export let params = undefined;
	
	let loading = true;
	
	onMount(async () => {
		if (browser) {
			// Check if we have auth token
			const hasToken = localStorage.getItem('access_token');
			
			if (hasToken) {
				// Initialize tenant context
				const success = await initializeTenantContext();
				if (!success) {
					console.warn('Failed to initialize tenant context');
				}
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
