<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import {
		getTenantSettings,
		updateTenantSettings,
		uploadTenantLogo,
		deleteTenantLogo,
		getOutlets,
		getOutletStats,
		createOutlet,
		updateOutlet,
		deleteOutlet,
		bulkUpdateOutlets,
		formatOperatingHours,
		formatAddress,
		formatDate,
		isValidHexColor,
		getStatusBadge,
		getCitiesList,
		getProvincesList
	} from '$lib/api/settings';

	// Safe alert function for SSR compatibility
	function safeAlert(message) {
		if (browser && typeof alert !== 'undefined') {
			safeAlert(message);
		} else {
			console.log('[Alert]:', message);
		}
	}

	// Active tab
	let activeTab = 'tenant'; // 'tenant' or 'outlets'

	// Tenant Settings State
	let tenant = null;
	let tenantLoading = false;
	let tenantSaving = false;
	let showLogoUpload = false;
	let logoFile = null;
	let logoPreview = null;

	// Tenant Form Data
	let tenantForm = {
		name: '',
		description: '',
		phone: '',
		email: '',
		website: '',
		primary_color: '#FF6B35',
		secondary_color: '#F7931E',
		tax_rate: '10.00',
		service_charge_rate: '5.00'
	};

	// Outlets State
	let outlets = [];
	let outletStats = {
		total: 0,
		active: 0,
		inactive: 0,
		by_city: {},
		by_province: {}
	};
	let outletsLoading = false;
	let selectedOutlets = [];
	let allOutletsSelected = false;

	// Filters
	let searchQuery = '';
	let statusFilter = 'all';
	let cityFilter = 'all';
	let provinceFilter = 'all';

	// Pagination
	let currentPage = 1;
	let pageSize = 10;
	let totalOutlets = 0;

	// Modals
	let showOutletModal = false;
	let showDeleteModal = false;
	let editingOutlet = null;
	let deletingOutlet = null;

	// Outlet Form
	let outletForm = {
		name: '',
		address: '',
		city: '',
		province: '',
		postal_code: '',
		phone: '',
		email: '',
		latitude: '',
		longitude: '',
		opening_time: '',
		closing_time: '',
		is_active: true
	};

	// Form errors
	let errors = {};

	// Load tenant settings
	async function loadTenantSettings() {
		if (!browser) return; // Only run in browser
		
		try {
			tenantLoading = true;
			tenant = await getTenantSettings();
			
			// Populate form
			tenantForm = {
				name: tenant.name || '',
				description: tenant.description || '',
				phone: tenant.phone || '',
				email: tenant.email || '',
				website: tenant.website || '',
				primary_color: tenant.primary_color || '#FF6B35',
				secondary_color: tenant.secondary_color || '#F7931E',
				tax_rate: tenant.tax_rate || '10.00',
				service_charge_rate: tenant.service_charge_rate || '5.00'
			};
		} catch (error) {
			console.error('Failed to load tenant settings:', error);
			if (browser && typeof alert !== 'undefined') {
				safeAlert('Failed to load tenant settings');
			}
		} finally {
			tenantLoading = false;
		}
	}

	// Save tenant settings
	async function saveTenantSettings() {
		try {
			// Validate
			errors = {};
			
			if (!tenantForm.name || tenantForm.name.trim() === '') {
				errors.name = 'Tenant name is required';
			}
			
			if (tenantForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(tenantForm.email)) {
				errors.email = 'Invalid email format';
			}
			
			if (!isValidHexColor(tenantForm.primary_color)) {
				errors.primary_color = 'Invalid color format (use #RRGGBB)';
			}
			
			if (!isValidHexColor(tenantForm.secondary_color)) {
				errors.secondary_color = 'Invalid color format (use #RRGGBB)';
			}
			
			if (Object.keys(errors).length > 0) {
				return;
			}
			
			tenantSaving = true;
			tenant = await updateTenantSettings(tenant.id, tenantForm);
			safeAlert('Tenant settings saved successfully');
		} catch (error) {
			console.error('Failed to save tenant settings:', error);
			safeAlert('Failed to save tenant settings');
		} finally {
			tenantSaving = false;
		}
	}

	// Handle logo file selection
	function handleLogoSelect(event) {
		const file = event.target.files[0];
		if (!file) return;
		
		// Validate file type
		if (!file.type.startsWith('image/')) {
			safeAlert('Please select an image file');
			return;
		}
		
		// Validate file size (max 2MB)
		if (file.size > 2 * 1024 * 1024) {
			safeAlert('Image file size must be less than 2MB');
			return;
		}
		
		logoFile = file;
		
		// Generate preview
		const reader = new FileReader();
		reader.onload = (e) => {
			logoPreview = e.target.result;
		};
		reader.readAsDataURL(file);
	}

	// Upload logo
	async function handleLogoUpload() {
		if (!logoFile) {
			safeAlert('Please select a logo file');
			return;
		}
		
		try {
			const result = await uploadTenantLogo(tenant.id, logoFile);
			tenant = result.data;
			logoFile = null;
			logoPreview = null;
			showLogoUpload = false;
			safeAlert('Logo uploaded successfully');
		} catch (error) {
			console.error('Failed to upload logo:', error);
			safeAlert('Failed to upload logo');
		}
	}

	// Delete logo
	async function handleLogoDelete() {
		if (!confirm('Are you sure you want to delete the logo?')) return;
		
		try {
			await deleteTenantLogo(tenant.id);
			tenant.logo_url = null;
			safeAlert('Logo deleted successfully');
		} catch (error) {
			console.error('Failed to delete logo:', error);
			safeAlert('Failed to delete logo');
		}
	}

	// Load outlets
	async function loadOutlets() {
		if (!browser) return; // Only run in browser
		
		try {
			outletsLoading = true;
			
			const filters = {
				search: searchQuery || undefined,
				is_active: statusFilter !== 'all' ? statusFilter === 'active' : undefined,
				city: cityFilter !== 'all' ? cityFilter : undefined,
				province: provinceFilter !== 'all' ? provinceFilter : undefined,
				page: currentPage,
				page_size: pageSize
			};
			
			const response = await getOutlets(filters);
			
			if (response.results) {
				outlets = response.results;
				totalOutlets = response.count;
			} else {
				outlets = response;
				totalOutlets = response.length;
			}
			
			selectedOutlets = [];
			allOutletsSelected = false;
		} catch (error) {
			console.error('Failed to load outlets:', error);
			safeAlert('Failed to load outlets');
		} finally {
			outletsLoading = false;
		}
	}

	// Load outlet stats
	async function loadOutletStats() {
		if (!browser) return; // Only run in browser
		
		try {
			outletStats = await getOutletStats();
		} catch (error) {
			console.error('Failed to load outlet stats:', error);
		}
	}

	// Open outlet modal for create
	function openCreateOutletModal() {
		editingOutlet = null;
		outletForm = {
			name: '',
			address: '',
			city: '',
			province: '',
			postal_code: '',
			phone: '',
			email: '',
			latitude: '',
			longitude: '',
			opening_time: '',
			closing_time: '',
			is_active: true
		};
		errors = {};
		showOutletModal = true;
	}

	// Open outlet modal for edit
	function openEditOutletModal(outlet) {
		editingOutlet = outlet;
		outletForm = {
			name: outlet.name || '',
			address: outlet.address || '',
			city: outlet.city || '',
			province: outlet.province || '',
			postal_code: outlet.postal_code || '',
			phone: outlet.phone || '',
			email: outlet.email || '',
			latitude: outlet.latitude || '',
			longitude: outlet.longitude || '',
			opening_time: outlet.opening_time || '',
			closing_time: outlet.closing_time || '',
			is_active: outlet.is_active
		};
		errors = {};
		showOutletModal = true;
	}

	// Save outlet
	async function handleOutletSubmit() {
		try {
			// Validate
			errors = {};
			
			if (!outletForm.name || outletForm.name.trim() === '') {
				errors.name = 'Outlet name is required';
			}
			
			if (!outletForm.address || outletForm.address.trim() === '') {
				errors.address = 'Address is required';
			}
			
			if (!outletForm.city || outletForm.city.trim() === '') {
				errors.city = 'City is required';
			}
			
			if (!outletForm.phone || outletForm.phone.trim() === '') {
				errors.phone = 'Phone is required';
			}
			
			if (outletForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(outletForm.email)) {
				errors.email = 'Invalid email format';
			}
			
			if (Object.keys(errors).length > 0) {
				return;
			}
			
			if (editingOutlet) {
				await updateOutlet(editingOutlet.id, outletForm);
			} else {
				await createOutlet(outletForm);
			}
			
			showOutletModal = false;
			await loadOutlets();
			await loadOutletStats();
			safeAlert(editingOutlet ? 'Outlet updated successfully' : 'Outlet created successfully');
		} catch (error) {
			console.error('Failed to save outlet:', error);
			safeAlert('Failed to save outlet');
		}
	}

	// Delete outlet
	async function handleDeleteOutlet() {
		try {
			await deleteOutlet(deletingOutlet.id);
			showDeleteModal = false;
			deletingOutlet = null;
			await loadOutlets();
			await loadOutletStats();
			safeAlert('Outlet deleted successfully');
		} catch (error) {
			console.error('Failed to delete outlet:', error);
			safeAlert('Failed to delete outlet');
		}
	}

	// Toggle outlet selection
	function toggleOutletSelection(outletId) {
		if (selectedOutlets.includes(outletId)) {
			selectedOutlets = selectedOutlets.filter((id) => id !== outletId);
		} else {
			selectedOutlets = [...selectedOutlets, outletId];
		}
	}

	// Toggle all outlets selection
	function toggleAllOutlets() {
		if (allOutletsSelected) {
			selectedOutlets = [];
			allOutletsSelected = false;
		} else {
			selectedOutlets = outlets.map((o) => o.id);
			allOutletsSelected = true;
		}
	}

	// Bulk activate
	async function bulkActivate() {
		if (selectedOutlets.length === 0) {
			safeAlert('Please select outlets to activate');
			return;
		}
		
		try {
			await bulkUpdateOutlets(selectedOutlets, { is_active: true });
			await loadOutlets();
			await loadOutletStats();
			selectedOutlets = [];
			allOutletsSelected = false;
			safeAlert('Outlets activated successfully');
		} catch (error) {
			console.error('Failed to activate outlets:', error);
			safeAlert('Failed to activate outlets');
		}
	}

	// Bulk deactivate
	async function bulkDeactivate() {
		if (selectedOutlets.length === 0) {
			safeAlert('Please select outlets to deactivate');
			return;
		}
		
		try {
			await bulkUpdateOutlets(selectedOutlets, { is_active: false });
			await loadOutlets();
			await loadOutletStats();
			selectedOutlets = [];
			allOutletsSelected = false;
			safeAlert('Outlets deactivated successfully');
		} catch (error) {
			console.error('Failed to deactivate outlets:', error);
			safeAlert('Failed to deactivate outlets');
		}
	}

	// Debounce search
	let searchTimeout;
	function handleSearch() {
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(() => {
			currentPage = 1;
			loadOutlets();
		}, 500);
	}

	// Filter change handler
	function handleFilterChange() {
		currentPage = 1;
		loadOutlets();
	}

	// Pagination
	function goToPage(page) {
		currentPage = page;
		loadOutlets();
	}

	$: totalPages = Math.ceil(totalOutlets / pageSize);
	$: availableCities = getCitiesList(outlets);
	$: availableProvinces = getProvincesList(outlets);

	// Initialize
	onMount(() => {
		if (activeTab === 'tenant') {
			loadTenantSettings();
		} else if (activeTab === 'outlets') {
			loadOutlets();
			loadOutletStats();
		}
	});

	// Watch tab changes (only in browser)
	$: if (browser && activeTab === 'tenant' && !tenant) {
		loadTenantSettings();
	}
	$: if (browser && activeTab === 'outlets' && outlets.length === 0) {
		loadOutlets();
		loadOutletStats();
	}
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Settings</h1>
			<p class="text-sm text-gray-600 mt-1">Manage your tenant and outlet settings</p>
		</div>
	</div>

	<!-- Tabs -->
	<div class="border-b border-gray-200">
		<nav class="-mb-px flex space-x-8">
			<button
				on:click={() => (activeTab = 'tenant')}
				class="py-4 px-1 border-b-2 font-medium text-sm transition-colors {activeTab === 'tenant'
					? 'border-primary-500 text-primary-600'
					: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
			>
				<span class="flex items-center">
					<span class="mr-2">🏢</span>
					Tenant Settings
				</span>
			</button>
			<button
				on:click={() => (activeTab = 'outlets')}
				class="py-4 px-1 border-b-2 font-medium text-sm transition-colors {activeTab === 'outlets'
					? 'border-primary-500 text-primary-600'
					: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
			>
				<span class="flex items-center">
					<span class="mr-2">📍</span>
					Outlets
				</span>
			</button>
		</nav>
	</div>

	<!-- Tenant Settings Tab -->
	{#if activeTab === 'tenant'}
		<div class="space-y-6">
			{#if tenantLoading}
				<div class="text-center py-12">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
					<p class="mt-2 text-sm text-gray-600">Loading settings...</p>
				</div>
			{:else if tenant}
				<!-- Logo Section -->
				<div class="card">
					<div class="card-header">
						<h2 class="text-lg font-semibold">Tenant Logo</h2>
					</div>
					<div class="card-body">
						<div class="flex items-center space-x-6">
							{#if tenant.logo_url}
								<div class="flex-shrink-0">
									<img src={tenant.logo_url} alt="Tenant Logo" class="w-32 h-32 object-contain rounded-lg border-2 border-gray-200" />
								</div>
								<div class="flex-1">
									<p class="text-sm text-gray-600 mb-3">Current logo</p>
									<div class="flex space-x-2">
										<button on:click={() => (showLogoUpload = true)} class="btn btn-secondary btn-sm">
											Change Logo
										</button>
										<button on:click={handleLogoDelete} class="btn btn-danger btn-sm">
											Delete Logo
										</button>
									</div>
								</div>
							{:else}
								<div class="flex-shrink-0">
									<div class="w-32 h-32 flex items-center justify-center bg-gray-100 rounded-lg border-2 border-dashed border-gray-300">
										<span class="text-4xl text-gray-400">🏪</span>
									</div>
								</div>
								<div class="flex-1">
									<p class="text-sm text-gray-600 mb-3">No logo uploaded</p>
									<button on:click={() => (showLogoUpload = true)} class="btn btn-primary btn-sm">
										Upload Logo
									</button>
								</div>
							{/if}
						</div>

						{#if showLogoUpload}
							<div class="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
								<h3 class="text-sm font-medium text-gray-900 mb-3">Upload New Logo</h3>
								<div class="space-y-3">
									<input
										type="file"
										accept="image/*"
										on:change={handleLogoSelect}
										class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
									/>
									{#if logoPreview}
										<img src={logoPreview} alt="Logo Preview" class="w-32 h-32 object-contain rounded-lg border-2 border-gray-200" />
									{/if}
									<div class="flex space-x-2">
										<button on:click={handleLogoUpload} class="btn btn-primary btn-sm">
											Upload
										</button>
										<button on:click={() => { showLogoUpload = false; logoFile = null; logoPreview = null; }} class="btn btn-secondary btn-sm">
											Cancel
										</button>
									</div>
								</div>
							</div>
						{/if}
					</div>
				</div>

				<!-- Business Information -->
				<div class="card">
					<div class="card-header">
						<h2 class="text-lg font-semibold">Business Information</h2>
					</div>
					<div class="card-body">
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<!-- Tenant Name -->
							<div>
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

							<!-- Phone -->
							<div>
								<label for="tenant-phone" class="form-label">Phone</label>
								<input
									id="tenant-phone"
									type="text"
									bind:value={tenantForm.phone}
									class="form-input"
									placeholder="Enter phone number"
								/>
							</div>

							<!-- Email -->
							<div>
								<label for="tenant-email" class="form-label">Email</label>
								<input
									id="tenant-email"
									type="email"
									bind:value={tenantForm.email}
									class="form-input {errors.email ? 'border-red-500' : ''}"
									placeholder="Enter email address"
								/>
								{#if errors.email}
									<p class="form-error">{errors.email}</p>
								{/if}
							</div>

							<!-- Website -->
							<div>
								<label for="tenant-website" class="form-label">Website</label>
								<input
									id="tenant-website"
									type="url"
									bind:value={tenantForm.website}
									class="form-input"
									placeholder="https://example.com"
								/>
							</div>

							<!-- Description (full width) -->
							<div class="md:col-span-2">
								<label for="tenant-description" class="form-label">Description</label>
								<textarea
									id="tenant-description"
									bind:value={tenantForm.description}
									rows="3"
									class="form-input"
									placeholder="Enter tenant description"
								></textarea>
							</div>
						</div>
					</div>
				</div>

				<!-- Branding -->
				<div class="card">
					<div class="card-header">
						<h2 class="text-lg font-semibold">Branding Colors</h2>
					</div>
					<div class="card-body">
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<!-- Primary Color -->
							<div>
								<label for="primary-color" class="form-label required">Primary Color</label>
								<div class="flex items-center space-x-3">
									<input
										id="primary-color"
										type="color"
										bind:value={tenantForm.primary_color}
										class="h-10 w-20 rounded-lg border border-gray-300 cursor-pointer"
									/>
									<input
										type="text"
										bind:value={tenantForm.primary_color}
										class="form-input flex-1 {errors.primary_color ? 'border-red-500' : ''}"
										placeholder="#FF6B35"
									/>
								</div>
								{#if errors.primary_color}
									<p class="form-error">{errors.primary_color}</p>
								{/if}
							</div>

							<!-- Secondary Color -->
							<div>
								<label for="secondary-color" class="form-label required">Secondary Color</label>
								<div class="flex items-center space-x-3">
									<input
										id="secondary-color"
										type="color"
										bind:value={tenantForm.secondary_color}
										class="h-10 w-20 rounded-lg border border-gray-300 cursor-pointer"
									/>
									<input
										type="text"
										bind:value={tenantForm.secondary_color}
										class="form-input flex-1 {errors.secondary_color ? 'border-red-500' : ''}"
										placeholder="#F7931E"
									/>
								</div>
								{#if errors.secondary_color}
									<p class="form-error">{errors.secondary_color}</p>
								{/if}
							</div>
						</div>
					</div>
				</div>

				<!-- Financial Settings -->
				<div class="card">
					<div class="card-header">
						<h2 class="text-lg font-semibold">Financial Settings</h2>
					</div>
					<div class="card-body">
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<!-- Tax Rate -->
							<div>
								<label for="tax-rate" class="form-label required">Tax Rate (%)</label>
								<input
									id="tax-rate"
									type="number"
									step="0.01"
									min="0"
									max="100"
									bind:value={tenantForm.tax_rate}
									class="form-input"
									placeholder="10.00"
								/>
								<p class="text-xs text-gray-500 mt-1">Enter tax rate as percentage (e.g., 10.00 for 10%)</p>
							</div>

							<!-- Service Charge Rate -->
							<div>
								<label for="service-charge-rate" class="form-label required">Service Charge (%)</label>
								<input
									id="service-charge-rate"
									type="number"
									step="0.01"
									min="0"
									max="100"
									bind:value={tenantForm.service_charge_rate}
									class="form-input"
									placeholder="5.00"
								/>
								<p class="text-xs text-gray-500 mt-1">Enter service charge as percentage (e.g., 5.00 for 5%)</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Save Button -->
				<div class="flex justify-end">
					<button
						on:click={saveTenantSettings}
						disabled={tenantSaving}
						class="btn btn-primary"
					>
						{tenantSaving ? 'Saving...' : 'Save Settings'}
					</button>
				</div>
			{/if}
		</div>
	{/if}

	<!-- Outlets Tab -->
	{#if activeTab === 'outlets'}
		<div class="space-y-6">
			<!-- Statistics -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-6">
				<div class="card">
					<div class="card-body">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm font-medium text-gray-600">Total Outlets</p>
								<p class="text-2xl font-bold text-gray-900 mt-1">{outletStats.total}</p>
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
								<p class="text-2xl font-bold text-green-600 mt-1">{outletStats.active}</p>
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
								<p class="text-2xl font-bold text-red-600 mt-1">{outletStats.inactive}</p>
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
								<p class="text-2xl font-bold text-purple-600 mt-1">{Object.keys(outletStats.by_city).length}</p>
							</div>
							<div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
								<span class="text-2xl">🏙️</span>
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
									placeholder="Search outlets..."
									class="form-input"
								/>
							</div>

							<!-- Status Filter -->
							<select bind:value={statusFilter} on:change={handleFilterChange} class="form-select w-full md:w-40">
								<option value="all">All Status</option>
								<option value="active">Active</option>
								<option value="inactive">Inactive</option>
							</select>

							<!-- City Filter -->
							<select bind:value={cityFilter} on:change={handleFilterChange} class="form-select w-full md:w-40">
								<option value="all">All Cities</option>
								{#each availableCities as city}
									<option value={city}>{city}</option>
								{/each}
							</select>
						</div>

						<button on:click={openCreateOutletModal} class="btn btn-primary whitespace-nowrap">
							<span class="mr-2">➕</span>
							Add Outlet
						</button>
					</div>

					<!-- Bulk Actions -->
					{#if selectedOutlets.length > 0}
						<div class="mt-4 flex items-center justify-between p-3 bg-primary-50 rounded-lg border border-primary-200">
							<span class="text-sm font-medium text-primary-900">
								{selectedOutlets.length} outlet{selectedOutlets.length > 1 ? 's' : ''} selected
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

			<!-- Outlets Table -->
			<div class="card">
				<div class="card-body p-0">
					{#if outletsLoading}
						<div class="text-center py-12">
							<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
							<p class="mt-2 text-sm text-gray-600">Loading outlets...</p>
						</div>
					{:else if outlets.length === 0}
						<div class="text-center py-12">
							<span class="text-4xl mb-4 block">📍</span>
							<p class="text-gray-500">No outlets found</p>
							<button on:click={openCreateOutletModal} class="btn btn-primary btn-sm mt-4">
								Add Your First Outlet
							</button>
						</div>
					{:else}
						<div class="overflow-x-auto">
							<table class="table">
								<thead class="table-header">
									<tr>
										<th class="w-12">
											<input
												type="checkbox"
												checked={allOutletsSelected}
												on:change={toggleAllOutlets}
												class="form-checkbox"
											/>
										</th>
										<th>Outlet</th>
										<th>Location</th>
										<th>Contact</th>
										<th>Operating Hours</th>
										<th>Status</th>
										<th class="text-right">Actions</th>
									</tr>
								</thead>
								<tbody class="table-body">
									{#each outlets as outlet (outlet.id)}
										{#if true}
											{@const statusBadge = getStatusBadge(outlet.is_active)}
											<tr class="hover:bg-gray-50">
												<td>
													<input
														type="checkbox"
														checked={selectedOutlets.includes(outlet.id)}
														on:change={() => toggleOutletSelection(outlet.id)}
														class="form-checkbox"
													/>
												</td>
												<td>
													<div class="flex items-center">
														<div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center mr-3">
															<span class="text-lg">📍</span>
														</div>
														<div>
															<p class="font-medium text-gray-900">{outlet.name}</p>
															<p class="text-xs text-gray-500">ID: {outlet.id}</p>
														</div>
													</div>
												</td>
												<td>
													<p class="text-sm text-gray-900">{outlet.city}, {outlet.province}</p>
													<p class="text-xs text-gray-500">{outlet.address}</p>
												</td>
												<td>
													<p class="text-sm text-gray-900">{outlet.phone}</p>
													{#if outlet.email}
														<p class="text-xs text-gray-500">{outlet.email}</p>
													{/if}
												</td>
												<td>
													<p class="text-sm text-gray-900">{formatOperatingHours(outlet.opening_time, outlet.closing_time)}</p>
												</td>
												<td>
													<span class="badge {statusBadge.colorClass}">
														{statusBadge.label}
													</span>
												</td>
												<td class="text-right">
													<div class="flex items-center justify-end space-x-2">
														<button
															on:click={() => openEditOutletModal(outlet)}
															class="btn-icon btn-icon-primary"
															title="Edit"
														>
															✏️
														</button>
														<button
															on:click={() => { deletingOutlet = outlet; showDeleteModal = true; }}
															class="btn-icon btn-icon-danger"
															title="Delete"
														>
															🗑️
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
							<div class="border-t border-gray-200 px-6 py-4">
								<div class="flex items-center justify-between">
									<div class="text-sm text-gray-700">
										Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, totalOutlets)} of {totalOutlets} outlets
									</div>
									<div class="flex space-x-2">
										<button
											on:click={() => goToPage(currentPage - 1)}
											disabled={currentPage === 1}
											class="btn btn-secondary btn-sm"
										>
											Previous
										</button>
										<span class="px-4 py-2 text-sm text-gray-700">
											Page {currentPage} of {totalPages}
										</span>
										<button
											on:click={() => goToPage(currentPage + 1)}
											disabled={currentPage === totalPages}
											class="btn btn-secondary btn-sm"
										>
											Next
										</button>
									</div>
								</div>
							</div>
						{/if}
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>

<!-- Outlet Modal -->
{#if showOutletModal}
	<div class="modal">
		<div class="modal-content max-w-3xl">
			<div class="modal-header">
				<h3 class="modal-title">
					{editingOutlet ? 'Edit Outlet' : 'Create New Outlet'}
				</h3>
				<button on:click={() => (showOutletModal = false)} class="modal-close">✕</button>
			</div>

			<div class="modal-body">
				<div class="space-y-6">
					<!-- Outlet Name and Status -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
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

						<div>
							<label class="form-label">Status</label>
							<div class="flex items-center mt-2">
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

					<!-- Address -->
					<div>
						<label for="outlet-address" class="form-label required">Address</label>
						<textarea
							id="outlet-address"
							bind:value={outletForm.address}
							rows="3"
							class="form-input {errors.address ? 'border-red-500' : ''}"
							placeholder="Enter complete address"
						></textarea>
						{#if errors.address}
							<p class="form-error">{errors.address}</p>
						{/if}
					</div>

					<!-- City, Province, Postal Code -->
					<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
								placeholder="Phone number"
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
								class="form-input {errors.email ? 'border-red-500' : ''}"
								placeholder="Email address"
							/>
							{#if errors.email}
								<p class="form-error">{errors.email}</p>
							{/if}
						</div>
					</div>

					<!-- Coordinates -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label for="outlet-latitude" class="form-label">Latitude</label>
							<input
								id="outlet-latitude"
								type="text"
								bind:value={outletForm.latitude}
								class="form-input"
								placeholder="e.g., -6.200000"
							/>
						</div>

						<div>
							<label for="outlet-longitude" class="form-label">Longitude</label>
							<input
								id="outlet-longitude"
								type="text"
								bind:value={outletForm.longitude}
								class="form-input"
								placeholder="e.g., 106.816666"
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
				</div>
			</div>

			<div class="modal-footer">
				<button on:click={() => (showOutletModal = false)} class="btn btn-secondary">
					Cancel
				</button>
				<button on:click={handleOutletSubmit} class="btn btn-primary">
					{editingOutlet ? 'Update Outlet' : 'Create Outlet'}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal && deletingOutlet}
	<div class="modal">
		<div class="modal-content">
			<div class="modal-header">
				<h3 class="modal-title">Delete Outlet</h3>
				<button on:click={() => (showDeleteModal = false)} class="modal-close">✕</button>
			</div>

			<div class="modal-body">
				<div class="text-center">
					<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
						<span class="text-3xl">⚠️</span>
					</div>
					<p class="text-lg font-semibold text-gray-900 mb-2">Are you sure?</p>
					<p class="text-gray-600 mb-4">
						You are about to delete the outlet <strong>{deletingOutlet.name}</strong>.
						This action will deactivate the outlet.
					</p>
				</div>
			</div>

			<div class="modal-footer">
				<button on:click={() => { showDeleteModal = false; deletingOutlet = null; }} class="btn btn-secondary">
					Cancel
				</button>
				<button on:click={handleDeleteOutlet} class="btn btn-danger">
					Delete Outlet
				</button>
			</div>
		</div>
	</div>
{/if}
