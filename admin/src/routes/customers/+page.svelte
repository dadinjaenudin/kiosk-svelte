<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import {
		getCustomers,
		getCustomerStats,
		getCustomer,
		createCustomer,
		updateCustomer,
		deleteCustomer,
		bulkUpdateCustomers,
		addCustomerPoints,
		redeemCustomerPoints,
		getTopCustomers,
		getMembershipTierOptions,
		getGenderOptions,
		formatMembershipTier,
		formatGender,
		formatPhone,
		formatCurrency,
		formatDate,
		formatDateTime,
		getStatusBadge,
		isValidEmail,
		isValidPhone
	} from '$lib/api/customers';

	// Toast notification state
	let showToast = false;
	let toastMessage = '';
	let toastType = 'success'; // 'success' | 'error' | 'info'

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

	// Customers State
	let customers = [];
	let stats = {
		total: 0,
		active: 0,
		inactive: 0,
		by_tier: {},
		by_gender: {},
		new_this_month: 0,
		total_points: 0,
		avg_points: 0
	};
	let customersLoading = false;
	let selectedCustomers = [];
	let allCustomersSelected = false;

	// Filters
	let searchQuery = '';
	let tierFilter = 'all';
	let statusFilter = 'all';
	let genderFilter = 'all';

	// Pagination
	let currentPage = 1;
	let pageSize = 10;
	let totalCustomers = 0;

	// Modals
	let showCustomerModal = false;
	let showDeleteModal = false;
	let showPointsModal = false;
	let editingCustomer = null;
	let deletingCustomer = null;
	let pointsCustomer = null;
	let pointsAction = 'add'; // 'add' or 'redeem'

	// Customer Form
	let customerForm = {
		name: '',
		email: '',
		phone: '',
		gender: '',
		date_of_birth: '',
		address: '',
		city: '',
		postal_code: '',
		membership_tier: 'regular',
		points: 0,
		notes: '',
		is_subscribed: true,
		is_active: true
	};

	// Points Form
	let pointsForm = {
		points: 0,
		reason: ''
	};

	// Form errors
	let errors = {};

	// Load customers
	async function loadCustomers() {
		if (!browser) return;

		try {
			customersLoading = true;

			const filters = {
				search: searchQuery || undefined,
				membership_tier: tierFilter !== 'all' ? tierFilter : undefined,
				is_active: statusFilter !== 'all' ? statusFilter === 'active' : undefined,
				gender: genderFilter !== 'all' ? genderFilter : undefined,
				page: currentPage,
				page_size: pageSize
			};

			const response = await getCustomers(filters);

			if (response.results) {
				customers = response.results;
				totalCustomers = response.count;
			} else {
				customers = response;
				totalCustomers = response.length;
			}

			selectedCustomers = [];
			allCustomersSelected = false;
		} catch (error) {
			console.error('Failed to load customers:', error);
			showAlert('Failed to load customers', 'error');
		} finally {
			customersLoading = false;
		}
	}

	// Load customer stats
	async function loadCustomerStats() {
		if (!browser) return;

		try {
			stats = await getCustomerStats();
		} catch (error) {
			console.error('Failed to load customer stats:', error);
		}
	}

	// Open customer modal for create
	function openCreateCustomerModal() {
		editingCustomer = null;
		customerForm = {
			name: '',
			email: '',
			phone: '',
			gender: '',
			date_of_birth: '',
			address: '',
			city: '',
			postal_code: '',
			membership_tier: 'regular',
			points: 0,
			notes: '',
			is_subscribed: true,
			is_active: true
		};
		errors = {};
		showCustomerModal = true;
	}

	// Open customer modal for edit
	function openEditCustomerModal(customer) {
		editingCustomer = customer;
		customerForm = {
			name: customer.name || '',
			email: customer.email || '',
			phone: customer.phone || '',
			gender: customer.gender || '',
			date_of_birth: customer.date_of_birth || '',
			address: customer.address || '',
			city: customer.city || '',
			postal_code: customer.postal_code || '',
			membership_tier: customer.membership_tier || 'regular',
			points: customer.points || 0,
			notes: customer.notes || '',
			is_subscribed: customer.is_subscribed !== undefined ? customer.is_subscribed : true,
			is_active: customer.is_active !== undefined ? customer.is_active : true
		};
		errors = {};
		showCustomerModal = true;
	}

	// Save customer
	async function handleCustomerSubmit() {
		try {
			// Validate
			errors = {};

			if (!customerForm.name || customerForm.name.trim() === '') {
				errors.name = 'Customer name is required';
			}

			if (!customerForm.phone || customerForm.phone.trim() === '') {
				errors.phone = 'Phone number is required';
			} else if (!isValidPhone(customerForm.phone)) {
				errors.phone = 'Invalid phone number format';
			}

			if (customerForm.email && !isValidEmail(customerForm.email)) {
				errors.email = 'Invalid email format';
			}

			if (!customerForm.gender || customerForm.gender === '') {
				errors.gender = 'Gender is required';
			}

			if (Object.keys(errors).length > 0) {
				return;
			}

			// Sanitize data - convert empty strings to null for optional fields
			const sanitizedData = {
				...customerForm,
				email: customerForm.email?.trim() || '',
				gender: customerForm.gender || '',  // CharField, use empty string not null
				date_of_birth: customerForm.date_of_birth || null,
				address: customerForm.address?.trim() || '',
				city: customerForm.city?.trim() || '',
				postal_code: customerForm.postal_code?.trim() || '',
				notes: customerForm.notes?.trim() || ''
			};

			if (editingCustomer) {
				await updateCustomer(editingCustomer.id, sanitizedData);
			} else {
				await createCustomer(sanitizedData);
			}

			showCustomerModal = false;
			await loadCustomers();
			await loadCustomerStats();
			showAlert(editingCustomer ? 'Customer updated successfully' : 'Customer created successfully', 'success');
		} catch (error) {
			console.error('Failed to save customer:', error);
			showAlert('Failed to save customer: ' + (error.message || 'Unknown error'), 'error');
		}
	}

	// Delete customer
	async function handleDeleteCustomer() {
		try {
			await deleteCustomer(deletingCustomer.id);
			showDeleteModal = false;
			deletingCustomer = null;
			await loadCustomers();
			await loadCustomerStats();
			showAlert('Customer deleted successfully');
		} catch (error) {
			console.error('Failed to delete customer:', error);
			showAlert('Failed to delete customer', 'error');
		}
	}

	// Open points modal
	function openPointsModal(customer, action) {
		pointsCustomer = customer;
		pointsAction = action;
		pointsForm = {
			points: 0,
			reason: ''
		};
		errors = {};
		showPointsModal = true;
	}

	// Handle points action
	async function handlePointsAction() {
		try {
			errors = {};

			if (!pointsForm.points || pointsForm.points <= 0) {
				errors.points = 'Points must be greater than 0';
				return;
			}

			if (pointsAction === 'add') {
				await addCustomerPoints(pointsCustomer.id, pointsForm.points, pointsForm.reason);
				showAlert('Points added successfully');
			} else {
				await redeemCustomerPoints(pointsCustomer.id, pointsForm.points, pointsForm.reason);
				showAlert('Points redeemed successfully');
			}

			showPointsModal = false;
			await loadCustomers();
			await loadCustomerStats();
		} catch (error) {
			console.error('Failed to process points:', error);
			showAlert(error.message || 'Failed to process points', 'error');
		}
	}

	// Toggle customer selection
	function toggleCustomerSelection(customerId) {
		if (selectedCustomers.includes(customerId)) {
			selectedCustomers = selectedCustomers.filter((id) => id !== customerId);
		} else {
			selectedCustomers = [...selectedCustomers, customerId];
		}
	}

	// Toggle all customers selection
	function toggleAllCustomers() {
		if (allCustomersSelected) {
			selectedCustomers = [];
			allCustomersSelected = false;
		} else {
			selectedCustomers = customers.map((c) => c.id);
			allCustomersSelected = true;
		}
	}

	// Bulk activate
	async function bulkActivate() {
		if (selectedCustomers.length === 0) {
			showAlert('Please select customers to activate');
			return;
		}

		try {
			await bulkUpdateCustomers(selectedCustomers, { is_active: true });
			await loadCustomers();
			await loadCustomerStats();
			selectedCustomers = [];
			allCustomersSelected = false;
			showAlert('Customers activated successfully');
		} catch (error) {
			console.error('Failed to activate customers:', error);
			showAlert('Failed to activate customers', 'error');
		}
	}

	// Bulk deactivate
	async function bulkDeactivate() {
		if (selectedCustomers.length === 0) {
			showAlert('Please select customers to deactivate');
			return;
		}

		try {
			await bulkUpdateCustomers(selectedCustomers, { is_active: false });
			await loadCustomers();
			await loadCustomerStats();
			selectedCustomers = [];
			allCustomersSelected = false;
			showAlert('Customers deactivated successfully');
		} catch (error) {
			console.error('Failed to deactivate customers:', error);
			showAlert('Failed to deactivate customers', 'error');
		}
	}

	// Debounce search
	let searchTimeout;
	function handleSearch() {
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(() => {
			currentPage = 1;
			loadCustomers();
		}, 500);
	}

	// Filter change handler
	function handleFilterChange() {
		currentPage = 1;
		loadCustomers();
	}

	// Pagination
	function goToPage(page) {
		currentPage = page;
		loadCustomers();
	}

	$: totalPages = Math.ceil(totalCustomers / pageSize);

	// Initialize
	onMount(() => {
		loadCustomers();
		loadCustomerStats();
	});
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Customers</h1>
			<p class="text-sm text-gray-600 mt-1">Manage your customer database</p>
		</div>
		<button on:click={openCreateCustomerModal} class="btn btn-primary">
			<span class="mr-2">➕</span>
			Add Customer
		</button>
	</div>

	<!-- Statistics -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-6">
		<div class="card">
			<div class="card-body">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Total Customers</p>
						<p class="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
					</div>
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
						<span class="text-2xl">👥</span>
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
						<p class="text-sm font-medium text-gray-600">New This Month</p>
						<p class="text-2xl font-bold text-purple-600 mt-1">{stats.new_this_month}</p>
					</div>
					<div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
						<span class="text-2xl">🆕</span>
					</div>
				</div>
			</div>
		</div>

		<div class="card">
			<div class="card-body">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Total Points</p>
						<p class="text-2xl font-bold text-yellow-600 mt-1">{stats.total_points.toLocaleString()}</p>
					</div>
					<div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
						<span class="text-2xl">⭐</span>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Filters and Actions -->
	<div class="card">
		<div class="card-body">
			<div class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
				<div class="flex-1 flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
					<!-- Search -->
					<div class="flex-1">
						<input
							type="text"
							bind:value={searchQuery}
							on:input={handleSearch}
							placeholder="Search customers..."
							class="form-input"
						/>
					</div>

					<!-- Tier Filter -->
					<select bind:value={tierFilter} on:change={handleFilterChange} class="form-select w-full md:w-40">
						<option value="all">All Tiers</option>
						{#each getMembershipTierOptions() as tier}
							<option value={tier.value}>{tier.label}</option>
						{/each}
					</select>

					<!-- Status Filter -->
					<select bind:value={statusFilter} on:change={handleFilterChange} class="form-select w-full md:w-40">
						<option value="all">All Status</option>
						<option value="active">Active</option>
						<option value="inactive">Inactive</option>
					</select>
				</div>
			</div>

			<!-- Bulk Actions -->
			{#if selectedCustomers.length > 0}
				<div class="mt-4 flex items-center justify-between p-3 bg-primary-50 rounded-lg border border-primary-200">
					<span class="text-sm font-medium text-primary-900">
						{selectedCustomers.length} customer{selectedCustomers.length > 1 ? 's' : ''} selected
					</span>
					<div class="flex space-x-2">
						<button on:click={bulkActivate} class="btn btn-success btn-sm">
							Activate Selected
						</button>
						<button on:click={bulkDeactivate} class="btn btn-danger btn-sm">
							Deactivate Selected
						</button>
					</div>
				</div>
			{/if}
		</div>
	</div>

	<!-- Customers Table -->
	<div class="card">
		<div class="card-body p-0">
			{#if customersLoading}
				<div class="text-center py-12">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
					<p class="mt-2 text-sm text-gray-600">Loading customers...</p>
				</div>
			{:else if customers.length === 0}
				<div class="text-center py-12">
					<span class="text-4xl mb-4 block">👥</span>
					<p class="text-gray-500">No customers found</p>
					<button on:click={openCreateCustomerModal} class="btn btn-primary btn-sm mt-4">
						Add Your First Customer
					</button>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th scope="col" class="w-12 px-4 py-3 text-left">
									<input
										type="checkbox"
										checked={allCustomersSelected}
										on:change={toggleAllCustomers}
										class="form-checkbox"
									/>
								</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Customer
								</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Contact
								</th>
								<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Membership
								</th>
								<th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
									Points
								</th>
								<th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
									Orders
								</th>
								<th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
									Total Spent
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
							{#each customers as customer (customer.id)}
								{#if true}
									{@const statusBadge = getStatusBadge(customer.is_active)}
									{@const tierBadge = formatMembershipTier(customer.membership_tier)}
									<tr class="hover:bg-gray-50 transition-colors">
										<td class="px-4 py-4">
											<input
												type="checkbox"
												checked={selectedCustomers.includes(customer.id)}
												on:change={() => toggleCustomerSelection(customer.id)}
												class="form-checkbox"
											/>
										</td>
										<td class="px-6 py-4 whitespace-nowrap">
											<div class="flex items-center">
												<div class="flex-shrink-0 w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
													<span class="text-lg font-bold text-primary-600">{customer.name?.[0]?.toUpperCase()}</span>
												</div>
												<div class="ml-3">
													<p class="text-sm font-medium text-gray-900">{customer.name}</p>
													<p class="text-xs text-gray-500">{customer.membership_number}</p>
												</div>
											</div>
										</td>
										<td class="px-6 py-4">
											<p class="text-sm text-gray-900">{formatPhone(customer.phone)}</p>
											{#if customer.email}
												<p class="text-xs text-gray-500 truncate max-w-[200px]">{customer.email}</p>
											{/if}
										</td>
										<td class="px-6 py-4 whitespace-nowrap">
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {tierBadge.colorClass}">
												{tierBadge.label}
											</span>
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-center">
											<p class="text-sm font-semibold text-gray-900">{customer.points.toLocaleString()}</p>
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-center">
											<p class="text-sm text-gray-900">{customer.total_orders || 0}</p>
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-right">
											<p class="text-sm font-medium text-gray-900">{formatCurrency(customer.total_spent)}</p>
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-center">
											<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {statusBadge.colorClass}">
												{statusBadge.label}
											</span>
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-right">
											<div class="flex items-center justify-end space-x-1">
												<button
													on:click={() => openEditCustomerModal(customer)}
													class="p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
													title="Edit"
												>
													<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
													</svg>
												</button>
												<button
													on:click={() => openPointsModal(customer, 'add')}
													class="p-2 text-green-600 hover:bg-green-50 rounded-md transition-colors"
													title="Add Points"
												>
													<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
													</svg>
												</button>
												<button
													on:click={() => openPointsModal(customer, 'redeem')}
													class="p-2 text-orange-600 hover:bg-orange-50 rounded-md transition-colors"
													title="Redeem Points"
												>
													<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
														<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
													</svg>
												</button>
												<button
													on:click={() => { deletingCustomer = customer; showDeleteModal = true; }}
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
								{/if}
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Pagination -->
				{#if totalPages > 1}
					<div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
						<div class="text-sm text-gray-700">
							Showing page {currentPage} of {totalPages} ({totalCustomers} total)
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

<!-- Customer Modal -->
{#if showCustomerModal}
	<div class="modal">
		<div class="modal-content max-w-3xl">
			<div class="modal-header">
				<h3 class="modal-title">
					{editingCustomer ? 'Edit Customer' : 'Create New Customer'}
				</h3>
				<button on:click={() => (showCustomerModal = false)} class="modal-close">✕</button>
			</div>

			<div class="modal-body">
				<div class="space-y-6">
					<!-- Basic Info -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="md:col-span-2">
							<label for="customer-name" class="form-label required">Customer Name</label>
							<input
								id="customer-name"
								type="text"
								bind:value={customerForm.name}
								class="form-input {errors.name ? 'border-red-500' : ''}"
								placeholder="Enter customer name"
							/>
							{#if errors.name}
								<p class="form-error">{errors.name}</p>
							{/if}
						</div>

						<div>
							<label for="customer-phone" class="form-label required">Phone</label>
							<input
								id="customer-phone"
								type="text"
								bind:value={customerForm.phone}
								class="form-input {errors.phone ? 'border-red-500' : ''}"
								placeholder="+62812345678"
							/>
							{#if errors.phone}
								<p class="form-error">{errors.phone}</p>
							{/if}
						</div>

						<div>
							<label for="customer-email" class="form-label">Email</label>
							<input
								id="customer-email"
								type="email"
								bind:value={customerForm.email}
								class="form-input {errors.email ? 'border-red-500' : ''}"
								placeholder="customer@example.com"
							/>
							{#if errors.email}
								<p class="form-error">{errors.email}</p>
							{/if}
						</div>

						<div>
							<label for="customer-gender" class="form-label">Gender</label>
							<select id="customer-gender" bind:value={customerForm.gender} class="form-select">
								<option value="">Select gender</option>
								{#each getGenderOptions() as gender}
									<option value={gender.value}>{gender.label}</option>
								{/each}
							</select>
							{#if errors.gender}
								<p class="form-error">{errors.gender}</p>
							{/if}
						</div>

						<div>
							<label for="customer-dob" class="form-label">Date of Birth</label>
							<input
								id="customer-dob"
								type="date"
								bind:value={customerForm.date_of_birth}
								class="form-input"
							/>
						</div>
					</div>

					<!-- Address -->
					<div>
						<label for="customer-address" class="form-label">Address</label>
						<textarea
							id="customer-address"
							bind:value={customerForm.address}
							rows="3"
							class="form-input"
							placeholder="Enter customer address"
						></textarea>
					</div>

					<!-- City and Postal Code -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="customer-city" class="form-label">City</label>
							<input
								id="customer-city"
								type="text"
								bind:value={customerForm.city}
								class="form-input"
								placeholder="City"
							/>
						</div>

						<div>
							<label for="customer-postal" class="form-label">Postal Code</label>
							<input
								id="customer-postal"
								type="text"
								bind:value={customerForm.postal_code}
								class="form-input"
								placeholder="12345"
							/>
						</div>
					</div>

					<!-- Membership -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="customer-tier" class="form-label">Membership Tier</label>
							<select id="customer-tier" bind:value={customerForm.membership_tier} class="form-select">
								{#each getMembershipTierOptions() as tier}
									<option value={tier.value}>{tier.label}</option>
								{/each}
							</select>
						</div>

						<div>
							<label for="customer-points" class="form-label">Points</label>
							<input
								id="customer-points"
								type="number"
								bind:value={customerForm.points}
								class="form-input"
								min="0"
							/>
						</div>
					</div>

					<!-- Notes -->
					<div>
						<label for="customer-notes" class="form-label">Notes</label>
						<textarea
							id="customer-notes"
							bind:value={customerForm.notes}
							rows="2"
							class="form-input"
							placeholder="Additional notes about the customer"
						></textarea>
					</div>

					<!-- Checkboxes -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="flex items-center">
							<input
								id="customer-subscribed"
								type="checkbox"
								bind:checked={customerForm.is_subscribed}
								class="form-checkbox"
							/>
							<label for="customer-subscribed" class="ml-2 text-sm text-gray-700">
								Subscribed to marketing
							</label>
						</div>

						<div class="flex items-center">
							<input
								id="customer-active"
								type="checkbox"
								bind:checked={customerForm.is_active}
								class="form-checkbox"
							/>
							<label for="customer-active" class="ml-2 text-sm text-gray-700">
								Active
							</label>
						</div>
					</div>
				</div>
			</div>

			<div class="modal-footer">
				<button on:click={() => (showCustomerModal = false)} class="btn btn-secondary">
					Cancel
				</button>
				<button on:click={handleCustomerSubmit} class="btn btn-primary">
					{editingCustomer ? 'Update Customer' : 'Create Customer'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Points Modal -->
{#if showPointsModal && pointsCustomer}
	<div class="modal">
		<div class="modal-content">
			<div class="modal-header">
				<h3 class="modal-title">
					{pointsAction === 'add' ? 'Add Points' : 'Redeem Points'}
				</h3>
				<button on:click={() => (showPointsModal = false)} class="modal-close">✕</button>
			</div>

			<div class="modal-body">
				<div class="mb-4 p-4 bg-gray-50 rounded-lg">
					<p class="text-sm text-gray-600">Customer</p>
					<p class="font-medium text-gray-900">{pointsCustomer.name}</p>
					<p class="text-sm text-gray-600 mt-2">Current Points</p>
					<p class="text-2xl font-bold text-primary-600">{pointsCustomer.points.toLocaleString()}</p>
				</div>

				<div class="space-y-4">
					<div>
						<label for="points-amount" class="form-label required">Points</label>
						<input
							id="points-amount"
							type="number"
							bind:value={pointsForm.points}
							class="form-input {errors.points ? 'border-red-500' : ''}"
							placeholder="Enter points amount"
							min="1"
						/>
						{#if errors.points}
							<p class="form-error">{errors.points}</p>
						{/if}
					</div>

					<div>
						<label for="points-reason" class="form-label">Reason</label>
						<textarea
							id="points-reason"
							bind:value={pointsForm.reason}
							rows="3"
							class="form-input"
							placeholder="Reason for {pointsAction === 'add' ? 'adding' : 'redeeming'} points"
						></textarea>
					</div>
				</div>
			</div>

			<div class="modal-footer">
				<button on:click={() => (showPointsModal = false)} class="btn btn-secondary">
					Cancel
				</button>
				<button
					on:click={handlePointsAction}
					class="btn {pointsAction === 'add' ? 'btn-success' : 'btn-warning'}"
				>
					{pointsAction === 'add' ? 'Add Points' : 'Redeem Points'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal && deletingCustomer}
	<div class="modal">
		<div class="modal-content">
			<div class="modal-header">
				<h3 class="modal-title">Delete Customer</h3>
				<button on:click={() => (showDeleteModal = false)} class="modal-close">✕</button>
			</div>

			<div class="modal-body">
				<div class="text-center">
					<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
						<span class="text-3xl">⚠️</span>
					</div>
					<p class="text-lg font-semibold text-gray-900 mb-2">Are you sure?</p>
					<p class="text-gray-600 mb-4">
						You are about to delete customer <strong>{deletingCustomer.name}</strong>.
						This action will deactivate the customer.
					</p>
				</div>
			</div>

			<div class="modal-footer">
				<button on:click={() => { showDeleteModal = false; deletingCustomer = null; }} class="btn btn-secondary">
					Cancel
				</button>
				<button on:click={handleDeleteCustomer} class="btn btn-danger">
					Delete Customer
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Toast Notification -->
{#if showToast}
	<div class="fixed top-4 right-4 z-50 animate-slide-in">
		<div class="bg-white rounded-lg shadow-lg border-l-4 {toastType === 'success' ? 'border-green-500' : toastType === 'error' ? 'border-red-500' : 'border-blue-500'} p-4 min-w-[300px] max-w-md">
			<div class="flex items-start">
				<div class="flex-shrink-0">
					{#if toastType === 'success'}
						<svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					{:else if toastType === 'error'}
						<svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					{:else}
						<svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					{/if}
				</div>
				<div class="ml-3 flex-1">
					<p class="text-sm font-medium text-gray-900">{toastMessage}</p>
				</div>
				<button on:click={() => showToast = false} class="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600">
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	@keyframes slide-in {
		from {
			transform: translateX(100%);
			opacity: 0;
		}
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}
	
	.animate-slide-in {
		animation: slide-in 0.3s ease-out;
	}
</style>
