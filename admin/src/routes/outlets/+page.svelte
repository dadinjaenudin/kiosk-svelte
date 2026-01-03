<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import Swal from 'sweetalert2';
	import {
		getOutlets,
		getOutletStats,
		createOutlet,
		updateOutlet,
		deleteOutlet,
		formatOperatingHours
	} from '$lib/api/settings';
	import { getTenants } from '$lib/api/tenants';
	import { selectedTenant } from '$lib/stores/auth';

	// State
	let outlets = [];
	let tenants = [];
	let stats = { total: 0, active: 0, inactive: 0, by_city: {}, by_province: {} };
	let loading = false;
	let mounted = false;

	// Filters
	let searchQuery = '';
	let statusFilter = '';
	let cityFilter = '';

	// Pagination
	let currentPage = 1;
	let totalPages = 1;
	let totalCount = 0;

	// Modals
	let showModal = false;
	let editingOutlet = null;

	// Form
	let outletForm = {
		name: '',
		slug: '',
		tenant: '',
		address: '',
		city: '',
		province: '',
		postal_code: '',
		phone: '',
		email: '',
		opening_time: '09:00',
		closing_time: '22:00',
		websocket_url: 'ws://localhost:3001',
		is_active: true
	};

	let errors = {};

	// Get available cities from stats
	$: availableCities = Object.keys(stats.by_city || {});

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

	// Load outlets
	async function loadOutlets() {
		if (!browser) return;
		
		try {
			loading = true;
			const params = {
				page: currentPage,
				search: searchQuery || undefined,
				is_active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined,
				city: cityFilter && cityFilter !== 'all' ? cityFilter : undefined,
				tenant: $selectedTenant || undefined
			};
			
			const response = await getOutlets(params);
			outlets = response.results || [];
			totalCount = response.count || 0;
			totalPages = Math.ceil(totalCount / 10);
		} catch (error) {
			console.error('Failed to load outlets:', error);
			Swal.fire('Error', 'Failed to load outlets', 'error');
		} finally {
			loading = false;
		}
	}

	// Load stats
	async function loadStats() {
		if (!browser) return;
		
		try {
			stats = await getOutletStats();
		} catch (error) {
			console.error('Failed to load stats:', error);
		}
	}

	// Open create modal
	function openCreateModal() {
		editingOutlet = null;
		outletForm = {
			name: '',
			slug: '',
			tenant: '',
			address: '',
			city: '',
			province: '',
			postal_code: '',
			phone: '',
			email: '',
			opening_time: '09:00',
			closing_time: '22:00',
			websocket_url: 'ws://localhost:3001',
			is_active: true
		};
		errors = {};
		showModal = true;
	}

	// Open edit modal
	function openEditModal(outlet) {
		editingOutlet = outlet;
		outletForm = {
			name: outlet.name || '',
			slug: outlet.slug || '',
			tenant: outlet.tenant || '',
			address: outlet.address || '',
			city: outlet.city || '',
			province: outlet.province || '',
			postal_code: outlet.postal_code || '',
			phone: outlet.phone || '',
			email: outlet.email || '',
			opening_time: outlet.opening_time || '09:00',
			closing_time: outlet.closing_time || '22:00',
			websocket_url: outlet.websocket_url || 'ws://localhost:3001',
			is_active: outlet.is_active !== undefined ? outlet.is_active : true
		};
		errors = {};
		showModal = true;
	}

	// Submit form
	async function handleSubmit() {
		try {
			errors = {};
			
			if (!outletForm.name || outletForm.name.trim() === '') {
				errors.name = 'Outlet name is required';
			}
			if (!outletForm.tenant) {
				errors.tenant = 'Tenant is required';
			}
			if (!outletForm.city || outletForm.city.trim() === '') {
				errors.city = 'City is required';
			}
			if (!outletForm.phone || outletForm.phone.trim() === '') {
				errors.phone = 'Phone is required';
			}
			if (Object.keys(errors).length > 0) return;

			const sanitizedData = {
				...outletForm,
				slug: outletForm.slug?.trim() || '',
				address: outletForm.address?.trim() || '',
				postal_code: outletForm.postal_code?.trim() || '',
				phone: outletForm.phone?.trim() || '',
				email: outletForm.email?.trim() || ''
			};

			if (editingOutlet) {
				await updateOutlet(editingOutlet.id, sanitizedData);
				Swal.fire('Success', 'Outlet updated successfully', 'success');
			} else {
				await createOutlet(sanitizedData);
				Swal.fire('Success', 'Outlet created successfully', 'success');
			}

			showModal = false;
			await loadOutlets();
			await loadStats();
		} catch (error) {
			console.error('Failed to save outlet:', error);
			Swal.fire('Error', 'Failed to save outlet: ' + (error.message || 'Unknown error'), 'error');
		}
	}

	// Delete outlet
	async function handleDelete(outlet) {
		const result = await Swal.fire({
			title: 'Delete Outlet?',
			text: `Are you sure you want to delete "${outlet.name}"? This action cannot be undone.`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#d33',
			cancelButtonColor: '#3085d6',
			confirmButtonText: 'Yes, delete it!'
		});

		if (result.isConfirmed) {
			try {
				await deleteOutlet(outlet.id);
				Swal.fire('Deleted!', 'Outlet has been deleted.', 'success');
				await loadOutlets();
				await loadStats();
			} catch (error) {
				console.error('Failed to delete outlet:', error);
				Swal.fire('Error', 'Failed to delete outlet', 'error');
			}
		}
	}

	// Search
	function handleSearch() {
		currentPage = 1;
		loadOutlets();
	}

	// Filter
	function handleFilterChange() {
		currentPage = 1;
		loadOutlets();
	}

	// Pagination
	function goToPage(page) {
		if (page < 1 || page > totalPages) return;
		currentPage = page;
		loadOutlets();
	}

	// Init
	onMount(() => {
		loadTenants();
		loadOutlets();
		loadStats();
		mounted = true;
	});

	// Reactive: reload when tenant filter changes
	$: if (mounted) {
		// This will trigger whenever $selectedTenant changes
		const tenantId = $selectedTenant;
		currentPage = 1;
		loadOutlets();
	}
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Outlet Management</h1>
			<p class="text-sm text-gray-600 mt-1">Manage all outlets in the system</p>
		</div>
	</div>

	<!-- Statistics -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-6">
		<div class="card">
			<div class="card-body">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Total Outlets</p>
						<p class="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
					</div>
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
						<span class="text-2xl">📍</span>
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

		<div class="card">
			<div class="card-body">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Cities</p>
						<p class="text-2xl font-bold text-purple-600 mt-1">{Object.keys(stats.by_city || {}).length}</p>
					</div>
					<div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
						<span class="text-2xl">🏙️</span>
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
						placeholder="Search outlets..."
						class="form-input"
					/>
				</div>
				<div class="flex gap-2">
					<select
						bind:value={statusFilter}
						on:change={handleFilterChange}
						class="form-select"
					>
						<option value="">All Status</option>
						<option value="active">Active</option>
						<option value="inactive">Inactive</option>
					</select>
					<select
						bind:value={cityFilter}
						on:change={handleFilterChange}
						class="form-select"
					>
						<option value="all">All Cities</option>
						{#each availableCities as city}
							<option value={city}>{city}</option>
						{/each}
					</select>
					<button on:click={openCreateModal} class="btn btn-primary whitespace-nowrap">
						<span class="mr-2">➕</span>
						Add Outlet
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Outlets Table -->
	<div class="card">
		<div class="card-body p-0">
			{#if loading}
				<div class="text-center py-12">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
					<p class="mt-2 text-sm text-gray-600">Loading outlets...</p>
				</div>
			{:else if outlets.length === 0}
				<div class="text-center py-12">
					<span class="text-4xl mb-4 block">📍</span>
					<p class="text-gray-500">No outlets found</p>
					<button on:click={openCreateModal} class="btn btn-primary btn-sm mt-4">
						Add Your First Outlet
					</button>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Outlet
								</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Tenant
								</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Location
								</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Contact
								</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Operating Hours
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
							{#each outlets as outlet (outlet.id)}
								<tr class="hover:bg-gray-50 transition-colors">
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="flex items-center">
											<div class="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
												<span class="text-lg">📍</span>
											</div>
											<div class="ml-3">
												<p class="text-sm font-medium text-gray-900">{outlet.name}</p>
												<p class="text-xs text-gray-500">ID: {outlet.id}</p>
											</div>
										</div>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<p class="text-sm text-gray-900">{getTenantName(outlet.tenant)}</p>
									</td>
									<td class="px-6 py-4">
										<p class="text-sm text-gray-900 font-medium">{outlet.city}, {outlet.province}</p>
										<p class="text-xs text-gray-500 mt-1 max-w-xs truncate">{outlet.address}</p>
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										{#if outlet.phone}
											<p class="text-sm text-gray-900">{outlet.phone}</p>
										{/if}
										{#if outlet.email}
											<p class="text-xs text-gray-500 mt-1">{outlet.email}</p>
										{/if}
										{#if !outlet.phone && !outlet.email}
											<p class="text-sm text-gray-400">-</p>
										{/if}
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<p class="text-sm text-gray-900">{formatOperatingHours(outlet.opening_time, outlet.closing_time)}</p>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-center">
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {outlet.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
											{outlet.is_active ? 'Active' : 'Inactive'}
										</span>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-right">
										<div class="flex items-center justify-end space-x-1">
											<button
												on:click={() => openEditModal(outlet)}
												class="p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
												title="Edit"
											>
												<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
												</svg>
											</button>
											<button
												on:click={() => handleDelete(outlet)}
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

<!-- Outlet Modal -->
{#if showModal}
	<div class="modal">
		<div class="modal-content max-w-3xl">
			<div class="modal-header">
				<h3 class="modal-title">
					{editingOutlet ? 'Edit Outlet' : 'Create New Outlet'}
				</h3>
				<button on:click={() => showModal = false} class="modal-close">✕</button>
			</div>

			<div class="modal-body">
				<div class="space-y-6">
					<!-- Basic Info -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="md:col-span-2">
							<label for="outlet-tenant" class="form-label required">Tenant</label>
							<select
								id="outlet-tenant"
								bind:value={outletForm.tenant}
								class="form-select {errors.tenant ? 'border-red-500' : ''}"
							>
								<option value="">Select tenant</option>
								{#each tenants as tenant}
									<option value={tenant.id}>{tenant.name}</option>
								{/each}
							</select>
							{#if errors.tenant}
								<p class="form-error">{errors.tenant}</p>
							{/if}
						</div>

						<div class="md:col-span-2">
							<label for="outlet-name" class="form-label required">Outlet Name</label>
							<input
								id="outlet-name"
								type="text"
								bind:value={outletForm.name}
								class="form-input {errors.name ? 'border-red-500' : ''}"
								placeholder="Enter outlet name"
							/>
							{#if errors.name}
								<p class="form-error">{errors.name}</p>
							{/if}
						</div>

						<div class="md:col-span-2">
							<label for="outlet-slug" class="form-label">Slug</label>
							<input
								id="outlet-slug"
								type="text"
								bind:value={outletForm.slug}
								class="form-input"
								placeholder="outlet-slug"
							/>
						</div>
					</div>

					<!-- Address -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="md:col-span-2">
							<label for="outlet-address" class="form-label">Address</label>
							<textarea
								id="outlet-address"
								bind:value={outletForm.address}
								rows="2"
								class="form-input"
								placeholder="Street address"
							></textarea>
						</div>

						<div>
							<label for="outlet-city" class="form-label required">City</label>
							<input
								id="outlet-city"
								type="text"
								bind:value={outletForm.city}
								class="form-input {errors.city ? 'border-red-500' : ''}"
								placeholder="City"
							/>
							{#if errors.city}
								<p class="form-error">{errors.city}</p>
							{/if}
						</div>

						<div>
							<label for="outlet-province" class="form-label">Province</label>
							<input
								id="outlet-province"
								type="text"
								bind:value={outletForm.province}
								class="form-input"
								placeholder="Province"
							/>
						</div>

						<div>
							<label for="outlet-postal" class="form-label">Postal Code</label>
							<input
								id="outlet-postal"
								type="text"
								bind:value={outletForm.postal_code}
								class="form-input"
								placeholder="12345"
							/>
						</div>
					</div>

					<!-- Contact -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="outlet-phone" class="form-label required">Phone</label>
							<input
								id="outlet-phone"
								type="text"
								bind:value={outletForm.phone}
								class="form-input {errors.phone ? 'border-red-500' : ''}"
								placeholder="+62812345678"
								required
							/>
							{#if errors.phone}
								<p class="form-error">{errors.phone}</p>
							{/if}
						</div>

						<div>
							<label for="outlet-email" class="form-label">Email</label>
							<input
								id="outlet-email"
								type="email"
								bind:value={outletForm.email}
								class="form-input"
								placeholder="outlet@example.com"
							/>
						</div>
					</div>

					<!-- Operating Hours -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="outlet-opening" class="form-label">Opening Time</label>
							<input
								id="outlet-opening"
								type="time"
								bind:value={outletForm.opening_time}
								class="form-input"
							/>
						</div>

						<div>
							<label for="outlet-closing" class="form-label">Closing Time</label>
							<input
								id="outlet-closing"
								type="time"
								bind:value={outletForm.closing_time}
								class="form-input"
							/>
						</div>
					</div>

					<!-- WebSocket Configuration -->
					<div>
						<label for="outlet-websocket" class="form-label">
							WebSocket URL
							<span class="text-xs text-gray-500 ml-2">(Kitchen Sync Server)</span>
						</label>
						<input
							id="outlet-websocket"
							type="text"
							bind:value={outletForm.websocket_url}
							class="form-input"
							placeholder="ws://192.168.1.10:3001"
						/>
						<p class="text-xs text-gray-500 mt-1">
							Example: ws://192.168.1.10:3001 (use local network IP for multi-outlet)
						</p>
					</div>

					<!-- Status -->
					<div class="flex items-center">
						<input
							id="outlet-active"
							type="checkbox"
							bind:checked={outletForm.is_active}
							class="form-checkbox"
						/>
						<label for="outlet-active" class="ml-2 text-sm text-gray-700">
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
					{editingOutlet ? 'Update Outlet' : 'Create Outlet'}
				</button>
			</div>
		</div>
	</div>
{/if}
