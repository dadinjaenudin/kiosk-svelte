<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { authFetch } from '$lib/api/auth';
	import Swal from 'sweetalert2';
	
	const API_BASE = '/api';
	
	let storeId = null;
	let store = null;
	let allOutlets = [];
	let assignedOutlets = [];
	let loading = true;
	let saving = false;
	
	// Get store ID from URL
	onMount(async () => {
		if (browser) {
			const urlParams = new URLSearchParams(window.location.search);
			storeId = urlParams.get('store');
			
			if (storeId) {
				await loadStore(); // This will call loadOutlets() after store is loaded
				await loadAssignedOutlets();
			}
		}
	});
	
	async function loadStore() {
		try {
			console.log('[Store-Outlets] Loading store:', storeId);
			store = await authFetch(`${API_BASE}/admin/stores/${storeId}/`);
			console.log('[Store-Outlets] Store loaded:', store);
			
			// After store loaded, load ALL outlets (cross-tenant assignment allowed)
			await loadOutlets();
		} catch (err) {
			console.error('[Store-Outlets] Error loading store:', err);
			Swal.fire('Error', 'Failed to load store details', 'error');
		}
	}
	
	async function loadOutlets() {
		try {
			// Filter outlets by store's tenant (same company only)
			const tenantId = store?.tenant;
			console.log('[Store-Outlets] Loading outlets for tenant:', tenantId);
			
			const url = `${API_BASE}/admin/settings/outlets/?tenant=${tenantId}`;
			console.log('[Store-Outlets] Fetching from:', url);
			
			const data = await authFetch(url);
			allOutlets = data.results || data;
			console.log('[Store-Outlets] Outlets loaded:', allOutlets.length, allOutlets);
		} catch (err) {
			console.error('[Store-Outlets] Error loading outlets:', err);
			Swal.fire('Error', 'Failed to load outlets', 'error');
		}
	}
	
	async function loadAssignedOutlets() {
		loading = true;
		try {
			console.log('[Store-Outlets] Loading assigned outlets for store:', storeId);
			// Get outlets assigned to this store
			const data = await authFetch(`${API_BASE}/admin/stores/${storeId}/outlets/`);
			console.log('[Store-Outlets] Assigned outlets response:', data);
			assignedOutlets = data.map(outlet => outlet.id);
			console.log('[Store-Outlets] Assigned outlet IDs:', assignedOutlets);
		} catch (err) {
			console.error('[Store-Outlets] Error loading assigned outlets:', err);
		} finally {
			loading = false;
		}
	}
	
	function isOutletAssigned(outletId) {
		return assignedOutlets.includes(outletId);
	}
	
	function getOutletDetails(outletId) {
		return allOutlets.find(o => o.id === outletId);
	}
	
	async function toggleOutlet(outlet) {
		const isAssigned = isOutletAssigned(outlet.id);
		
		saving = true;
		try {
			if (isAssigned) {
				// Remove assignment
				await authFetch(`${API_BASE}/admin/stores/${storeId}/remove_outlet/`, {
					method: 'POST',
					body: JSON.stringify({
						outlet: outlet.id
					})
				});
				
				// Update assignedOutlets array (trigger reactivity)
				assignedOutlets = assignedOutlets.filter(id => id !== outlet.id);
				console.log('[Store-Outlets] After remove, assignedOutlets:', assignedOutlets);
				
				Swal.fire({
					title: 'Removed!',
					html: `<p><strong>${outlet.name}</strong> removed from <strong>${store.name}</strong></p>`,
					icon: 'success',
					timer: 2000,
					showConfirmButton: false
				});
			} else {
				// Add assignment
				await authFetch(`${API_BASE}/admin/stores/${storeId}/add_outlet/`, {
					method: 'POST',
					body: JSON.stringify({
						outlet: outlet.id
					})
				});
				
				// Update assignedOutlets array (trigger reactivity)
				assignedOutlets = [...assignedOutlets, outlet.id];
				console.log('[Store-Outlets] After add, assignedOutlets:', assignedOutlets);
				
				Swal.fire({
					title: 'Added!',
					html: `<p><strong>${outlet.name}</strong> added to <strong>${store.name}</strong></p>`,
					icon: 'success',
					timer: 2000,
					showConfirmButton: false
				});
			}
			
			// Force re-render by reassigning
			assignedOutlets = assignedOutlets;
		} catch (err) {
			console.error('Error toggling outlet:', err);
			Swal.fire('Error', err.message || 'Failed to update outlet assignment', 'error');
		} finally {
			saving = false;
		}
	}
</script>

<div class="p-6 max-w-6xl mx-auto">
	<!-- Header -->
	<div class="mb-6">
		<div class="flex items-center gap-3 mb-2">
			<a
				href="/stores"
				class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
				title="Back to Stores"
			>
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
				</svg>
			</a>
			<div>
				<h1 class="text-3xl font-bold text-gray-900">🏬 Manage Store Outlets</h1>
				{#if store}
					<p class="text-gray-600 mt-1">
						Assign brand outlets to <strong>{store.name}</strong>
					</p>
					<p class="text-sm text-gray-500">
						📍 {store.address}, {store.city}
					</p>
				{/if}
			</div>
		</div>
	</div>

	{#if loading}
		<div class="text-center py-12">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			<p class="mt-2 text-gray-600">Loading outlets...</p>
		</div>
	{:else}
		<!-- Outlets Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each allOutlets as outlet (outlet.id)}
				{@const isAssigned = assignedOutlets.includes(outlet.id)}
				<div 
					class="bg-white rounded-lg border-2 transition-all {isAssigned ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-blue-300'}"
				>
					<div class="p-6">
						<div class="flex justify-between items-start mb-4">
							<div class="flex-1">
								<h3 class="text-xl font-bold text-gray-900 mb-1">{outlet.name}</h3>
								{#if outlet.brand_name}
									<p class="text-sm text-purple-600 font-medium">🏷️ {outlet.brand_name}</p>
								{/if}
								{#if outlet.tenant_name}
									<p class="text-xs text-gray-500 mt-1">🏢 {outlet.tenant_name}</p>
								{/if}
							</div>
							{#if isAssigned}
								<span class="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
									✓ Assigned
								</span>
							{/if}
						</div>

						<!-- Outlet Info -->
						<div class="text-sm text-gray-600 space-y-1 mb-4">
							{#if outlet.phone}
								<p>📞 {outlet.phone}</p>
							{/if}
							{#if outlet.email}
								<p>✉️ {outlet.email}</p>
							{/if}
						</div>

						<!-- Toggle Button -->
						<button
							on:click={() => toggleOutlet(outlet)}
							disabled={saving}
							class="w-full px-4 py-2 rounded-lg font-medium transition-all disabled:opacity-50 {isAssigned 
								? 'bg-red-50 hover:bg-red-100 text-red-700 border border-red-300' 
								: 'bg-blue-600 hover:bg-blue-700 text-white'}"
						>
							{#if saving}
								<span class="inline-block animate-spin mr-2">⚙️</span>
							{/if}
							{isAssigned ? '❌ Remove from Store' : '➕ Add to Store'}
						</button>
					</div>
				</div>
			{/each}
		</div>

		{#if allOutlets.length === 0}
			<div class="text-center py-12">
				<p class="text-gray-500 text-lg">No outlets available</p>
				<p class="text-gray-400 text-sm mt-2">Create outlets first in the Outlets page</p>
				<a href="/outlets" class="inline-block mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
					Go to Outlets
				</a>
			</div>
		{/if}
	{/if}
</div>
