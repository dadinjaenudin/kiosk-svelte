<script lang="ts">
	import KioskHeader from '$lib/components/kiosk/KioskHeader.svelte';
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
