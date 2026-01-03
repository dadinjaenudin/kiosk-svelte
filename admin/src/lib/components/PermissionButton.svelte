<script>
	/**
	 * PermissionButton Component
	 * 
	 * Button that auto-hides based on user permissions.
	 * 
	 * Usage:
	 *   <PermissionButton action="delete" resource="products" on:click={deleteProduct}>
	 *     Delete
	 *   </PermissionButton>
	 */
	
	import { canPerform } from '$lib/stores/auth';
	
	// Props
	export let action = 'read';        // Action to check
	export let resource = '';          // Resource to check
	export let type = 'button';        // Button type
	export let variant = 'primary';    // Button style variant
	export let size = 'md';            // Button size
	export let disabled = false;       // Disabled state
	export let loading = false;        // Loading state
	export let fullWidth = false;      // Full width button
	
	// Permission check
	$: hasPermission = canPerform(action, resource);
	
	// CSS classes
	$: buttonClasses = [
		'btn',
		`btn-${variant}`,
		`btn-${size}`,
		fullWidth ? 'btn-block' : '',
		disabled || loading ? 'opacity-50 cursor-not-allowed' : '',
		$$props.class || ''
	].filter(Boolean).join(' ');
</script>

{#if hasPermission}
	<button
		{type}
		class={buttonClasses}
		disabled={disabled || loading}
		on:click
		on:mouseenter
		on:mouseleave
		on:focus
		on:blur
		{...$$restProps}
	>
		{#if loading}
			<svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
			</svg>
		{/if}
		<slot />
	</button>
{/if}

<style>
	.btn {
		@apply inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2;
	}
	
	/* Variants */
	.btn-primary {
		@apply bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500;
	}
	
	.btn-secondary {
		@apply bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500;
	}
	
	.btn-danger {
		@apply bg-red-600 text-white hover:bg-red-700 focus:ring-red-500;
	}
	
	.btn-success {
		@apply bg-green-600 text-white hover:bg-green-700 focus:ring-green-500;
	}
	
	.btn-warning {
		@apply bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500;
	}
	
	.btn-ghost {
		@apply bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500;
	}
	
	/* Sizes */
	.btn-sm {
		@apply px-3 py-1.5 text-sm;
	}
	
	.btn-md {
		@apply px-4 py-2 text-base;
	}
	
	.btn-lg {
		@apply px-6 py-3 text-lg;
	}
	
	.btn-block {
		@apply w-full;
	}
</style>
