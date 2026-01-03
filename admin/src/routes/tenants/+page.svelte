<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import Swal from 'sweetalert2';
	import {
		getTenants,
		getTenantStats,
		createTenant,
		updateTenant,
		deleteTenant
	} from '$lib/api/tenants';

	// State
	let tenants = [];
	let stats = { total: 0, active: 0, inactive: 0 };
	let loading = false;

	// Filters
	let searchQuery = '';
	let isActiveFilter = '';

	// Pagination
	let currentPage = 1;
	let totalPages = 1;
	let totalCount = 0;

	// Modals
	let showModal = false;
	let editingTenant = null;

	// Form
	let tenantForm = {
		name: '',
		slug: '',
		description: '',
		phone: '',
		email: '',
		website: '',
		is_active: true
	};

	let errors = {};

	// Auto-generate slug from name
	function slugify(text) {
		return text
			.toString()
			.toLowerCase()
			.trim()
			.replace(/\s+/g, '-')        // Replace spaces with -
			.replace(/[^\w\-]+/g, '')    // Remove non-word chars except -
			.replace(/\-\-+/g, '-')      // Replace multiple - with single -
			.replace(/^-+/, '')          // Trim - from start
			.replace(/-+$/, '');         // Trim - from end
	}

	// Watch name changes to auto-update slug (only when creating)
	$: if (!editingTenant && tenantForm.name) {
		tenantForm.slug = slugify(tenantForm.name);
	}

	// Load tenants
	async function loadTenants() {
		if (!browser) return;
		
		try {
			loading = true;
			const params = {
				page: currentPage,
				search: searchQuery || undefined,
				is_active: isActiveFilter || undefined
			};
			
			const response = await getTenants(params);
			tenants = response.results || [];
			totalCount = response.count || 0;
			totalPages = Math.ceil(totalCount / 10);
		} catch (error) {
			console.error('Failed to load tenants:', error);
			Swal.fire('Error', 'Failed to load tenants', 'error');
		} finally {
			loading = false;
		}
	}

	// Load stats
	async function loadStats() {
		if (!browser) return;
		
		try {
			stats = await getTenantStats();
		} catch (error) {
			console.error('Failed to load stats:', error);
		}
	}

	// Open create modal
	function openCreateModal() {
		editingTenant = null;
		tenantForm = {
			name: '',
			slug: '',
			description: '',
			phone: '',
			email: '',
			website: '',
			is_active: true
		};
		errors = {};
		showModal = true;
	}

	// Open edit modal
	function openEditModal(tenant) {
		editingTenant = tenant;
		tenantForm = { ...tenant };
		errors = {};
		showModal = true;
	}

	// Submit form
	async function handleSubmit() {
		try {
			errors = {};
			
			if (!tenantForm.name || tenantForm.name.trim() === '') {
				errors.name = 'Tenant name is required';
			}
			if (Object.keys(errors).length > 0) return;

			const sanitizedData = {
				...tenantForm,
				slug: tenantForm.slug?.trim() || '',
				description: tenantForm.description?.trim() || '',
				phone: tenantForm.phone?.trim() || '',
				email: tenantForm.email?.trim() || '',
				website: tenantForm.website?.trim() || ''
			};

			if (editingTenant) {
				await updateTenant(editingTenant.id, sanitizedData);
				Swal.fire('Success', 'Tenant updated successfully', 'success');
			} else {
				await createTenant(sanitizedData);
				Swal.fire('Success', 'Tenant created successfully', 'success');
			}

			showModal = false;
			await loadTenants();
			await loadStats();
		} catch (error) {
			console.error('Failed to save tenant:', error);
			Swal.fire('Error', 'Failed to save tenant', 'error');
		}
	}

	// Delete tenant
	async function handleDelete(tenant) {
		const result = await Swal.fire({
			title: 'Delete Tenant?',
			text: `Are you sure you want to delete "${tenant.name}"? This action cannot be undone.`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#d33',
			cancelButtonColor: '#3085d6',
			confirmButtonText: 'Yes, delete it!'
		});

		if (result.isConfirmed) {
			try {
				await deleteTenant(tenant.id);
				Swal.fire('Deleted!', 'Tenant has been deleted.', 'success');
				await loadTenants();
				await loadStats();
			} catch (error) {
				console.error('Failed to delete tenant:', error);
				Swal.fire('Error', 'Failed to delete tenant', 'error');
			}
		}
	}

	// Search
	function handleSearch() {
		currentPage = 1;
		loadTenants();
	}

	// Filter
	function handleFilter() {
		currentPage = 1;
		loadTenants();
	}

	// Pagination
	function goToPage(page) {
		if (page < 1 || page > totalPages) return;
		currentPage = page;
		loadTenants();
	}

	// Init
	onMount(() => {
		loadTenants();
		loadStats();
	});
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Tenant Management</h1>
			<p class="text-sm text-gray-600 mt-1">Manage all tenants in the system</p>
		</div>
	</div>

	<!-- Statistics -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
		<div class="card">
			<div class="card-body">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Total Tenants</p>
						<p class="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
					</div>
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
						<span class="text-2xl">🏢</span>
					</div>
				</div>
			</div>
		</div>

		<div class="card">
			<div class="card-body">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Active</p>
						<p class="text-2xl font-bold text-green-600 mt-1">{stats.active}</p>
					</div>
					<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
						<span class="text-2xl">✅</span>
					</div>
				</div>
			</div>
		</div>

		<div class="card">
			<div class="card-body">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Inactive</p>
						<p class="text-2xl font-bold text-red-600 mt-1">{stats.inactive}</p>
					</div>
					<div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
						<span class="text-2xl">❌</span>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Search and Actions -->
	<div class="card">
		<div class="card-body">
			<div class="flex flex-col lg:flex-row gap-4">
				<div class="flex-1">
					<input
						type="text"
						bind:value={searchQuery}
						on:keyup={(e) => e.key === 'Enter' && handleSearch()}
						placeholder="Search tenants..."
						class="form-input"
					/>
				</div>
				<div class="flex gap-2">
					<select
						bind:value={isActiveFilter}
						on:change={handleFilter}
						class="form-select"
					>
						<option value="">All Status</option>
						<option value="true">Active</option>
						<option value="false">Inactive</option>
					</select>
					<button on:click={openCreateModal} class="btn btn-primary whitespace-nowrap">
						<span class="mr-2">➕</span>
						Add Tenant
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Tenants Table -->
	<div class="card">
		<div class="card-body p-0">
			{#if loading}
				<div class="text-center py-12">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
					<p class="mt-2 text-sm text-gray-600">Loading tenants...</p>
				</div>
			{:else if tenants.length === 0}
				<div class="text-center py-12">
					<span class="text-4xl mb-4 block">🏢</span>
					<p class="text-gray-500">No tenants found</p>
					<button on:click={openCreateModal} class="btn btn-primary btn-sm mt-4">
						Add Your First Tenant
					</button>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Tenant
								</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Contact
								</th>
								<th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
									Status
								</th>
								<th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
									Actions
								</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-gray-200">
							{#each tenants as tenant (tenant.id)}
								<tr class="hover:bg-gray-50 transition-colors">
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="flex items-center">
											<div class="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
												<span class="text-lg">🏢</span>
											</div>
											<div class="ml-3">
												<p class="text-sm font-medium text-gray-900">{tenant.name}</p>
												<p class="text-xs text-gray-500">{tenant.slug || '-'}</p>
											</div>
										</div>
									</td>
									<td class="px-6 py-4">
										{#if tenant.phone}
											<p class="text-sm text-gray-900">{tenant.phone}</p>
										{/if}
										{#if tenant.email}
											<p class="text-xs text-gray-500 truncate max-w-[200px]">{tenant.email}</p>
										{/if}
										{#if !tenant.phone && !tenant.email}
											<p class="text-sm text-gray-400">-</p>
										{/if}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-center">
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {tenant.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
											{tenant.is_active ? 'Active' : 'Inactive'}
										</span>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-right">
										<div class="flex items-center justify-end space-x-1">
											<button
												on:click={() => openEditModal(tenant)}
												class="p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
												title="Edit"
											>
												<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
												</svg>
											</button>
											<button
												on:click={() => handleDelete(tenant)}
												class="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
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
</div>

<!-- Tenant Modal -->
{#if showModal}
	<div class="modal">
		<div class="modal-content max-w-3xl">
			<div class="modal-header">
				<h3 class="modal-title">
					{editingTenant ? 'Edit Tenant' : 'Create New Tenant'}
				</h3>
				<button on:click={() => showModal = false} class="modal-close">✕</button>
			</div>

			<div class="modal-body">
				<div class="space-y-6">
					<!-- Basic Info -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="md:col-span-2">
							<label for="tenant-name" class="form-label required">Tenant Name</label>
							<input
								id="tenant-name"
								type="text"
								bind:value={tenantForm.name}
								class="form-input {errors.name ? 'border-red-500' : ''}"
								placeholder="Enter tenant name"
							/>
							{#if errors.name}
								<p class="form-error">{errors.name}</p>
							{/if}
						</div>

						<div class="md:col-span-2">
							<label for="tenant-slug" class="form-label">
								Slug {#if !editingTenant}<span class="text-xs text-gray-500">(auto-generated)</span>{/if}
							</label>
							<input
								id="tenant-slug"
								type="text"
								bind:value={tenantForm.slug}
								class="form-input"
								placeholder="tenant-slug"
								readonly={!editingTenant}
							/>
							{#if errors.slug}
								<p class="form-error">{errors.slug}</p>
							{/if}
						</div>

						<div>
							<label for="tenant-phone" class="form-label">Phone</label>
							<input
								id="tenant-phone"
								type="text"
								bind:value={tenantForm.phone}
								class="form-input"
								placeholder="+62812345678"
							/>
						</div>

						<div>
							<label for="tenant-email" class="form-label">Email</label>
							<input
								id="tenant-email"
								type="email"
								bind:value={tenantForm.email}
								class="form-input"
								placeholder="tenant@example.com"
							/>
						</div>

						<div class="md:col-span-2">
							<label for="tenant-website" class="form-label">Website</label>
							<input
								id="tenant-website"
								type="text"
								bind:value={tenantForm.website}
								class="form-input"
								placeholder="https://example.com"
							/>
						</div>

						<div class="md:col-span-2">
							<label for="tenant-description" class="form-label">Description</label>
							<textarea
								id="tenant-description"
								bind:value={tenantForm.description}
								rows="3"
								class="form-input"
								placeholder="Tenant description"
							></textarea>
						</div>
					</div>

					<!-- Status -->
					<div class="flex items-center">
						<input
							id="tenant-active"
							type="checkbox"
							bind:checked={tenantForm.is_active}
							class="form-checkbox"
						/>
						<label for="tenant-active" class="ml-2 text-sm text-gray-700">
							Active
						</label>
					</div>
				</div>
			</div>

			<div class="modal-footer">
				<button on:click={() => showModal = false} class="btn btn-secondary">
					Cancel
				</button>
				<button on:click={handleSubmit} class="btn btn-primary">
					{editingTenant ? 'Update Tenant' : 'Create Tenant'}
				</button>
			</div>
		</div>
	</div>
{/if}
