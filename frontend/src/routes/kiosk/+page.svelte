<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { kioskConfig } from '$lib/stores/kioskStore';
	import KioskSetup from '$lib/components/kiosk/KioskSetup.svelte';

	let showSetup = false;

	// Subscribe to kiosk configuration
	$: isConfigured = $kioskConfig.isConfigured;

	onMount(() => {
		console.log('🏪 Multi-Outlet Kiosk mounted');
		console.log('📍 Store:', $kioskConfig.storeName || 'Not configured');
		console.log('✅ Configured:', isConfigured);

		// Check if kiosk needs configuration
		if (!isConfigured) {
			showSetup = true;
		} else {
			// Redirect to idle screen if already configured
			goto('/kiosk/idle');
		}
	});

	function handleConfigured(event: CustomEvent) {
		console.log('✅ Kiosk configured:', event.detail);
		showSetup = false;
		// After configuration, go to idle screen
		goto('/kiosk/idle');
	}
</script>

<div class="kiosk-container">
	{#if showSetup}
		<!-- STEP 1: Kiosk Setup -->
		<KioskSetup on:configured={handleConfigured} />
	{:else}
		<!-- Loading/Redirecting -->
		<div class="flex items-center justify-center min-h-screen">
			<div class="text-white text-xl">Loading...</div>
		</div>
	{/if}
</div>

<style>
	.kiosk-container {
		min-height: 100vh;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 20px;
	}

	.welcome-screen {
		text-align: center;
		color: white;
		max-width: 600px;
		width: 100%;
	}

	.welcome-content {
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(10px);
		border-radius: 24px;
		padding: 60px 40px;
		border: 2px solid rgba(255, 255, 255, 0.2);
	}

	.welcome-title {
		font-size: 2.5rem;
		font-weight: 300;
		margin-bottom: 10px;
		opacity: 0.9;
	}

	.store-name {
		font-size: 3rem;
		font-weight: 700;
		margin-bottom: 10px;
		text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
	}

	.welcome-subtitle {
		font-size: 1.2rem;
		opacity: 0.8;
		margin-bottom: 50px;
	}

	.btn-start-order {
		background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
		border: none;
		border-radius: 16px;
		padding: 30px 60px;
		font-size: 1.8rem;
		font-weight: 700;
		color: white;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
		display: flex;
		align-items: center;
		gap: 20px;
		margin: 0 auto 30px;
	}

	.btn-start-order:hover {
		transform: scale(1.05);
		box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
	}

	.btn-start-order:active {
		transform: scale(0.98);
	}

	.btn-icon {
		font-size: 2.5rem;
	}

	.btn-reconfigure-bottom {
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.3);
		border-radius: 10px;
		padding: 12px 24px;
		color: white;
		font-size: 1rem;
		cursor: pointer;
		transition: all 0.3s ease;
	}

	.btn-reconfigure-bottom:hover {
		background: rgba(255, 255, 255, 0.2);
	}
</style>
