<script>
	/**
	 * TenantSelector Component
	 * 
	 * Dropdown selector for admin users to switch between tenants.
	 * Only visible to admin/super_admin users.
	 * 
	 * Usage:
	 *   <TenantSelector bind:selectedTenant />
	 */
	
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';
	import { isAdmin, user } from '$lib/stores/auth';
	import { authFetch } from '$lib/api/auth';
	
	// Props
	export let selectedTenant = null;
	export let onChange = null;
	export let compact = false; // Compact mode for header display
	
	// State
	let tenants = writable([]);
	let loading = false;
	let error = null;
	
	// Fetch tenants on mount
	onMount(async () => {
		if ($isAdmin) {
			await loadTenants();
		}
	});
	
	async function loadTenants() {
		loading = true;
		error = null;
		
		try {
			const data = await authFetch('/api/admin/tenants/');
			tenants.set(data.results || data);
		} catch (e) {
			error = e.message;
			console.error('Failed to load tenants:', e);
		} finally {
			loading = false;
		}
	}
	
	function handleChange(event) {
		const value = event.target.value;
		selectedTenant = value === 'all' ? null : parseInt(value);
		
		if (onChange) {
			onChange(selectedTenant);
		}
	}
</script>

{#if $isAdmin}
	<div class="tenant-selector" class:compact>
		{#if !compact}
			<label for="tenant-select" class="block text-sm font-medium text-gray-700 mb-1">
				<svg class="inline-block w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
				</svg>
				Tenant Filter
			</label>
		{/if}
		
		{#if loading}
			<div class="flex items-center space-x-2 text-sm text-gray-500">
				<svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
				{#if !compact}
					<span>Loading tenants...</span>
				{/if}
			</div>
		{:else if error}
			<div class="text-sm text-red-600">
				<svg class="inline-block w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				{#if !compact}
					{error}
				{/if}
			</div>
		{:else}
			<select
				id="tenant-select"
				class="select-input"
				value={selectedTenant === null ? 'all' : selectedTenant}
				on:change={handleChange}
			>
				<option value="all">All Tenants</option>
				{#each $tenants as tenant (tenant.id)}
					<option value={tenant.id}>
						{tenant.name}
						{#if tenant.is_active === false}
							(Inactive)
						{/if}
					</option>
				{/each}
			</select>
			
			{#if $tenants.length === 0}
				<p class="text-sm text-gray-500 mt-1">No tenants found</p>
			{/if}
		{/if}
	</div>
{/if}

<style>
	.tenant-selector {
		@apply w-full;
	}
	
	.tenant-selector.compact {
		@apply w-auto;
	}
	
	.select-input {
		@apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm;
		@apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
		@apply bg-white text-gray-900 text-sm;
		@apply transition-colors duration-200;
	}
	
	.compact .select-input {
		@apply py-1.5 text-xs;
	}
	
	.select-input:hover {
		@apply border-gray-400;
	}
	
	.select-input:disabled {
		@apply bg-gray-100 text-gray-500 cursor-not-allowed;
	}
</style>
