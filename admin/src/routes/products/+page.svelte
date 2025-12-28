<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import {
		getProducts,
		getCategories,
		deleteProduct,
		duplicateProduct,
		bulkUpdateProducts,
		getProductStats,
		formatCurrency,
		formatDate
	} from '$lib/api/products';

	// Props
	export let data = {};

	// State
	let products = [];
	let categories = [];
	let stats = null;
	let isLoading = true;
	let error = null;
	let searchQuery = '';
	let selectedCategory = '';
	let selectedStatus = '';
	let selectedAvailability = '';
	let currentPage = 1;
	let totalPages = 1;
	let totalProducts = 0;

	// Filters
	let showFilters = false;
	let filters = {
		is_active: '',
		is_available: '',
		is_featured: '',
		has_promo: '',
		track_stock: ''
	};

	// Bulk actions
	let selectedProducts = [];
	let showBulkActions = false;

	// Delete confirmation
	let showDeleteModal = false;
	let productToDelete = null;

	// Load data
	async function loadProducts() {
		isLoading = true;
		error = null;

		try {
			const filterParams = {
				search: searchQuery || undefined,
				category: selectedCategory || undefined,
				is_active: filters.is_active !== '' ? filters.is_active : undefined,
				is_available: filters.is_available !== '' ? filters.is_available : undefined,
				is_featured: filters.is_featured !== '' ? filters.is_featured : undefined,
				has_promo: filters.has_promo !== '' ? filters.has_promo : undefined,
				track_stock: filters.track_stock !== '' ? filters.track_stock : undefined,
				page: currentPage,
				ordering: '-created_at'
			};

			const response = await getProducts(filterParams);
			products = response.results || response;
			totalProducts = response.count || products.length;
			totalPages = response.next || response.previous ? Math.ceil(totalProducts / 20) : 1;
		} catch (err) {
			console.error('Error loading products:', err);
			error = err.message || 'Failed to load products';
		} finally {
			isLoading = false;
		}
	}

	async function loadCategories() {
		try {
			const response = await getCategories({ is_active: true });
			categories = response.results || response;
		} catch (err) {
			console.error('Error loading categories:', err);
		}
	}

	async function loadStats() {
		try {
			stats = await getProductStats();
		} catch (err) {
			console.error('Error loading stats:', err);
		}
	}

	// Search handler
	function handleSearch() {
		currentPage = 1;
		loadProducts();
	}

	// Filter handler
	function handleFilterChange() {
		currentPage = 1;
		loadProducts();
	}

	// Pagination
	function goToPage(page) {
		currentPage = page;
		loadProducts();
	}

	// Delete product
	async function confirmDelete(product) {
		productToDelete = product;
		showDeleteModal = true;
	}

	async function handleDelete() {
		if (!productToDelete) return;

		try {
			await deleteProduct(productToDelete.id);
			showDeleteModal = false;
			productToDelete = null;
			loadProducts();
			loadStats();
		} catch (err) {
			console.error('Error deleting product:', err);
			alert('Failed to delete product: ' + (err.message || 'Unknown error'));
		}
	}

	// Duplicate product
	async function handleDuplicate(product) {
		if (!confirm(`Duplicate "${product.name}"?`)) return;

		try {
			await duplicateProduct(product.id);
			loadProducts();
		} catch (err) {
			console.error('Error duplicating product:', err);
			alert('Failed to duplicate product: ' + (err.message || 'Unknown error'));
		}
	}

	// Toggle product selection
	function toggleProductSelection(productId) {
		if (selectedProducts.includes(productId)) {
			selectedProducts = selectedProducts.filter((id) => id !== productId);
		} else {
			selectedProducts = [...selectedProducts, productId];
		}
	}

	// Select all products
	function toggleSelectAll() {
		if (selectedProducts.length === products.length) {
			selectedProducts = [];
		} else {
			selectedProducts = products.map((p) => p.id);
		}
	}

	// Bulk update
	async function handleBulkUpdate(updates) {
		if (selectedProducts.length === 0) {
			alert('No products selected');
			return;
		}

		try {
			await bulkUpdateProducts(selectedProducts, updates);
			selectedProducts = [];
			showBulkActions = false;
			loadProducts();
			loadStats();
		} catch (err) {
			console.error('Error bulk updating:', err);
			alert('Failed to update products: ' + (err.message || 'Unknown error'));
		}
	}

	// Get status badge class
	function getStatusBadge(product) {
		if (!product.is_active) return { class: 'bg-gray-100 text-gray-800', label: 'Inactive' };
		if (!product.is_available)
			return { class: 'bg-red-100 text-red-800', label: 'Unavailable' };
		if (product.is_low_stock) return { class: 'bg-yellow-100 text-yellow-800', label: 'Low Stock' };
		return { class: 'bg-green-100 text-green-800', label: 'Active' };
	}

	onMount(() => {
		if (!$isAuthenticated) {
			goto('/login');
			return;
		}

		loadProducts();
		loadCategories();
		loadStats();
	});
</script>

<svelte:head>
	<title>Products - Admin Panel</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Products</h1>
			<p class="text-gray-600 mt-1">Manage your product catalog</p>
		</div>
		<button
			on:click={() => goto('/products/create')}
			class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
		>
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 4v16m8-8H4"
				/>
			</svg>
			Add Product
		</button>
	</div>

	<!-- Stats Cards -->
	{#if stats}
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
			<div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
				<div class="text-sm text-gray-600">Total Products</div>
				<div class="text-2xl font-bold text-gray-900">{stats.total_products}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
				<div class="text-sm text-gray-600">Active</div>
				<div class="text-2xl font-bold text-green-600">{stats.active_products}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
				<div class="text-sm text-gray-600">Low Stock</div>
				<div class="text-2xl font-bold text-yellow-600">{stats.low_stock_products || 0}</div>
			</div>
			<div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
				<div class="text-sm text-gray-600">With Promo</div>
				<div class="text-2xl font-bold text-blue-600">{stats.products_with_promo}</div>
			</div>
		</div>
	{/if}

	<!-- Filters & Search -->
	<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
		<div class="flex flex-col md:flex-row gap-4">
			<!-- Search -->
			<div class="flex-1">
				<input
					type="text"
					bind:value={searchQuery}
					on:input={handleSearch}
					placeholder="Search products by name, SKU, or description..."
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
			</div>

			<!-- Category Filter -->
			<select
				bind:value={selectedCategory}
				on:change={handleFilterChange}
				class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			>
				<option value="">All Categories</option>
				{#each categories as category}
					<option value={category.id}>{category.name}</option>
				{/each}
			</select>

			<!-- Toggle Filters -->
			<button
				on:click={() => (showFilters = !showFilters)}
				class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center gap-2"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
					/>
				</svg>
				Filters
			</button>
		</div>

		<!-- Advanced Filters -->
		{#if showFilters}
			<div class="grid grid-cols-1 md:grid-cols-5 gap-4 mt-4 pt-4 border-t border-gray-200">
				<select bind:value={filters.is_active} on:change={handleFilterChange} class="px-4 py-2 border border-gray-300 rounded-lg">
					<option value="">All Status</option>
					<option value="true">Active</option>
					<option value="false">Inactive</option>
				</select>

				<select bind:value={filters.is_available} on:change={handleFilterChange} class="px-4 py-2 border border-gray-300 rounded-lg">
					<option value="">All Availability</option>
					<option value="true">Available</option>
					<option value="false">Unavailable</option>
				</select>

				<select bind:value={filters.is_featured} on:change={handleFilterChange} class="px-4 py-2 border border-gray-300 rounded-lg">
					<option value="">All Featured</option>
					<option value="true">Featured</option>
					<option value="false">Not Featured</option>
				</select>

				<select bind:value={filters.has_promo} on:change={handleFilterChange} class="px-4 py-2 border border-gray-300 rounded-lg">
					<option value="">All Promo</option>
					<option value="true">Has Promo</option>
					<option value="false">No Promo</option>
				</select>

				<button
					on:click={() => {
						filters = {
							is_active: '',
							is_available: '',
							is_featured: '',
							has_promo: '',
							track_stock: ''
						};
						handleFilterChange();
					}}
					class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
				>
					Clear Filters
				</button>
			</div>
		{/if}
	</div>

	<!-- Bulk Actions -->
	{#if selectedProducts.length > 0}
		<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-center justify-between">
			<div class="flex items-center gap-4">
				<span class="text-blue-900 font-medium">{selectedProducts.length} product(s) selected</span>
				<button
					on:click={() => (showBulkActions = !showBulkActions)}
					class="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
				>
					Bulk Actions
				</button>
			</div>
			<button on:click={() => (selectedProducts = [])} class="text-blue-600 hover:text-blue-800">
				Clear Selection
			</button>
		</div>

		{#if showBulkActions}
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
				<div class="flex flex-wrap gap-2">
					<button
						on:click={() => handleBulkUpdate({ is_active: true })}
						class="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm"
					>
						Activate
					</button>
					<button
						on:click={() => handleBulkUpdate({ is_active: false })}
						class="px-3 py-1 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition text-sm"
					>
						Deactivate
					</button>
					<button
						on:click={() => handleBulkUpdate({ is_available: true })}
						class="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
					>
						Make Available
					</button>
					<button
						on:click={() => handleBulkUpdate({ is_available: false })}
						class="px-3 py-1 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm"
					>
						Make Unavailable
					</button>
					<button
						on:click={() => handleBulkUpdate({ is_featured: true })}
						class="px-3 py-1 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm"
					>
						Feature
					</button>
				</div>
			</div>
		{/if}
	{/if}

	<!-- Products Table -->
	<div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
		{#if isLoading}
			<div class="flex items-center justify-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
			</div>
		{:else if error}
			<div class="text-center py-12">
				<p class="text-red-600 mb-4">{error}</p>
				<button
					on:click={loadProducts}
					class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
				>
					Retry
				</button>
			</div>
		{:else if products.length === 0}
			<div class="text-center py-12">
				<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
				</svg>
				<p class="text-gray-600 mt-4 mb-2">No products found</p>
				<button
					on:click={() => goto('/products/create')}
					class="text-blue-600 hover:text-blue-800"
				>
					Create your first product
				</button>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead class="bg-gray-50 border-b border-gray-200">
						<tr>
							<th class="px-6 py-3 text-left">
								<input
									type="checkbox"
									checked={selectedProducts.length === products.length && products.length > 0}
									on:change={toggleSelectAll}
									class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
								/>
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Image</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each products as product}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4">
									<input
										type="checkbox"
										checked={selectedProducts.includes(product.id)}
										on:change={() => toggleProductSelection(product.id)}
										class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
									/>
								</td>
								<td class="px-6 py-4">
									{#if product.image}
										<img src={product.image} alt={product.name} class="w-16 h-16 object-cover rounded" />
									{:else}
										<div class="w-16 h-16 bg-gray-200 rounded flex items-center justify-center">
											<svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
											</svg>
										</div>
									{/if}
								</td>
								<td class="px-6 py-4">
									<div class="font-medium text-gray-900">{product.name}</div>
									<div class="text-sm text-gray-500">SKU: {product.sku}</div>
								</td>
								<td class="px-6 py-4 text-sm text-gray-900">
									{product.category_name || '-'}
								</td>
								<td class="px-6 py-4">
									<div class="font-medium text-gray-900">{formatCurrency(product.price)}</div>
									{#if product.has_promo && product.promo_price}
										<div class="text-sm text-green-600">{formatCurrency(product.promo_price)}</div>
									{/if}
								</td>
								<td class="px-6 py-4 text-sm">
									{#if product.track_stock}
										<span class:text-red-600={product.is_low_stock} class:text-gray-900={!product.is_low_stock}>
											{product.stock_quantity}
										</span>
									{:else}
										<span class="text-gray-400">N/A</span>
									{/if}
								</td>
								<td class="px-6 py-4">
									{@const badge = getStatusBadge(product)}
									<span class="px-2 py-1 text-xs font-medium rounded-full {badge.class}">
										{badge.label}
									</span>
								</td>
								<td class="px-6 py-4 text-sm">
									<div class="flex items-center gap-2">
										<button
											on:click={() => goto(`/products/${product.id}/edit`)}
											class="text-blue-600 hover:text-blue-800"
											title="Edit"
										>
											<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
											</svg>
										</button>
										<button
											on:click={() => handleDuplicate(product)}
											class="text-green-600 hover:text-green-800"
											title="Duplicate"
										>
											<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
											</svg>
										</button>
										<button
											on:click={() => confirmDelete(product)}
											class="text-red-600 hover:text-red-800"
											title="Delete"
										>
											<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
											</svg>
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
						Showing page {currentPage} of {totalPages} ({totalProducts} total products)
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
								class="px-3 py-1 border rounded-lg {currentPage === page
									? 'bg-blue-600 text-white border-blue-600'
									: 'border-gray-300 hover:bg-gray-50'}"
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

<!-- Delete Confirmation Modal -->
{#if showDeleteModal && productToDelete}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
		<div class="bg-white rounded-lg max-w-md w-full p-6">
			<h2 class="text-xl font-bold text-gray-900 mb-4">Delete Product</h2>
			<p class="text-gray-600 mb-6">
				Are you sure you want to delete "<strong>{productToDelete.name}</strong>"? This action
				cannot be undone.
			</p>
			<div class="flex gap-2 justify-end">
				<button
					on:click={() => {
						showDeleteModal = false;
						productToDelete = null;
					}}
					class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
				>
					Cancel
				</button>
				<button
					on:click={handleDelete}
					class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
				>
					Delete
				</button>
			</div>
		</div>
	</div>
{/if}
