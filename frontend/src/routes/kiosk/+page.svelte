<script lang="ts">
import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isKioskConfigured, kioskConfig } from '$lib/stores/kioskStore';
	import KioskSetup from '$lib/components/kiosk/KioskSetup.svelte';
let showSetup = false;

// Subscribe to kiosk configuration status
$: kioskConfigured = $isKioskConfigured;

onMount(() => {
console.log('🏪 Multi-Outlet Kiosk mounted');
console.log('📍 Store:', $kioskConfig.storeName || 'Not configured');
console.log('✅ Configured:', kioskConfigured);

// Check if kiosk needs configuration
if (!kioskConfigured) {
showSetup = true;
} else {
	// OPSI 2: Go directly to products page (no outlet selection)
	goto('/kiosk/products');
}
});

function handleConfigured(event: CustomEvent) {
console.log('✅ Kiosk configured:', event.detail);
showSetup = false;
kioskConfigured = true;
	
	// OPSI 2: Redirect to products page after setup
	goto('/kiosk/products');
}

function reconfigure() {
if (confirm('Reset kiosk configuration? This will clear all settings.')) {
kioskConfig.reset();
showSetup = true;
kioskConfigured = false;
}
}
</script>

<div class="kiosk-container">
{#if showSetup || !kioskConfigured}
<!-- STEP 1: Kiosk Setup -->
<KioskSetup on:configured={handleConfigured} />
{:else}
<!-- OPSI 2: Redirect to products (loading...) -->
<div class="flex items-center justify-center">
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

.btn-reconfigure {
position: fixed;
bottom: 20px;
right: 20px;
padding: 10px 20px;
background: rgba(255, 255, 255, 0.2);
border: 1px solid rgba(255, 255, 255, 0.3);
border-radius: 8px;
color: white;
font-size: 14px;
cursor: pointer;
backdrop-filter: blur(10px);
transition: all 0.3s ease;
z-index: 1000;
}

.btn-reconfigure:hover {
background: rgba(255, 255, 255, 0.3);
transform: translateY(-2px);
}
</style>
