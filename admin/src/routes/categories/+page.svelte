<script>
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { browser } from '$app/environment';
	import Swal from 'sweetalert2';
	import { authFetch } from '$lib/api/auth';
	import { getTenants } from '$lib/api/tenants';
	import { getKitchenStationTypes } from '$lib/api/kitchenStationTypes';
	import { user, selectedTenant } from '$lib/stores/auth';
	
	let tenants = [];
	let stationTypes = []; // Kitchen Station Types for routing
	let categories = []; // Categories list
	let currentUser = null;
	let mounted = false;
	
	let stats = {
		total_categories: 0,
		active_categories: 0,
		inactive_categories: 0,
		categories_with_products: 0
	};
	let loading = false;
	let showTenantField = false;
	let errors = {};

	// Filters
	let searchQuery = '';
	let statusFilter = '';

	// Pagination
	let currentPage = 1;
	let totalPages = 1;
	let totalCount = 0;

	// Modals
	let showModal = false;
	let editingCategory = null;

	// Form
	let categoryForm = {
		name: '',
		description: '',
		tenant: '',
		kitchen_station_code: 'MAIN',
		sort_order: 0,
		is_active: true
	};

	// Load tenants list
	async function loadTenants() {
		if (!browser) return;
		
		try {
			const response = await getTenants({ page_size: 100, is_active: true });
			tenants = response.results || [];
		} catch (error) {
			console.error('Failed to load tenants:', error);
		}
	}

	// Get tenant name by ID
	function getTenantName(tenantId) {
		const tenant = tenants.find(t => t.id === tenantId);
		return tenant ? tenant.name : '-';
	}

	// Load kitchen station types
	async function loadStationTypes() {
		if (!browser) return;
		
		try {
			const response = await getKitchenStationTypes($selectedTenant);
			stationTypes = response.results || response || [];
			// Filter only active types
			stationTypes = stationTypes.filter(t => t.is_active);
			// Sort by sort_order
			stationTypes.sort((a, b) => a.sort_order - b.sort_order);
		} catch (error) {
			console.error('Failed to load station types:', error);
		}
	}

	// Get station type by code
	function getStationType(code) {
		return stationTypes.find(t => t.code === code);
	}

	// Load categories
	async function loadCategories() {
		if (!browser) return;
		
		try {
			loading = true;
			const params = new URLSearchParams({
				page: currentPage,
				page_size: 10,
				ordering: 'sort_order,name'
			});
			
			if (searchQuery) params.append('search', searchQuery);
			if (statusFilter === 'active') params.append('is_active', 'true');
			if (statusFilter === 'inactive') params.append('is_active', 'false');
			if ($selectedTenant) {
				console.log('Loading categories with tenant:', $selectedTenant);
				params.append('tenant', $selectedTenant);
			} else {
				console.log('Loading categories without tenant filter');
			}
			
			console.log('Categories URL:', `/api/admin/categories/?${params}`);
			const response = await authFetch(`/api/admin/categories/?${params}`);
			categories = response.results || [];
			totalCount = response.count || 0;
			totalPages = Math.ceil(totalCount / 10);
		} catch (error) {
			console.error('Failed to load categories:', error);
			Swal.fire('Error', 'Failed to load categories', 'error');
		} finally {
			loading = false;
		}
	}

	// Load stats
	async function loadStats() {
		if (!browser) return;
		
		try {
			const params = new URLSearchParams();
			if ($selectedTenant) {
				console.log('Loading stats with tenant:', $selectedTenant);
				params.append('tenant', $selectedTenant);
			} else {
				console.log('Loading stats without tenant filter');
			}
			const queryString = params.toString();
			console.log('Stats URL:', `/api/admin/categories/stats/${queryString ? '?' + queryString : ''}`);
			const response = await authFetch(`/api/admin/categories/stats/${queryString ? '?' + queryString : ''}`);
			stats = response;
		} catch (error) {
			console.error('Failed to load stats:', error);
		}
	}

	// Open create modal
	function openCreateModal() {
		editingCategory = null;
		categoryForm = {
			name: '',
			description: '',
			tenant: currentUser?.tenant_id || '',
			kitchen_station_code: 'MAIN',
			sort_order: 0,
			is_active: true
		};
		errors = {};
		showModal = true;
	}

	// Open edit modal
	function openEditModal(category) {
		editingCategory = category;
		categoryForm = {
			name: category.name,
			description: category.description || '',
			tenant: category.tenant,
			kitchen_station_code: category.kitchen_station_code || 'MAIN',
			sort_order: category.sort_order,
			is_active: category.is_active
		};
		errors = {};
		showModal = true;
	}

	// Close modal
	function closeModal() {
		showModal = false;
		editingCategory = null;
		errors = {};
	}

	// Validate form
	function validateForm() {
		errors = {};
		
		if (!categoryForm.name.trim()) {
			errors.name = 'Category name is required';
		}
		
		if (!categoryForm.tenant) {
			errors.tenant = 'Tenant is required';
		}
		
		return Object.keys(errors).length === 0;
	}

	// Save category
	async function saveCategory() {
		if (!validateForm()) return;
		
		try {
			loading = true;
			
			if (editingCategory) {
				// Update
				await authFetch(`/api/admin/categories/${editingCategory.id}/`, {
					method: 'PATCH',
					body: JSON.stringify(categoryForm)
				});
				Swal.fire('Success', 'Category updated successfully', 'success');
			} else {
				// Create
				await authFetch('/api/admin/categories/', {
					method: 'POST',
					body: JSON.stringify(categoryForm)
				});
				Swal.fire('Success', 'Category created successfully', 'success');
			}
			
			closeModal();
			await loadCategories();
			await loadStats();
		} catch (error) {
			console.error('Failed to save category:', error);
			Swal.fire('Error', error.message || 'Failed to save category', 'error');
		} finally {
			loading = false;
		}
	}

	// Delete category
	async function deleteCategory(category) {
		const result = await Swal.fire({
			title: 'Delete Category?',
			text: `Are you sure you want to delete "${category.name}"?`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#d33',
			cancelButtonColor: '#3085d6',
			confirmButtonText: 'Yes, delete it!'
		});
		
		if (!result.isConfirmed) return;
		
		try {
			loading = true;
			await authFetch(`/api/admin/categories/${category.id}/`, {
				method: 'DELETE'
			});
			Swal.fire('Deleted!', 'Category has been deleted.', 'success');
			await loadCategories();
			await loadStats();
		} catch (error) {
			console.error('Failed to delete category:', error);
			Swal.fire('Error', error.message || 'Failed to delete category', 'error');
		} finally {
			loading = false;
		}
	}

	// Toggle active status
	async function toggleActive(category) {
		try {
			loading = true;
			await authFetch(`/api/admin/categories/${category.id}/`, {
				method: 'PATCH',
				body: JSON.stringify({ is_active: !category.is_active })
			});
			await loadCategories();
			await loadStats();
		} catch (error) {
			console.error('Failed to toggle status:', error);
			Swal.fire('Error', error.message || 'Failed to update status', 'error');
		} finally {
			loading = false;
		}
	}

	// Pagination handlers
	function goToPage(page) {
		currentPage = page;
		loadCategories();
	}

	function nextPage() {
		if (currentPage < totalPages) {
			currentPage++;
			loadCategories();
		}
	}

	function prevPage() {
		if (currentPage > 1) {
			currentPage--;
			loadCategories();
		}
	}

	// Apply filters
	function applyFilters() {
		currentPage = 1;
		loadCategories();
	}

	onMount(() => {
		currentUser = get(user);
		showTenantField = currentUser?.role === 'super_admin' || currentUser?.role === 'admin';
		
		loadTenants();
		loadStationTypes();
		loadCategories();
		loadStats();
		mounted = true;
	});

	// Reactive: reload when tenant filter changes
	$: if (mounted && $selectedTenant !== undefined) {
		console.log('🔄 Reactive reload triggered. Tenant:', $selectedTenant);
		const tenantId = $selectedTenant;
		currentPage = 1;
		loadCategories();
		loadStats();
	}
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex justify-between items-center">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Category Management</h1>
			<p class="text-gray-500 mt-1">Manage product categories</p>
		</div>
		<button on:click={openCreateModal} class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors">
			+ Add Category
		</button>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
		<div class="bg-white p-6 rounded-lg border border-gray-200">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-500">Total Categories</p>
					<p class="text-2xl font-bold text-gray-900">{stats.total_categories}</p>
				</div>
				<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
					<span class="text-2xl">📁</span>
				</div>
			</div>
		</div>

		<div class="bg-white p-6 rounded-lg border border-gray-200">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-500">Active</p>
					<p class="text-2xl font-bold text-green-600">{stats.active_categories}</p>
				</div>
				<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
					<span class="text-2xl">✅</span>
				</div>
			</div>
		</div>

		<div class="bg-white p-6 rounded-lg border border-gray-200">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-500">Inactive</p>
					<p class="text-2xl font-bold text-red-600">{stats.inactive_categories}</p>
				</div>
				<div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
					<span class="text-2xl">❌</span>
				</div>
			</div>
		</div>

		<div class="bg-white p-6 rounded-lg border border-gray-200">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-gray-500">With Products</p>
					<p class="text-2xl font-bold text-purple-600">{stats.categories_with_products}</p>
				</div>
				<div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
					<span class="text-2xl">🍽️</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Filters -->
	<div class="bg-white p-4 rounded-lg border border-gray-200">
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
				<input
					type="text"
					bind:value={searchQuery}
					on:input={applyFilters}
					placeholder="Search categories..."
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
				<select
					bind:value={statusFilter}
					on:change={applyFilters}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				>
					<option value="">All Status</option>
					<option value="active">Active</option>
					<option value="inactive">Inactive</option>
				</select>
			</div>

			<div class="flex items-end">
				<button
					on:click={applyFilters}
					class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium transition-colors"
				>
					Apply Filters
				</button>
			</div>
		</div>
	</div>

	<!-- Categories Table -->
	<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
		{#if loading && categories.length === 0}
			<div class="text-center py-12">
				<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
				<p class="mt-2 text-gray-500">Loading categories...</p>
			</div>
		{:else if categories.length === 0}
			<div class="text-center py-12">
				<span class="text-6xl">📁</span>
				<p class="mt-4 text-lg font-medium text-gray-900">No categories found</p>
				<p class="text-gray-500">Create your first category to get started</p>
				<button
					on:click={openCreateModal}
					class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
				>
					Add Category
				</button>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead class="bg-gray-50 border-b border-gray-200">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Name
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Kitchen Station
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Tenant
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
						{#each categories as category}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4">
									<div class="flex items-center">
										<div>
											<div class="text-sm font-medium text-gray-900">{category.name}</div>
											{#if category.description}
												<div class="text-sm text-gray-500">{category.description}</div>
											{/if}
										</div>
									</div>
								</td>
								<td class="px-6 py-4">								<div class="flex items-center gap-2">
									{#if getStationType(category.kitchen_station_code)}
										<span class="text-lg">{getStationType(category.kitchen_station_code).icon}</span>
									{/if}
									<span 
										class="px-2 py-1 text-xs font-semibold rounded"
										style="background-color: {getStationType(category.kitchen_station_code)?.color}20; color: {getStationType(category.kitchen_station_code)?.color || '#666'};"
									>
										{category.kitchen_station_code || 'MAIN'}
									</span>
								</div>
							</td>
							<td class="px-6 py-4">									<div class="text-sm text-gray-900">{category.tenant_name || '-'}</div>
								</td>
								<td class="px-6 py-4">
									<div class="text-sm text-gray-900">{category.sort_order}</div>
								</td>
								<td class="px-6 py-4">
									<button
										on:click={() => toggleActive(category)}
										class="inline-flex px-3 py-1 text-xs font-semibold rounded-full {category.is_active
											? 'bg-green-100 text-green-800'
											: 'bg-red-100 text-red-800'}"
									>
										{category.is_active ? 'Active' : 'Inactive'}
									</button>
								</td>
								<td class="px-6 py-4 text-sm">
									<div class="flex items-center gap-2">
										<button
											on:click={() => openEditModal(category)}
											class="text-blue-600 hover:text-blue-800"
											title="Edit"
										>
											✏️
										</button>
										<button
											on:click={() => toggleActive(category)}
											class="text-yellow-600 hover:text-yellow-800"
											title={category.is_active ? 'Deactivate' : 'Activate'}
										>
											{category.is_active ? '🔓' : '🔒'}
										</button>
										<button
											on:click={() => deleteCategory(category)}
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
							on:click={prevPage}
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
							on:click={nextPage}
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
{#if showModal}
	<div class="fixed inset-0 z-50 overflow-y-auto">
		<div class="flex items-center justify-center min-h-screen px-4">
			<div class="fixed inset-0 bg-black opacity-50" on:click={closeModal}></div>
			
			<div class="relative bg-white rounded-lg w-full max-w-2xl p-6">
				<div class="flex justify-between items-center mb-6">
					<h2 class="text-xl font-bold text-gray-900">
						{editingCategory ? 'Edit Category' : 'Add New Category'}
					</h2>
					<button on:click={closeModal} class="text-gray-400 hover:text-gray-600">
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>

				<form on:submit|preventDefault={saveCategory} class="space-y-4">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="md:col-span-2">
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Name <span class="text-red-500">*</span>
							</label>
							<input
								type="text"
								bind:value={categoryForm.name}
								class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent {errors.name ? 'border-red-500' : 'border-gray-300'}"
								placeholder="Category name"
							/>
							{#if errors.name}
								<p class="mt-1 text-sm text-red-500">{errors.name}</p>
							{/if}
						</div>

						<div class="md:col-span-2">
							<label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
							<textarea
								bind:value={categoryForm.description}
								rows="3"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="Category description"
							></textarea>
						</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Kitchen Station <span class="text-red-500">*</span>
						</label>
						<select
							bind:value={categoryForm.kitchen_station_code}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						>
							{#each stationTypes as type}
								<option value={type.code}>
									{type.icon} {type.name} ({type.code})
								</option>
							{/each}
						</select>
						<p class="text-xs text-gray-500 mt-1">
							Products in this category will route to this station type
						</p>
					</div>

					{#if showTenantField}
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Tenant <span class="text-red-500">*</span>
						</label>
						<select
							bind:value={categoryForm.tenant}
							class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent {errors.tenant ? 'border-red-500' : 'border-gray-300'}"
						>
							<option value="">Select Tenant</option>
							{#each tenants as tenant}
								<option value={tenant.id}>{tenant.name}</option>
							{/each}
						</select>
						{#if errors.tenant}
							<p class="mt-1 text-sm text-red-500">{errors.tenant}</p>
						{/if}
					</div>
					{/if}

					<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">Sort Order</label>
							<input
								type="number"
								bind:value={categoryForm.sort_order}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="0"
							/>
						</div>

						<div class="md:col-span-2">
							<label class="flex items-center space-x-2">
								<input
									type="checkbox"
									bind:checked={categoryForm.is_active}
									class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
								/>
								<span class="text-sm font-medium text-gray-700">Active</span>
							</label>
						</div>
					</div>

					<div class="flex justify-end space-x-3 pt-4">
						<button
							type="button"
							on:click={closeModal}
							class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium transition-colors"
						>
							Cancel
						</button>
						<button
							type="submit"
							disabled={loading}
							class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:opacity-50"
						>
							{loading ? 'Saving...' : 'Save Category'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}
