<script>
	import { onMount } from 'svelte';
	
	// Redirect to kiosk mode on mount
	onMount(() => {
		window.location.href = '/kiosk';
	});
</script>

<div class="h-screen flex items-center justify-center bg-gradient-to-br from-primary to-secondary">
	<div class="text-center text-white">
		<div class="text-9xl mb-8">🍽️</div>
		<h1 class="text-6xl font-bold mb-4">POS F&B System</h1>
		<p class="text-2xl mb-8">Loading Kiosk Mode...</p>
		<div class="spinner w-16 h-16 mx-auto"></div>
	</div>
</div>
