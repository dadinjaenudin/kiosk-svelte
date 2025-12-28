<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import {
		getModifiers,
		deleteModifier,
		getModifierStats,
		bulkUpdateModifiers,
		formatModifierType,
		formatPriceAdjustment
	} from '$lib/api/modifiers';
	import { getProducts } from '$lib/api/products';

	export let data = {};

	// State
	let modifiers = [];
	let products = [];
	let loading = true;
	let stats = { total: 0, active: 0, inactive: 0 };
	
	// Filters
	let searchQuery = '';
	let selectedProduct = '';
	let isActiveFilter = '';
	
	// Pagination
	let currentPage = 1;
	let totalPages = 1;
	let totalCount = 0;
	
	// Bulk actions
	let selectedModifiers = [];
	let bulkAction = '';
	
	// Modals
	let showDeleteModal = false;
	let modifierToDelete = null;
	let showCreateModal = false;
	let editingModifier = null;
	
	// Form data
	let formData = {
		name: '',
		type: 'topping',
		price_adjustment: 0,
		product: '',
		is_active: true,
		sort_order: 0
	};
	let formErrors = {};

	onMount(() => {
		if (!$isAuthenticated) {
			goto('/login');
			return;
		}
		
		loadModifiers();
		loadProducts();
		loadStats();
	});

	async function loadModifiers() {
		loading = true;
		try {
			const response = await getModifiers({
				type: 'topping',
				search: searchQuery,
				product: selectedProduct,
				is_active: isActiveFilter,
				page: currentPage,
				ordering: 'sort_order,name'
			});
			
			modifiers = response.results || response;
			totalCount = response.count || modifiers.length;
			totalPages = response.next ? Math.ceil(totalCount / 10) : 1;
		} catch (error) {
			console.error('Error loading toppings:', error);
			alert('Failed to load toppings');
		} finally {
			loading = false;
		}
	}

	async function loadProducts() {
		try {
			const response = await getProducts({ page_size: 1000 });
			products = response.results || response;
		} catch (error) {
			console.error('Error loading products:', error);
		}
	}

	async function loadStats() {
		try {
			const allStats = await getModifierStats();
			stats.total = allStats.by_type?.topping || 0;
			
			// Load active/inactive counts for toppings only
			const activeResponse = await getModifiers({ type: 'topping', is_active: true });
			stats.active = activeResponse.count || (activeResponse.results || activeResponse).length;
			stats.inactive = stats.total - stats.active;
		} catch (error) {
			console.error('Error loading stats:', error);
		}
	}

	function handleSearch() {
		currentPage = 1;
		loadModifiers();
	}

	function handleFilterChange() {
		currentPage = 1;
		loadModifiers();
	}

	function goToPage(page) {
		currentPage = page;
		loadModifiers();
	}

	function openCreateModal() {
		editingModifier = null;
		formData = {
			name: '',
			type: 'topping',
			price_adjustment: 0,
			product: '',
			is_active: true,
			sort_order: 0
		};
		formErrors = {};
		showCreateModal = true;
	}

	function openEditModal(modifier) {
		editingModifier = modifier;
		formData = {
			name: modifier.name,
			type: modifier.type,
			price_adjustment: modifier.price_adjustment,
			product: modifier.product_id,
			is_active: modifier.is_active,
			sort_order: modifier.sort_order
		};
		formErrors = {};
		showCreateModal = true;
	}

	function validateForm() {
		formErrors = {};
		
		if (!formData.name?.trim()) {
			formErrors.name = 'Name is required';
		}
		
		if (!formData.product) {
			formErrors.product = 'Product is required';
		}
		
		return Object.keys(formErrors).length === 0;
	}

	async function handleSubmit() {
		if (!validateForm()) return;
		
		try {
			if (editingModifier) {
				await updateModifier(editingModifier.id, formData);
			} else {
				await createModifier(formData);
			}
			
			showCreateModal = false;
			loadModifiers();
			loadStats();
		} catch (error) {
			console.error('Error saving topping:', error);
			alert('Failed to save topping: ' + (error.message || 'Unknown error'));
		}
	}

	function confirmDelete(modifier) {
		modifierToDelete = modifier;
		showDeleteModal = true;
	}

	async function handleDelete() {
		if (!modifierToDelete) return;
		
		try {
			await deleteModifier(modifierToDelete.id);
			showDeleteModal = false;
			modifierToDelete = null;
			loadModifiers();
			loadStats();
		} catch (error) {
			console.error('Error deleting topping:', error);
			alert('Failed to delete topping');
		}
	}

	function toggleSelectModifier(modifierId) {
		if (selectedModifiers.includes(modifierId)) {
			selectedModifiers = selectedModifiers.filter(id => id !== modifierId);
		} else {
			selectedModifiers = [...selectedModifiers, modifierId];
		}
	}

	function toggleSelectAll() {
		if (selectedModifiers.length === modifiers.length) {
			selectedModifiers = [];
		} else {
			selectedModifiers = modifiers.map(m => m.id);
		}
	}

	async function handleBulkAction() {
		if (!bulkAction || selectedModifiers.length === 0) return;
		
		const updates = {};
		if (bulkAction === 'activate') updates.is_active = true;
		if (bulkAction === 'deactivate') updates.is_active = false;
		
		if (Object.keys(updates).length === 0) return;
		
		try {
			await bulkUpdateModifiers(selectedModifiers, updates);
			selectedModifiers = [];
			bulkAction = '';
			loadModifiers();
			loadStats();
		} catch (error) {
			console.error('Error applying bulk action:', error);
			alert('Failed to apply bulk action');
		}
	}
</script>

<svelte:head>
	<title>Toppings - Admin Panel</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Toppings</h1>
			<p class="text-gray-600 mt-1">Manage product toppings and add-ons</p>
		</div>
		<button
			on:click={openCreateModal}
			class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
		>
			<span>➕</span>
			<span>Add Topping</span>
		</button>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Total Toppings</p>
					<p class="text-2xl font-bold text-gray-900 mt-2">{stats.total}</p>
				</div>
				<div class="bg-blue-100 p-3 rounded-lg">
					<span class="text-2xl">🧀</span>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Active</p>
					<p class="text-2xl font-bold text-green-600 mt-2">{stats.active}</p>
				</div>
				<div class="bg-green-100 p-3 rounded-lg">
					<span class="text-2xl">✅</span>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Inactive</p>
					<p class="text-2xl font-bold text-gray-600 mt-2">{stats.inactive}</p>
				</div>
				<div class="bg-gray-100 p-3 rounded-lg">
					<span class="text-2xl">❌</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Filters & Search -->
	<div class="bg-white rounded-lg shadow p-6 mb-6">
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
			<!-- Search -->
			<div class="md:col-span-2">
				<label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
				<input
					type="text"
					bind:value={searchQuery}
					on:input={handleSearch}
					placeholder="Search by name..."
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<!-- Product Filter -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Product</label>
				<select
					bind:value={selectedProduct}
					on:change={handleFilterChange}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				>
					<option value="">All Products</option>
					{#each products as product}
						<option value={product.id}>{product.name}</option>
					{/each}
				</select>
			</div>

			<!-- Active Filter -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
				<select
					bind:value={isActiveFilter}
					on:change={handleFilterChange}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				>
					<option value="">All Status</option>
					<option value="true">Active</option>
					<option value="false">Inactive</option>
				</select>
			</div>
		</div>
	</div>

	<!-- Bulk Actions -->
	{#if selectedModifiers.length > 0}
		<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-center gap-4">
			<span class="text-blue-900 font-medium">{selectedModifiers.length} selected</span>
			<select
				bind:value={bulkAction}
				class="px-4 py-2 border border-blue-300 rounded-lg bg-white"
			>
				<option value="">Choose action...</option>
				<option value="activate">Activate</option>
				<option value="deactivate">Deactivate</option>
			</select>
			<button
				on:click={handleBulkAction}
				disabled={!bulkAction}
				class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
			>
				Apply
			</button>
		</div>
	{/if}

	<!-- Table -->
	<div class="bg-white rounded-lg shadow overflow-hidden">
		{#if loading}
			<div class="p-12 text-center">
				<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
				<p class="text-gray-600 mt-4">Loading toppings...</p>
			</div>
		{:else if modifiers.length === 0}
			<div class="p-12 text-center">
				<span class="text-6xl">🧀</span>
				<p class="text-xl font-medium text-gray-900 mt-4">No toppings found</p>
				<p class="text-gray-600 mt-2">Create your first topping to get started</p>
				<button
					on:click={openCreateModal}
					class="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Add Topping
				</button>
			</div>
		{:else}
			<table class="min-w-full divide-y divide-gray-200">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-6 py-3 text-left">
							<input
								type="checkbox"
								checked={selectedModifiers.length === modifiers.length}
								on:change={toggleSelectAll}
								class="rounded border-gray-300"
							/>
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each modifiers as modifier}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4">
								<input
									type="checkbox"
									checked={selectedModifiers.includes(modifier.id)}
									on:change={() => toggleSelectModifier(modifier.id)}
									class="rounded border-gray-300"
								/>
							</td>
							<td class="px-6 py-4 text-sm font-medium text-gray-900">
								{modifier.name}
							</td>
							<td class="px-6 py-4 text-sm text-gray-600">
								{modifier.product_name}
							</td>
							<td class="px-6 py-4 text-sm font-medium text-gray-900">
								{formatPriceAdjustment(modifier.price_adjustment)}
							</td>
							<td class="px-6 py-4">
								{#if true}
									{@const status = modifier.is_active}
									<span class="px-2 py-1 text-xs font-medium rounded-full {status ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
										{status ? 'Active' : 'Inactive'}
									</span>
								{/if}
							</td>
							<td class="px-6 py-4 text-sm">
								<div class="flex items-center gap-2">
									<button
										on:click={() => openEditModal(modifier)}
										class="text-blue-600 hover:text-blue-800"
										title="Edit"
									>
										✏️
									</button>
									<button
										on:click={() => confirmDelete(modifier)}
										class="text-red-600 hover:text-red-800"
										title="Delete"
									>
										🗑️
									</button>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>

			<!-- Pagination -->
			{#if totalPages > 1}
				<div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
					<div class="text-sm text-gray-700">
						Showing page {currentPage} of {totalPages} ({totalCount} total)
					</div>
					<div class="flex gap-2">
						<button
							on:click={() => goToPage(currentPage - 1)}
							disabled={currentPage === 1}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Previous
						</button>
						{#each Array(Math.min(5, totalPages)) as _, i}
							{@const page = i + 1}
							<button
								on:click={() => goToPage(page)}
								class="px-3 py-1 border rounded-lg {currentPage === page ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 hover:bg-gray-50'}"
							>
								{page}
							</button>
						{/each}
						<button
							on:click={() => goToPage(currentPage + 1)}
							disabled={currentPage === totalPages}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Next
						</button>
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>

<!-- Create/Edit Modal -->
{#if showCreateModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
			<div class="p-6 border-b border-gray-200">
				<h2 class="text-2xl font-bold text-gray-900">
					{editingModifier ? 'Edit Topping' : 'Add New Topping'}
				</h2>
			</div>
			
			<form on:submit|preventDefault={handleSubmit} class="p-6 space-y-4">
				<!-- Name -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">
						Name <span class="text-red-500">*</span>
					</label>
					<input
						type="text"
						bind:value={formData.name}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
						placeholder="e.g., Extra Cheese"
					/>
					{#if formErrors.name}
						<p class="text-red-500 text-sm mt-1">{formErrors.name}</p>
					{/if}
				</div>

				<!-- Product -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">
						Product <span class="text-red-500">*</span>
					</label>
					<select
						bind:value={formData.product}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
					>
						<option value="">Select product</option>
						{#each products as product}
							<option value={product.id}>{product.name}</option>
						{/each}
					</select>
					{#if formErrors.product}
						<p class="text-red-500 text-sm mt-1">{formErrors.product}</p>
					{/if}
				</div>

				<!-- Price Adjustment -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">
						Price Adjustment
					</label>
					<div class="relative">
						<span class="absolute left-3 top-2 text-gray-500">Rp</span>
						<input
							type="number"
							bind:value={formData.price_adjustment}
							step="100"
							class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="0"
						/>
					</div>
					<p class="text-sm text-gray-500 mt-1">Use 0 for free toppings</p>
				</div>

				<!-- Sort Order -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">
						Sort Order
					</label>
					<input
						type="number"
						bind:value={formData.sort_order}
						min="0"
						class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
						placeholder="0"
					/>
				</div>

				<!-- Is Active -->
				<div>
					<label class="flex items-center">
						<input
							type="checkbox"
							bind:checked={formData.is_active}
							class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
						/>
						<span class="ml-2 text-sm text-gray-700">Active</span>
					</label>
				</div>

				<!-- Actions -->
				<div class="flex items-center justify-end gap-4 pt-4 border-t border-gray-200">
					<button
						type="button"
						on:click={() => showCreateModal = false}
						class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
					>
						Cancel
					</button>
					<button
						type="submit"
						class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
					>
						{editingModifier ? 'Update' : 'Create'} Topping
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
			<h3 class="text-lg font-bold text-gray-900 mb-4">Confirm Delete</h3>
			<p class="text-gray-600 mb-6">
				Are you sure you want to delete "{modifierToDelete?.name}"? This action cannot be undone.
			</p>
			<div class="flex items-center justify-end gap-4">
				<button
					on:click={() => { showDeleteModal = false; modifierToDelete = null; }}
					class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
				>
					Cancel
				</button>
				<button
					on:click={handleDelete}
					class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
				>
					Delete
				</button>
			</div>
		</div>
	</div>
{/if}
