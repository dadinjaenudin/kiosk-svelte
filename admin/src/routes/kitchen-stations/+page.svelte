<script>
	import { onMount } from 'svelte';
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

	let stations = [];
	let outlets = [];
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
			
			// Set default outlet from currentOutlet store
			if ($currentOutlet && outlets.find(o => o.id === $currentOutlet.id)) {
				filterOutletId = $currentOutlet.id;
			} else if (outlets.length > 0) {
				filterOutletId = outlets[0].id;
			}
		} catch (err) {
			console.error('Error loading outlets:', err);
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
			}
			
			const response = await getKitchenStations(params);
			stations = response.results || response || [];
			
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
		if (!confirm(`Are you sure you want to delete "${station.name}"?`)) {
			return;
		}

		try {
			await deleteKitchenStation(station.id);
			await loadStations();
		} catch (err) {
			console.error('Error deleting station:', err);
			error = 'Failed to delete station';
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
		await loadStations();
	});
</script>

<div class="p-6">
	<!-- Header -->
	<div class="mb-6">
		<div class="flex justify-between items-center">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">🍳 Kitchen Stations</h1>
				<p class="text-gray-600 mt-1">Manage kitchen stations for each outlet</p>
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
								<h3 class="text-xl font-bold text-gray-900">{station.name}</h3>
								<span class="px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-700">
									{station.code}
								</span>
							</div>
							<p class="text-sm text-gray-600">{getOutletName(station.outlet)}</p>
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
						<input
							type="text"
							bind:value={formData.code}
							required
							maxlength="20"
							placeholder="e.g., MAIN"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase"
							style="text-transform: uppercase;"
						/>
						<p class="text-xs text-gray-500 mt-1">Must be unique per outlet</p>
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
