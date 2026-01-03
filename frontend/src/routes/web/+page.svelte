<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	
	let redirecting = true;
	
	onMount(() => {
		if (browser) {
			// Redirect to kiosk for now (same interface)
			// Nanti bisa dibedakan UI untuk web vs kiosk
			window.location.href = '/kiosk';
		}
	});
</script>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
	<div class="text-center text-white">
		<div class="mb-4">
			<svg class="animate-spin h-16 w-16 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
			</svg>
		</div>
		<h1 class="text-3xl font-bold mb-2">Welcome to Online Ordering</h1>
		<p class="text-lg opacity-90">Redirecting to menu...</p>
	</div>
</div>
