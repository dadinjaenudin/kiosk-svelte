<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { isAuthenticated } from '$lib/stores/auth';

	let hasRedirected = false;

	onMount(() => {
		// Only redirect once when component mounts and only if on root path
		console.log('Root +page.svelte mounted, pathname:', $page.url.pathname);
		
		if (!hasRedirected && $page.url.pathname === '/') {
			hasRedirected = true;
			console.log('Redirecting from root, authenticated:', $isAuthenticated);
			
			if ($isAuthenticated) {
				goto('/dashboard');
			} else {
				goto('/login');
			}
		}
	});
</script>

<div class="min-h-screen flex items-center justify-center">
	<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
</div>
