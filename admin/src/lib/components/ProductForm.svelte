<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { getCategories } from '$lib/api/products';
	import { getTenants } from '$lib/api/tenants';
	import { getKitchenStationTypes } from '$lib/api/kitchenStationTypes';
	import { user, selectedTenant } from '$lib/stores/auth';
	import { get } from 'svelte/store';

	export let product = null; // If editing
	export let submitting = false;

	const dispatch = createEventDispatcher();

	// Form data
	let formData = {
		name: '',
		description: '',
		sku: '',
		category: '',
		tenant: '',
		kitchen_station_code_override: '',  // Optional override
		price: '',
		cost: '',
		promo_price: '',
		stock_quantity: '',
		low_stock_alert: '',
		is_active: true,
		is_available: true,
		is_featured: false,
		is_popular: false,
		has_promo: false,
		preparation_time: 10,
		tags: '',
		image: null
	};

	// Image handling
	let imagePreview = null;
	let imageFile = null;
	let existingImageUrl = null;

	// Categories and Tenants
	let categories = [];
	let loadingCategories = true;
	let tenants = [];
	let loadingTenants = false;
	let showTenantField = false;
	
	// Kitchen Station Types
	let stationTypes = [];
	let loadingStationTypes = false;

	// Validation
	let errors = {};

	// Reactive: Update showTenantField when user changes
	$: {
		const currentUser = $user;
		const isAdmin = currentUser?.role === 'super_admin' || currentUser?.role === 'admin';
		console.log('Reactive check - User role:', currentUser?.role, 'showTenantField:', isAdmin);
		showTenantField = isAdmin;
		
		// Auto-set tenant for non-admin users
		if (!isAdmin && currentUser?.tenant_id && !formData.tenant) {
			formData.tenant = currentUser.tenant_id;
			console.log('Auto-set tenant from user:', currentUser.tenant_id);
		}
	}

	onMount(async () => {
		console.log('=== ProductForm onMount ===');
		
		// Always load categories
		await loadCategories();
		
		// Load tenants for dropdown
		await loadTenants();
		
		// Load station types for routing
		await loadStationTypes();
		
		// Populate form if editing
		if (product) {
			console.log('Populating form with product data:', product);
			console.log('product.kitchen_station_code_override:', product.kitchen_station_code_override);
			formData = {
				name: product.name || '',
				description: product.description || '',
				sku: product.sku || '',
				category: product.category?.id || product.category || '',
				tenant: product.tenant_id || product.tenant || '',
				kitchen_station_code_override: product.kitchen_station_code_override || '',
				price: product.price || '',
				cost: product.cost || '',
				promo_price: product.promo_price || '',
				stock_quantity: product.stock_quantity || '',
				low_stock_alert: product.low_stock_alert || '',
				is_active: product.is_active ?? true,
				is_available: product.is_available ?? true,
				is_featured: product.is_featured ?? false,
				is_popular: product.is_popular ?? false,
				has_promo: product.has_promo ?? false,
				preparation_time: product.preparation_time || 10,
				tags: product.tags || '',
				image: null
			};
			
			console.log('Form data after population:', formData);
			console.log('formData.kitchen_station_code_override after populate:', formData.kitchen_station_code_override);
			
			if (product.image) {
				existingImageUrl = product.image;
			}
		}
	});

	async function loadCategories() {
		try {
			const response = await getCategories();
			categories = response.results || response;
			loadingCategories = false;
		} catch (error) {
			console.error('Error loading categories:', error);
			loadingCategories = false;
		}
	}

	async function loadTenants() {
		try {
			loadingTenants = true;
			const response = await getTenants();
			tenants = response.results || response;
			console.log('Loaded tenants:', tenants.length);
			loadingTenants = false;
		} catch (error) {
			console.error('Error loading tenants:', error);
			loadingTenants = false;
		}
	}

	async function loadStationTypes() {
		try {
			loadingStationTypes = true;
			const response = await getKitchenStationTypes(get(selectedTenant));
			stationTypes = response.results || response || [];
			stationTypes = stationTypes.filter(t => t.is_active);
			stationTypes.sort((a, b) => a.sort_order - b.sort_order);
			console.log('Loaded station types:', stationTypes.length);
			loadingStationTypes = false;
		} catch (error) {
			console.error('Error loading station types:', error);
			loadingStationTypes = false;
		}
	}

	function getStationType(code) {
		return stationTypes.find(t => t.code === code);
	}

	function getSelectedCategory() {
		return categories.find(c => c.id == formData.category);
	}

	function getEffectiveStationCode() {
		if (formData.kitchen_station_code_override) {
			return formData.kitchen_station_code_override;
		}
		const category = getSelectedCategory();
		return category?.kitchen_station_code || 'MAIN';
	}

	function handleImageChange(event) {
		const file = event.target.files?.[0];
		if (file) {
			imageFile = file;
			
			// Create preview
			const reader = new FileReader();
			reader.onload = (e) => {
				imagePreview = e.target.result;
			};
			reader.readAsDataURL(file);
		}
	}

	function removeImage() {
		imageFile = null;
		imagePreview = null;
		existingImageUrl = null;
		
		// Reset file input
		const fileInput = document.querySelector('input[type="file"]');
		if (fileInput) {
			fileInput.value = '';
		}
	}

	function validate() {
		errors = {};

		if (!formData.name?.trim()) {
			errors.name = 'Product name is required';
		}

		if (!formData.category) {
			errors.category = 'Category is required';
		}

		// Check tenant for super_admin/admin
		const currentUser = get(user);
		if ((currentUser?.role === 'super_admin' || currentUser?.role === 'admin') && !formData.tenant) {
			errors.tenant = 'Tenant is required';
		}

		if (!formData.price || parseFloat(formData.price) <= 0) {
			errors.price = 'Price must be greater than 0';
		}

		if (formData.promo_price && parseFloat(formData.promo_price) >= parseFloat(formData.price)) {
			errors.promo_price = 'Promo price must be less than price';
		}

		return Object.keys(errors).length === 0;
	}

	function handleSubmit() {
		console.log('=== SUBMIT DEBUG ===');
		console.log('showTenantField:', showTenantField);
		console.log('formData.tenant:', formData.tenant);
		console.log('formData.kitchen_station_code_override:', formData.kitchen_station_code_override);
		
		if (!validate()) {
			console.log('Validation failed, errors:', errors);
			return;
		}

		console.log('Form data before submit:', formData);
		
		// If there's an image file, use FormData
		if (imageFile) {
			const submitData = new FormData();
			
			// Add all form fields
			Object.keys(formData).forEach(key => {
				const value = formData[key];
				// Include tenant and kitchen_station_code_override even if empty
				if (key === 'tenant' || key === 'kitchen_station_code_override' || (key !== 'image' && value !== null && value !== undefined && value !== '')) {
					console.log(`Adding field: ${key} = ${value} (${typeof value})`);
					submitData.append(key, value);
				}
			});
			
			// Add image file
			console.log('Adding image file:', imageFile.name);
			submitData.append('image', imageFile);
			
			// Debug: show all FormData entries
			console.log('Sending as FormData with image:');
			for (let pair of submitData.entries()) {
				console.log(`  ${pair[0]}: ${pair[1]}`);
			}
			
			dispatch('submit', submitData);
		} else {
			// No image - send as JSON object (more reliable)
			const submitData = {};
			
			Object.keys(formData).forEach(key => {
				const value = formData[key];
				// Include kitchen_station_code_override even if empty (to clear override)
				if (key === 'kitchen_station_code_override' || (key !== 'image' && value !== null && value !== undefined && value !== '')) {
					submitData[key] = value;
				}
			});
			
			console.log('Sending as JSON (no image):', submitData);
			dispatch('submit', submitData);
		}
	}

	function handleCancel() {
		dispatch('cancel');
	}
</script>

<form on:submit|preventDefault={handleSubmit} class="p-6 space-y-6">
	<!-- Basic Information -->
	<div class="space-y-4">
		<h2 class="text-xl font-semibold text-gray-900">Basic Information</h2>
		
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<!-- Product Name -->
			<div class="md:col-span-2">
				<label for="name" class="block text-sm font-medium text-gray-700 mb-1">
					Product Name <span class="text-red-500">*</span>
				</label>
				<input
					type="text"
					id="name"
					bind:value={formData.name}
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					placeholder="e.g., Nasi Goreng Special"
					disabled={submitting}
				/>
				{#if errors.name}
					<p class="text-red-500 text-sm mt-1">{errors.name}</p>
				{/if}
			</div>

			<!-- SKU -->
			<div>
				<label for="sku" class="block text-sm font-medium text-gray-700 mb-1">
					SKU
				</label>
				<input
					type="text"
					id="sku"
					bind:value={formData.sku}
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					placeholder="e.g., NGS-001"
					disabled={submitting}
				/>
			</div>

			<!-- Category -->
			<div>
				<label for="category" class="block text-sm font-medium text-gray-700 mb-1">
					Category <span class="text-red-500">*</span>
				</label>
				<select
					id="category"
					bind:value={formData.category}
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					disabled={submitting || loadingCategories}
				>
					<option value="">Select category</option>
					{#each categories as cat}
						<option value={cat.id}>{cat.name}</option>
					{/each}
				</select>
				{#if errors.category}
					<p class="text-red-500 text-sm mt-1">{errors.category}</p>
				{/if}
			</div>
		<!-- Kitchen Station Override -->
		<div>
			<label for="kitchen_station" class="block text-sm font-medium text-gray-700 mb-1">
				Kitchen Station Override
				<span class="text-gray-500 text-xs font-normal">(Optional)</span>
			</label>
			<select
				id="kitchen_station"
				bind:value={formData.kitchen_station_code_override}
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				disabled={submitting || loadingStationTypes}
			>
				<option value="">Use category default</option>
				{#each stationTypes as type}
					<option value={type.code}>
						{type.icon} {type.name} ({type.code})
					</option>
				{/each}
			</select>
			<div class="mt-2 flex items-center gap-2 text-xs">
				{#if getEffectiveStationCode()}
					{@const effectiveCode = getEffectiveStationCode()}
					{@const type = getStationType(effectiveCode)}
					<span class="text-gray-600">Effective routing:</span>
					{#if type}
						<span class="text-lg">{type.icon}</span>
						<span 
							class="inline-flex items-center px-2 py-1 rounded-full font-medium"
							style="background-color: {type.color}20; color: {type.color};"
						>
							{effectiveCode}
						</span>
					{:else}
						<span class="inline-flex items-center px-2 py-1 rounded-full font-medium bg-gray-100 text-gray-800">
							{effectiveCode}
						</span>
					{/if}
					{#if formData.kitchen_station_code_override}
						<span class="text-gray-500">(Override)</span>
					{:else}
						<span class="text-gray-500">(From category)</span>
					{/if}
				{/if}
			</div>
		</div>
			<!-- Tenant -->
			{#if $user?.role === 'super_admin' || $user?.role === 'admin'}
			<div>
				<label for="tenant" class="block text-sm font-medium text-gray-700 mb-1">
					Tenant <span class="text-red-500">*</span>
				</label>
				<select
					id="tenant"
					bind:value={formData.tenant}
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					disabled={submitting || loadingTenants}
				>
					<option value="">Select tenant</option>
					{#each tenants as tenant}
						<option value={tenant.id}>{tenant.name}</option>
					{/each}
				</select>
				{#if errors.tenant}
					<p class="text-red-500 text-sm mt-1">{errors.tenant}</p>
				{/if}
			</div>
			{/if}

			<!-- Description -->
			<div class="md:col-span-2">
				<label for="description" class="block text-sm font-medium text-gray-700 mb-1">
					Description
				</label>
				<textarea
					id="description"
					bind:value={formData.description}
					rows="3"
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					placeholder="Describe your product..."
					disabled={submitting}
				></textarea>
			</div>
		</div>
	</div>

	<!-- Pricing -->
	<div class="space-y-4">
		<h2 class="text-xl font-semibold text-gray-900">Pricing</h2>
		
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<!-- Price -->
			<div>
				<label for="price" class="block text-sm font-medium text-gray-700 mb-1">
					Price <span class="text-red-500">*</span>
				</label>
				<div class="relative">
					<span class="absolute left-3 top-2 text-gray-500">Rp</span>
					<input
						type="number"
						id="price"
						bind:value={formData.price}
						min="0"
						step="100"
						class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						placeholder="0"
						disabled={submitting}
					/>
				</div>
				{#if errors.price}
					<p class="text-red-500 text-sm mt-1">{errors.price}</p>
				{/if}
			</div>

			<!-- Cost -->
			<div>
				<label for="cost" class="block text-sm font-medium text-gray-700 mb-1">
					Cost
				</label>
				<div class="relative">
					<span class="absolute left-3 top-2 text-gray-500">Rp</span>
					<input
						type="number"
						id="cost"
						bind:value={formData.cost}
						min="0"
						step="100"
						class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						placeholder="0"
						disabled={submitting}
					/>
				</div>
			</div>

			<!-- Promo Price -->
			<div>
				<label for="promo_price" class="block text-sm font-medium text-gray-700 mb-1">
					Promo Price
				</label>
				<div class="relative">
					<span class="absolute left-3 top-2 text-gray-500">Rp</span>
					<input
						type="number"
						id="promo_price"
						bind:value={formData.promo_price}
						min="0"
						step="100"
						class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						placeholder="0"
						disabled={submitting}
					/>
				</div>
				{#if errors.promo_price}
					<p class="text-red-500 text-sm mt-1">{errors.promo_price}</p>
				{/if}
			</div>
		</div>
	</div>

	<!-- Stock Management -->
	<div class="space-y-4">
		<h2 class="text-xl font-semibold text-gray-900">Stock Management</h2>
		
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<!-- Stock Quantity -->
			<div>
				<label for="stock_quantity" class="block text-sm font-medium text-gray-700 mb-1">
					Stock Quantity
				</label>
				<input
					type="number"
					id="stock_quantity"
					bind:value={formData.stock_quantity}
					min="0"
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					placeholder="0"
					disabled={submitting}
				/>
			</div>

			<!-- Low Stock Alert -->
			<div>
				<label for="low_stock_alert" class="block text-sm font-medium text-gray-700 mb-1">
					Low Stock Alert
				</label>
				<input
					type="number"
					id="low_stock_alert"
					bind:value={formData.low_stock_alert}
					min="0"
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					placeholder="0"
					disabled={submitting}
				/>
			</div>
		</div>
	</div>

	<!-- Product Image -->
	<div class="space-y-4">
		<h2 class="text-xl font-semibold text-gray-900">Product Image</h2>
		
		<div>
			<!-- Current/Preview Image -->
			{#if imagePreview || existingImageUrl}
				<div class="mb-4">
					<img
						src={imagePreview || existingImageUrl}
						alt="Product"
						class="w-48 h-48 object-cover rounded-lg border border-gray-300"
					/>
					<button
						type="button"
						on:click={removeImage}
						class="mt-2 text-sm text-red-600 hover:text-red-800"
						disabled={submitting}
					>
						Remove Image
					</button>
				</div>
			{/if}

			<!-- File Upload -->
			<div class="flex items-center justify-center w-full">
				<label for="image" class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
					<div class="flex flex-col items-center justify-center pt-5 pb-6">
						<svg class="w-8 h-8 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
						</svg>
						<p class="mb-2 text-sm text-gray-500">
							<span class="font-semibold">Click to upload</span> or drag and drop
						</p>
						<p class="text-xs text-gray-500">PNG, JPG or WEBP (MAX. 2MB)</p>
					</div>
					<input
						type="file"
						id="image"
						accept="image/*"
						on:change={handleImageChange}
						class="hidden"
						disabled={submitting}
					/>
				</label>
			</div>
		</div>
	</div>

	<!-- Status Flags -->
	<div class="space-y-4">
		<h2 class="text-xl font-semibold text-gray-900">Status & Visibility</h2>
		
		<div class="space-y-3">
			<!-- Is Active -->
			<label class="flex items-center">
				<input
					type="checkbox"
					bind:checked={formData.is_active}
					class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
					disabled={submitting}
				/>
				<span class="ml-2 text-sm text-gray-700">Active</span>
			</label>

			<!-- Is Available -->
			<label class="flex items-center">
				<input
					type="checkbox"
					bind:checked={formData.is_available}
					class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
					disabled={submitting}
				/>
				<span class="ml-2 text-sm text-gray-700">Available for Sale</span>
			</label>

			<!-- Is Featured -->
			<label class="flex items-center">
				<input
					type="checkbox"
					bind:checked={formData.is_featured}
					class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
					disabled={submitting}
				/>
				<span class="ml-2 text-sm text-gray-700">Featured Product</span>
			</label>

			<!-- Is Popular -->
			<label class="flex items-center">
				<input
					type="checkbox"
					bind:checked={formData.is_popular}
					class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
					disabled={submitting}
				/>
				<span class="ml-2 text-sm text-gray-700">Popular Product</span>
			</label>

			<!-- Has Promo -->
			<label class="flex items-center">
				<input
					type="checkbox"
					bind:checked={formData.has_promo}
					class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
					disabled={submitting}
				/>
				<span class="ml-2 text-sm text-gray-700">On Promotion</span>
			</label>
		</div>
	</div>

	<!-- Additional Information -->
	<div class="space-y-4">
		<h2 class="text-xl font-semibold text-gray-900">Additional Information</h2>
		
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<!-- Preparation Time -->
			<div>
				<label for="preparation_time" class="block text-sm font-medium text-gray-700 mb-1">
					Preparation Time (minutes)
				</label>
				<input
					type="number"
					id="preparation_time"
					bind:value={formData.preparation_time}
					min="1"
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					placeholder="10"
					disabled={submitting}
				/>
			</div>

			<!-- Tags -->
			<div>
				<label for="tags" class="block text-sm font-medium text-gray-700 mb-1">
					Tags (comma-separated)
				</label>
				<input
					type="text"
					id="tags"
					bind:value={formData.tags}
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					placeholder="spicy, vegetarian, halal"
					disabled={submitting}
				/>
				<p class="text-sm text-gray-500 mt-1">Used for search and filtering</p>
			</div>
		</div>
	</div>

	<!-- Form Actions -->
	<div class="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
		<button
			type="button"
			on:click={handleCancel}
			class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
			disabled={submitting}
		>
			Cancel
		</button>
		
		<button
			type="submit"
			class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
			disabled={submitting}
		>
			{#if submitting}
				<span class="flex items-center">
					<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					Saving...
				</span>
			{:else}
				{product ? 'Update Product' : 'Create Product'}
			{/if}
		</button>
	</div>
</form>
