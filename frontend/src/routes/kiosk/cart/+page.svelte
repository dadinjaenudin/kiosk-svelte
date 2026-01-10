<script lang="ts">
	import MultiCart from '$lib/components/kiosk/MultiCart.svelte';
	import { browser } from '$app/environment';
</script>

{#if browser}
	<MultiCart />
{:else}
	<div class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
	</div>
{/if}
