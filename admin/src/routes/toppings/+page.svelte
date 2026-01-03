<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isAuthenticated, selectedTenant } from '$lib/stores/auth';
	import {
		getModifiers,
		createModifier,
		updateModifier,
		deleteModifier,
		getModifierStats,
		bulkUpdateModifiers,
		formatModifierType,
		formatPriceAdjustment
	} from '$lib/api/modifiers';
	import { getProducts } from '$lib/api/products';
	import { getTenants } from '$lib/api/tenants';

	export let data = {};

	// State
	let modifiers = [];
	let products = [];
	let tenants = [];
	let loading = true;
	let stats = { total: 0, active: 0, inactive: 0 };
	let mounted = false;
	
	// Toast notification state
	let showToast = false;
	let toastMessage = '';
	let toastType = 'success'; // 'success' | 'error' | 'info'
	
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

	// Show alert function with toast
	function showAlert(message, type = 'success') {
		toastMessage = message;
		toastType = type;
		showToast = true;
		
		// Auto hide after 3 seconds
		setTimeout(() => {
			showToast = false;
		}, 3000);
	}

	onMount(() => {
		loadModifiers();
		loadProducts();
		loadTenants();
		loadStats();
		mounted = true;
	});

	// Reactive: reload when tenant filter changes
	$: if (mounted) {
		const tenantId = $selectedTenant;
		currentPage = 1;
		loadModifiers();
	}

	async function loadModifiers() {
		loading = true;
		try {
			// Build filters object, only include non-empty values
			const filters = {
				type: 'topping',
				page: currentPage,
				page_size: 10,
				ordering: 'sort_order,name'
			};
			
			if (searchQuery) filters.search = searchQuery;
			if (selectedProduct) filters.product = selectedProduct;
			if ($selectedTenant) filters.tenant = $selectedTenant;
			if (isActiveFilter !== '') filters.is_active = isActiveFilter;
			
			const response = await getModifiers(filters);
			
			modifiers = response.results || response;
			totalCount = response.count || modifiers.length;
			// Calculate total pages properly (default page size is 10)
			totalPages = totalCount > 0 ? Math.ceil(totalCount / 10) : 1;
			
			// If current page exceeds total pages, go to last valid page
			if (currentPage > totalPages && totalPages > 0) {
				currentPage = totalPages;
				loadModifiers();
				return;
			}
		} catch (error) {
			console.error('Error loading toppings:', error);
			// If invalid page error and not already on page 1, reset to page 1
			if (error.message && error.message.includes('Invalid page') && currentPage !== 1) {
				currentPage = 1;
				loadModifiers();  // Retry with page 1
				return;
			}
			showAlert('Failed to load toppings', 'error');
		} finally {
			loading = false;
		}
	}

	async function loadProducts() {
		try {
			console.log('Loading products with page_size: 1000');
			const response = await getProducts({ page_size: 1000 });
			console.log('Products API response:', response);
			console.log('Response has results?', !!response.results);
			products = response.results || response;
			console.log('Products array length:', products.length);
			console.log('First 3 products:', products.slice(0, 3));
		} catch (error) {
			console.error('Error loading products:', error);
		}
	}

	async function loadTenants() {
		try {
			const response = await getTenants({ page_size: 100 });
			tenants = response.results || response;
		} catch (error) {
			console.error('Error loading tenants:', error);
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
		console.log('Opening edit modal for modifier:', modifier);
		console.log('modifier.product_id:', modifier.product_id);
		console.log('modifier.product:', modifier.product);
		console.log('Available products:', products.length);
		
		editingModifier = modifier;
		formData = {
			name: modifier.name,
			type: modifier.type,
			price_adjustment: modifier.price_adjustment,
			product: modifier.product_id || modifier.product,
			is_active: modifier.is_active,
			sort_order: modifier.sort_order
		};
		console.log('Form data after setting:', formData);
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
				showAlert('Topping updated successfully!', 'success');
			} else {
				await createModifier(formData);
				showAlert('Topping created successfully!', 'success');
			}
			
			showCreateModal = false;
			currentPage = 1;  // Reset to first page
			loadModifiers();
			loadStats();
		} catch (error) {
			console.error('Error saving topping:', error);
			showAlert('Failed to save topping: ' + (error.message || 'Unknown error'), 'error');
		}
	}

	function handleCopy(modifier) {
		// Open create modal with copied data
		editingModifier = null;
		formData = {
			name: modifier.name + ' (Copy)',
			type: modifier.type,
			price_adjustment: modifier.price_adjustment,
			product: modifier.product || '',
			is_active: modifier.is_active,
			sort_order: modifier.sort_order
		};
		formErrors = {};
		showCreateModal = true;
		showAlert('Topping copied! Modify and save to create.', 'info');
	}

	function confirmDelete(modifier) {
		modifierToDelete = modifier;
		showDeleteModal = true;
	}

	async function handleDelete() {
		if (!modifierToDelete) return;
		
		try {
			await deleteModifier(modifierToDelete.id);
			showAlert('Topping deleted successfully!', 'success');
			showDeleteModal = false;
			modifierToDelete = null;
			currentPage = 1;  // Reset to first page
			loadModifiers();
			loadStats();
		} catch (error) {
			console.error('Error deleting topping:', error);
			showAlert('Failed to delete topping', 'error');
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
										on:click={() => handleCopy(modifier)}
										class="text-green-600 hover:text-green-800"
										title="Copy"
									>
										📋
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
						
						{#if currentPage > 3}
							<button
								on:click={() => goToPage(1)}
								class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50"
							>
								1
							</button>
							{#if currentPage > 4}
								<span class="px-3 py-1">...</span>
							{/if}
						{/if}
						
						{#each Array(Math.min(5, totalPages)) as _, i}
							{@const startPage = Math.max(1, Math.min(currentPage - 2, totalPages - 4))}
							{@const page = startPage + i}
							{#if page <= totalPages}
								<button
									on:click={() => goToPage(page)}
									class="px-3 py-1 border rounded-lg {currentPage === page ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 hover:bg-gray-50'}"
								>
									{page}
								</button>
							{/if}
						{/each}
						
						{#if currentPage < totalPages - 2}
							{#if currentPage < totalPages - 3}
								<span class="px-3 py-1">...</span>
							{/if}
							<button
								on:click={() => goToPage(totalPages)}
								class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50"
							>
								{totalPages}
							</button>
						{/if}
						
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
						<option value="">Select product ({products.length} available)</option>
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

<!-- Toast Notification -->
{#if showToast}
	<div class="fixed bottom-4 right-4 z-50 animate-fade-in">
		<div class="bg-white rounded-lg shadow-lg border-l-4 {toastType === 'success' ? 'border-green-500' : toastType === 'error' ? 'border-red-500' : 'border-blue-500'} p-4 min-w-[300px] max-w-md">
			<div class="flex items-start">
				<div class="flex-shrink-0">
					{#if toastType === 'success'}
						<svg class="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					{:else if toastType === 'error'}
						<svg class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					{:else}
						<svg class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					{/if}
				</div>
				<div class="ml-3 flex-1">
					<p class="text-sm font-medium text-gray-900">{toastMessage}</p>
				</div>
				<button on:click={() => showToast = false} class="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600">
					<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
					</svg>
				</button>
			</div>
		</div>
	</div>
{/if}
