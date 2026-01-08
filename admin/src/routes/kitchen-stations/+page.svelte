<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { page } from '$app/stores';
	import Swal from 'sweetalert2';
	import { user, currentOutlet, selectedTenant } from '$lib/stores/auth';

	// SvelteKit page props
	export let params = {};
	import { 
		getKitchenStations, 
		createKitchenStation, 
		updateKitchenStation, 
		patchKitchenStation,
		deleteKitchenStation 
	} from '$lib/api/kitchenStations';
	import { getOutlets } from '$lib/api/settings';
	import { getKitchenStationTypes } from '$lib/api/kitchenStationTypes';

	let stations = [];
	let outlets = [];
	let stationTypes = []; // Available kitchen station types
	let loading = true;
	let error = null;
	let showModal = false;
	let editingStation = null;
	let filterOutletId = null;

	// Form data
	let formData = {
		outlet: null,
		name: '',
		code: '',
		description: '',
		is_active: true,
		sort_order: 0
	};

	// Load outlets for dropdown
	async function loadOutlets() {
		try {
			const response = await getOutlets();
			outlets = response.results || response || [];
			
			// Get outlet ID from URL query params first
			if (browser) {
				const urlParams = new URLSearchParams(window.location.search);
				const outletParam = urlParams.get('outlet');
				if (outletParam) {
					filterOutletId = parseInt(outletParam);
					return;
				}
			}
			
			// Fallback: Set default outlet from currentOutlet store
			if ($currentOutlet && outlets.find(o => o.id === $currentOutlet.id)) {
				filterOutletId = $currentOutlet.id;
			} else if (outlets.length > 0) {
				filterOutletId = outlets[0].id;
			}
		} catch (err) {
			console.error('Error loading outlets:', err);
		}
	}

	// Load kitchen station types
	async function loadStationTypes() {
		try {
			const response = await getKitchenStationTypes($selectedTenant);
			stationTypes = response.results || response || [];
			// Filter only active types
			stationTypes = stationTypes.filter(t => t.is_active);
			// Sort by sort_order
			stationTypes.sort((a, b) => a.sort_order - b.sort_order);
		} catch (err) {
			console.error('Error loading station types:', err);
		}
	}

	// Load kitchen stations
	async function loadStations() {
		loading = true;
		error = null;
		try {
			const params = {};
			if (filterOutletId) {
				params.outlet = filterOutletId;
				console.log('[Kitchen Stations] Loading stations for outlet:', filterOutletId);
			} else {
				console.log('[Kitchen Stations] Loading all stations (no filter)');
			}
			
			const response = await getKitchenStations(params);
			stations = response.results || response || [];
			
			console.log('[Kitchen Stations] Loaded', stations.length, 'stations:', stations.map(s => ({id: s.id, name: s.name, outlet: s.outlet})));
			
			// Sort by outlet and sort_order
			stations.sort((a, b) => {
				if (a.outlet !== b.outlet) return a.outlet - b.outlet;
				return a.sort_order - b.sort_order;
			});
		} catch (err) {
			console.error('Error loading stations:', err);
			error = 'Failed to load kitchen stations';
		} finally {
			loading = false;
		}
	}

	// Open modal for creating new station
	function openCreateModal() {
		editingStation = null;
		formData = {
			outlet: filterOutletId || (outlets.length > 0 ? outlets[0].id : null),
			name: '',
			code: '',
			description: '',
			is_active: true,
			sort_order: 0
		};
		showModal = true;
	}

	// Open modal for editing station
	function openEditModal(station) {
		editingStation = station;
		formData = {
			outlet: station.outlet,
			name: station.name,
			code: station.code,
			description: station.description || '',
			is_active: station.is_active,
			sort_order: station.sort_order
		};
		showModal = true;
	}

	// Close modal
	function closeModal() {
		showModal = false;
		editingStation = null;
		formData = {
			outlet: null,
			name: '',
			code: '',
			description: '',
			is_active: true,
			sort_order: 0
		};
	}

	// Save station (create or update)
	async function saveStation() {
		try {
			if (editingStation) {
				// Update existing station
				await updateKitchenStation(editingStation.id, formData);
			} else {
				// Create new station
				await createKitchenStation(formData);
			}
			
			closeModal();
			await loadStations();
		} catch (err) {
			console.error('Error saving station:', err);
			const errorData = err.response?.data || err.data || {};
			error = errorData.detail || errorData.code?.[0] || 'Failed to save station';
		}
	}

	// Delete station (soft delete)
	async function deleteStation(station) {
		// Show outlet name in confirmation
		const outletName = getOutletName(station.outlet);
		
		const result = await Swal.fire({
			title: 'Delete Kitchen Station?',
			html: `
				<div class="text-left">
					<p class="text-gray-700 mb-2">Are you sure you want to delete this station?</p>
					<div class="bg-gray-50 rounded-lg p-4 mb-3">
						<p class="font-semibold text-gray-900">${station.name}</p>
						<p class="text-sm text-gray-600">Code: ${station.code}</p>
						<p class="text-sm text-gray-600">Outlet: ${outletName}</p>
						<p class="text-xs text-gray-500 mt-1">ID: ${station.id}</p>
					</div>
					<p class="text-sm text-orange-600">⚠️ This station will be deactivated and no longer visible.</p>
				</div>
			`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#dc2626',
			cancelButtonColor: '#6b7280',
			confirmButtonText: '🗑️ Yes, Delete It',
			cancelButtonText: 'Cancel',
			reverseButtons: true,
			focusCancel: true
		});

		if (!result.isConfirmed) {
			return;
		}

		try {
			await deleteKitchenStation(station.id);
			
			await Swal.fire({
				title: 'Deleted!',
				html: `
					<p class="text-gray-700">Kitchen station has been successfully deactivated.</p>
					<div class="bg-green-50 rounded-lg p-3 mt-3">
						<p class="font-semibold text-green-900">${station.name}</p>
						<p class="text-sm text-green-700">from ${outletName}</p>
					</div>
				`,
				icon: 'success',
				confirmButtonColor: '#10b981',
				timer: 3000
			});
			
			await loadStations();
		} catch (err) {
			console.error('Error deleting station:', err);
			error = `Failed to delete station: ${err.message || 'Unknown error'}`;
			
			await Swal.fire({
				title: 'Error!',
				text: error,
				icon: 'error',
				confirmButtonColor: '#dc2626'
			});
		}
	}

	// Toggle station active status
	async function toggleActive(station) {
		try {
			await patchKitchenStation(station.id, {
				is_active: !station.is_active
			});
			await loadStations();
		} catch (err) {
			console.error('Error toggling station:', err);
			error = 'Failed to update station status';
		}
	}
	
	// Helper function to get station type info by code
	function getStationType(code) {
		return stationTypes.find(t => t.code === code);
	}

	// Filter by outlet
	async function changeOutletFilter(outletId) {
		filterOutletId = outletId ? parseInt(outletId) : null;
		await loadStations();
	}

	// Get outlet name by ID
	function getOutletName(outletId) {
		const outlet = outlets.find(o => o.id === outletId);
		return outlet ? outlet.name : `Outlet ${outletId}`;
	}

	onMount(async () => {
		await loadOutlets();
		await loadStationTypes();
		await loadStations();
	});
</script>

<div class="p-6">
	<!-- Header -->
	<div class="mb-6">
		<div class="flex justify-between items-center">
			<div>
				<div class="flex items-center gap-3">
					<a
						href="/outlets"
						class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
						title="Back to Outlets"
					>
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
						</svg>
					</a>
					<div>
						<h1 class="text-3xl font-bold text-gray-900">🍳 Kitchen Stations</h1>
						<p class="text-gray-600 mt-1">Manage kitchen stations for each outlet</p>
					</div>
				</div>
			</div>
			<button
				on:click={openCreateModal}
				class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
			>
				<span class="text-xl">➕</span>
				Add Station
			</button>
		</div>

		<!-- Filter by Outlet -->
		{#if outlets.length > 0}
			<div class="mt-4">
				<label class="block text-sm font-medium text-gray-700 mb-1">
					Filter by Outlet
				</label>
				<select
					bind:value={filterOutletId}
					on:change={(e) => changeOutletFilter(e.target.value)}
					class="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
				>
					<option value="">All Outlets</option>
					{#each outlets as outlet}
						<option value={outlet.id}>{outlet.name}</option>
					{/each}
				</select>
			</div>
		{/if}
	</div>

	<!-- Error Message -->
	{#if error}
		<div class="mb-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
			<p class="font-medium">Error</p>
			<p class="text-sm">{error}</p>
		</div>
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="text-center py-12">
			<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			<p class="mt-4 text-gray-600">Loading kitchen stations...</p>
		</div>
	{:else if stations.length === 0}
		<div class="text-center py-12 bg-gray-50 rounded-lg">
			<span class="text-6xl">🍳</span>
			<p class="mt-4 text-xl text-gray-600">No kitchen stations found</p>
			<p class="text-gray-500 mt-2">Create your first kitchen station to get started</p>
			<button
				on:click={openCreateModal}
				class="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
			>
				Add First Station
			</button>
		</div>
	{:else}
		<!-- Stations Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each stations as station}
				<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition">
					<div class="flex justify-between items-start mb-4">
						<div class="flex-1">
							<div class="flex items-center gap-2 mb-1">
								{#if getStationType(station.code)}
									<span class="text-2xl">{getStationType(station.code).icon}</span>
								{/if}
								<h3 class="text-xl font-bold text-gray-900">{station.name}</h3>
							</div>
							<div class="flex items-center gap-2 mt-1">
								<span 
									class="px-2 py-0.5 text-xs font-semibold rounded"
									style="background-color: {getStationType(station.code)?.color}20; color: {getStationType(station.code)?.color || '#666'};"
								>
									{station.code}
								</span>
								{#if getStationType(station.code)}
									<span class="text-xs text-gray-500">
										{getStationType(station.code).name}
									</span>
								{/if}
							</div>
							<p class="text-sm text-gray-600 mt-2">
								<span class="font-medium">{getOutletName(station.outlet)}</span>
								<span class="text-xs text-gray-400 ml-2">ID: {station.id}</span>
							</p>
						</div>
						<button
							on:click={() => toggleActive(station)}
							class="flex-shrink-0"
							title={station.is_active ? 'Active' : 'Inactive'}
						>
							{#if station.is_active}
								<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
									● Active
								</span>
							{:else}
								<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
									○ Inactive
								</span>
							{/if}
						</button>
					</div>

					{#if station.description}
						<p class="text-sm text-gray-600 mb-4">{station.description}</p>
					{/if}

					<div class="flex items-center justify-between text-sm text-gray-500 mb-4">
						<span>Sort Order: {station.sort_order}</span>
						{#if station.product_count !== undefined}
							<span>{station.product_count} products</span>
						{/if}
					</div>

					<div class="flex gap-2">
						<button
							on:click={() => openEditModal(station)}
							class="flex-1 px-3 py-2 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition text-sm font-medium"
						>
							✏️ Edit
						</button>
						<button
							on:click={() => deleteStation(station)}
							class="flex-1 px-3 py-2 bg-red-50 text-red-700 rounded hover:bg-red-100 transition text-sm font-medium"
						>
							🗑️ Delete
						</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Modal for Create/Edit Station -->
{#if showModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
		<div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
			<div class="p-6">
				<h2 class="text-2xl font-bold text-gray-900 mb-4">
					{editingStation ? 'Edit Kitchen Station' : 'Create Kitchen Station'}
				</h2>

				<form on:submit|preventDefault={saveStation}>
					<!-- Outlet Selection -->
					<div class="mb-4">
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Outlet <span class="text-red-500">*</span>
						</label>
						<select
							bind:value={formData.outlet}
							required
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option value="">Select outlet</option>
							{#each outlets as outlet}
								<option value={outlet.id}>{outlet.name}</option>
							{/each}
						</select>
					</div>

					<!-- Station Name -->
					<div class="mb-4">
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Station Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.name}
							required
							maxlength="100"
							placeholder="e.g., Main Kitchen"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>

					<!-- Station Code -->
					<div class="mb-4">
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Station Code <span class="text-red-500">*</span>
						</label>
						<select
							bind:value={formData.code}
							required
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option value="">Select station type</option>
							{#each stationTypes as type}
								<option value={type.code}>
									{type.icon} {type.name} ({type.code})
								</option>
							{/each}
						</select>
						<p class="text-xs text-gray-500 mt-1">
							Must match Kitchen Station Type for routing to work
						</p>
					</div>

					<!-- Description -->
					<div class="mb-4">
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Description
						</label>
						<textarea
							bind:value={formData.description}
							rows="3"
							placeholder="Optional description"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						></textarea>
					</div>

					<!-- Sort Order -->
					<div class="mb-4">
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Sort Order
						</label>
						<input
							type="number"
							bind:value={formData.sort_order}
							min="0"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
						<p class="text-xs text-gray-500 mt-1">Lower numbers appear first</p>
					</div>

					<!-- Active Status -->
					<div class="mb-6">
						<label class="flex items-center">
							<input
								type="checkbox"
								bind:checked={formData.is_active}
								class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
							/>
							<span class="ml-2 text-sm text-gray-700">Active</span>
						</label>
					</div>

					<!-- Error Display -->
					{#if error}
						<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
							{error}
						</div>
					{/if}

					<!-- Action Buttons -->
					<div class="flex gap-3">
						<button
							type="button"
							on:click={closeModal}
							class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
						>
							Cancel
						</button>
						<button
							type="submit"
							class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
						>
							{editingStation ? 'Update' : 'Create'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}
