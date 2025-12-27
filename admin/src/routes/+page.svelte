<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { isAuthenticated } from '$lib/stores/auth';

	onMount(() => {
		if ($isAuthenticated) {
			goto('/dashboard');
		} else {
			goto('/login');
		}
	});
</script>

<div class="min-h-screen flex items-center justify-center">
	<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
</div>
