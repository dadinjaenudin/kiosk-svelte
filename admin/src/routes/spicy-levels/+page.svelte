<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { isAuthenticated, selectedTenant } from '$lib/stores/auth';
	import {
		getModifiers,
		createModifier,
		updateModifier,
		deleteModifier,
		getModifierStats,
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
	
	// Modals
	let showDeleteModal = false;
	let modifierToDelete = null;
	let showCreateModal = false;
	let editingModifier = null;
	
	// Form data
	let formData = {
		name: '',
		type: 'spicy',
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
	$: if (mounted && $selectedTenant !== undefined) {
		console.log('🔄 Spicy Levels: Reactive reload triggered. Tenant:', $selectedTenant);
		const tenantId = $selectedTenant;
		currentPage = 1;
		loadModifiers();
		loadStats();
	}

	async function loadModifiers() {
		if (!browser) return;
		loading = true;
		try {
			const filters = {
				type: 'spicy',
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
			totalPages = totalCount > 0 ? Math.ceil(totalCount / 10) : 1;
			
			if (currentPage > totalPages && totalPages > 0) {
				currentPage = totalPages;
				loadModifiers();
				return;
			}
		} catch (error) {
			console.error('Error loading spicy levels:', error);
			if (error.message && error.message.includes('Invalid page') && currentPage !== 1) {
				currentPage = 1;
				loadModifiers();
				return;
			}
			showAlert('Failed to load spicy levels', 'error');
		} finally {
			loading = false;
		}
	}

	async function loadProducts() {
		if (!browser) return;
		try {
			const response = await getProducts({ page_size: 1000 });
			products = response.results || response;
		} catch (error) {
			console.error('Error loading products:', error);
		}
	}

	async function loadTenants() {
		if (!browser) return;
		try {
			const response = await getTenants({ page_size: 100 });
			tenants = response.results || response;
		} catch (error) {
			console.error('Error loading tenants:', error);
		}
	}

	async function loadStats() {
		if (!browser) return;
		try {
			const allStats = await getModifierStats();
			stats.total = allStats.by_type?.spicy || 0;
			
			const activeResponse = await getModifiers({ type: 'spicy', is_active: true });
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
		currentPage = 1;
		loadModifiers();
	}

	function openCreateModal() {
		editingModifier = null;
		formData = {
			name: '',
			type: 'spicy',
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
			product: modifier.product || '',
			is_active: modifier.is_active,
			sort_order: modifier.sort_order
		};
		formErrors = {};
		showCreateModal = true;
	}

	function closeModal() {
		showCreateModal = false;
		editingModifier = null;
		formErrors = {};
	}

	async function handleSubmit() {
		formErrors = {};
		
		// Validation
		if (!formData.name.trim()) {
			formErrors.name = 'Name is required';
			return;
		}
		
		try {
			const submitData = {
				...formData,
				product: formData.product || null,
				price_adjustment: parseFloat(formData.price_adjustment) || 0
			};
			
			if (editingModifier) {
				await updateModifier(editingModifier.id, submitData);
				showAlert('Spicy level updated successfully!', 'success');
			} else {
				await createModifier(submitData);
				showAlert('Spicy level created successfully!', 'success');
			}
			
			closeModal();
			loadModifiers();
			loadStats();
		} catch (error) {
			console.error('Error saving spicy level:', error);
			if (error.message) {
				formErrors.general = error.message;
			} else {
				showAlert('Failed to save spicy level', 'error');
			}
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
			showAlert('Spicy level deleted successfully!', 'success');
			showDeleteModal = false;
			modifierToDelete = null;
			loadModifiers();
			loadStats();
		} catch (error) {
			console.error('Error deleting spicy level:', error);
			showAlert('Failed to delete spicy level', 'error');
		}
	}

	function getProductName(productId) {
		if (!productId) return 'Global';
		const product = products.find(p => p.id === productId);
		return product ? product.name : '-';
	}
</script>

<svelte:head>
	<title>Spicy Levels - Admin Panel</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="flex justify-between items-center mb-6">
		<div>
			<h1 class="text-2xl font-bold text-gray-800">🌶️ Spicy Levels</h1>
			<p class="text-gray-600 mt-1">Manage spicy level options for your products</p>
		</div>
		<button
			on:click={openCreateModal}
			class="btn btn-primary"
		>
			<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			Add Spicy Level
		</button>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
		<div class="card">
			<div class="flex items-center">
				<div class="p-3 rounded-full bg-blue-100 text-blue-600 mr-4">
					<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
					</svg>
				</div>
				<div>
					<p class="text-sm text-gray-600">Total Levels</p>
					<p class="text-2xl font-bold text-gray-800">{stats.total}</p>
				</div>
			</div>
		</div>

		<div class="card">
			<div class="flex items-center">
				<div class="p-3 rounded-full bg-green-100 text-green-600 mr-4">
					<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<div>
					<p class="text-sm text-gray-600">Active</p>
					<p class="text-2xl font-bold text-gray-800">{stats.active}</p>
				</div>
			</div>
		</div>

		<div class="card">
			<div class="flex items-center">
				<div class="p-3 rounded-full bg-gray-100 text-gray-600 mr-4">
					<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
					</svg>
				</div>
				<div>
					<p class="text-sm text-gray-600">Inactive</p>
					<p class="text-2xl font-bold text-gray-800">{stats.inactive}</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Filters -->
	<div class="card mb-6">
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
			<!-- Search -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
				<input
					type="text"
					bind:value={searchQuery}
					on:input={handleSearch}
					placeholder="Search spicy levels..."
					class="input-field"
				/>
			</div>

			<!-- Product Filter -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Product</label>
				<select
					bind:value={selectedProduct}
					on:change={handleFilterChange}
					class="input-field"
				>
					<option value="">All Products</option>
					<option value="null">Global (No Product)</option>
					{#each products as product}
						<option value={product.id}>{product.name}</option>
					{/each}
				</select>
			</div>

			<!-- Status Filter -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
				<select
					bind:value={isActiveFilter}
					on:change={handleFilterChange}
					class="input-field"
				>
					<option value="">All Status</option>
					<option value="true">Active</option>
					<option value="false">Inactive</option>
				</select>
			</div>

			<!-- Results -->
			<div class="flex items-end">
				<div class="text-sm text-gray-600">
					Showing {modifiers.length} of {totalCount} spicy levels
				</div>
			</div>
		</div>
	</div>

	<!-- Table -->
	<div class="card overflow-hidden">
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			</div>
		{:else if modifiers.length === 0}
			<div class="text-center py-12">
				<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
				</svg>
				<p class="mt-2 text-gray-600">No spicy levels found</p>
				<button
					on:click={openCreateModal}
					class="btn btn-primary mt-4"
				>
					Add First Spicy Level
				</button>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Level Name
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Product
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Price Adjustment
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Sort Order
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Status
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Actions
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each modifiers as modifier}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="flex items-center">
										<span class="text-2xl mr-2">🌶️</span>
										<div class="text-sm font-medium text-gray-900">{modifier.name}</div>
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{getProductName(modifier.product)}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{formatPriceAdjustment(modifier.price_adjustment)}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{modifier.sort_order}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="px-2 py-1 text-xs font-medium rounded-full {modifier.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
										{modifier.is_active ? 'Active' : 'Inactive'}
									</span>
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
			</div>

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
		<div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
			<div class="p-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">
					{editingModifier ? 'Edit Spicy Level' : 'Add Spicy Level'}
				</h3>

				<form on:submit|preventDefault={handleSubmit}>
					<!-- Name -->
					<div class="mb-4">
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Level Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.name}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="e.g., Level 1 (Tidak Pedas)"
							required
						/>
						{#if formErrors.name}
							<p class="text-red-500 text-sm mt-1">{formErrors.name}</p>
						{/if}
					</div>

					<!-- Product (Optional) -->
					<div class="mb-4">
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Product (Optional)
						</label>
						<select
							bind:value={formData.product}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
						>
							<option value="">Global (All Products)</option>
							{#each products as product}
								<option value={product.id}>{product.name}</option>
							{/each}
						</select>
						<p class="text-sm text-gray-500 mt-1">Leave empty to make this level available for all products</p>
					</div>

					<!-- Price Adjustment -->
					<div class="mb-4">
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
						<p class="text-sm text-gray-500 mt-1">Extra charge for this spicy level (usually 0)</p>
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
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="0"
						/>
						<p class="text-sm text-gray-500 mt-1">Lower numbers appear first</p>
					</div>

					<!-- Active Status -->
					<div class="mb-4">
						<label class="flex items-center">
							<input
								type="checkbox"
								bind:checked={formData.is_active}
								class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
							/>
							<span class="ml-2 text-sm text-gray-700">Active</span>
						</label>
					</div>

					{#if formErrors.general}
						<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
							{formErrors.general}
						</div>
					{/if}

					<!-- Actions -->
					<div class="flex gap-3">
						<button
							type="button"
							on:click={closeModal}
							class="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
						>
							Cancel
						</button>
						<button
							type="submit"
							class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
						>
							{editingModifier ? 'Update' : 'Create'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
			<div class="p-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Delete Spicy Level</h3>
				<p class="text-gray-600 mb-6">
					Are you sure you want to delete "<strong>{modifierToDelete?.name}</strong>"? This action cannot be undone.
				</p>
				<div class="flex gap-3">
					<button
						on:click={() => { showDeleteModal = false; modifierToDelete = null; }}
						class="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
					>
						Cancel
					</button>
					<button
						on:click={handleDelete}
						class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
					>
						Delete
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Toast Notification -->
{#if showToast}
	<div class="fixed bottom-4 right-4 z-50 animate-slide-up">
		<div class="rounded-lg shadow-lg p-4 {toastType === 'success' ? 'bg-green-500' : toastType === 'error' ? 'bg-red-500' : 'bg-blue-500'} text-white">
			<div class="flex items-center">
				{#if toastType === 'success'}
					<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
				{:else if toastType === 'error'}
					<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				{/if}
				<span>{toastMessage}</span>
			</div>
		</div>
	</div>
{/if}

<style>
	@keyframes slide-up {
		from {
			transform: translateY(100%);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.animate-slide-up {
		animation: slide-up 0.3s ease-out;
	}
</style>
