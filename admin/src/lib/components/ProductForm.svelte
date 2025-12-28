<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { getCategories } from '$lib/api/products';

	export let product = null; // If editing
	export let submitting = false;

	const dispatch = createEventDispatcher();

	// Form data
	let formData = {
		name: '',
		description: '',
		sku: '',
		category: '',
		base_price: '',
		cost_price: '',
		promo_price: '',
		stock_quantity: '',
		stock_alert_threshold: '',
		is_active: true,
		is_available: true,
		is_featured: false,
		is_popular: false,
		is_promo: false,
		sort_order: 0,
		image: null
	};

	// Image handling
	let imagePreview = null;
	let imageFile = null;
	let existingImageUrl = null;

	// Categories
	let categories = [];
	let loadingCategories = true;

	// Validation
	let errors = {};

	onMount(async () => {
		await loadCategories();
		
		// Populate form if editing
		if (product) {
			formData = {
				name: product.name || '',
				description: product.description || '',
				sku: product.sku || '',
				category: product.category?.id || '',
				base_price: product.base_price || '',
				cost_price: product.cost_price || '',
				promo_price: product.promo_price || '',
				stock_quantity: product.stock_quantity || '',
				stock_alert_threshold: product.stock_alert_threshold || '',
				is_active: product.is_active ?? true,
				is_available: product.is_available ?? true,
				is_featured: product.is_featured ?? false,
				is_popular: product.is_popular ?? false,
				is_promo: product.is_promo ?? false,
				sort_order: product.sort_order || 0,
				image: null
			};
			
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

		if (!formData.base_price || parseFloat(formData.base_price) <= 0) {
			errors.base_price = 'Base price must be greater than 0';
		}

		if (formData.promo_price && parseFloat(formData.promo_price) >= parseFloat(formData.base_price)) {
			errors.promo_price = 'Promo price must be less than base price';
		}

		return Object.keys(errors).length === 0;
	}

	function handleSubmit() {
		if (!validate()) {
			return;
		}

		// Prepare submission data
		const submitData = new FormData();
		
		// Add all form fields
		Object.keys(formData).forEach(key => {
			if (key !== 'image' && formData[key] !== null && formData[key] !== '') {
				submitData.append(key, formData[key]);
			}
		});

		// Add image if new file selected
		if (imageFile) {
			submitData.append('image', imageFile);
		}

		dispatch('submit', submitData);
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
			<!-- Base Price -->
			<div>
				<label for="base_price" class="block text-sm font-medium text-gray-700 mb-1">
					Base Price <span class="text-red-500">*</span>
				</label>
				<div class="relative">
					<span class="absolute left-3 top-2 text-gray-500">Rp</span>
					<input
						type="number"
						id="base_price"
						bind:value={formData.base_price}
						min="0"
						step="100"
						class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						placeholder="0"
						disabled={submitting}
					/>
				</div>
				{#if errors.base_price}
					<p class="text-red-500 text-sm mt-1">{errors.base_price}</p>
				{/if}
			</div>

			<!-- Cost Price -->
			<div>
				<label for="cost_price" class="block text-sm font-medium text-gray-700 mb-1">
					Cost Price
				</label>
				<div class="relative">
					<span class="absolute left-3 top-2 text-gray-500">Rp</span>
					<input
						type="number"
						id="cost_price"
						bind:value={formData.cost_price}
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

			<!-- Stock Alert Threshold -->
			<div>
				<label for="stock_alert_threshold" class="block text-sm font-medium text-gray-700 mb-1">
					Stock Alert Threshold
				</label>
				<input
					type="number"
					id="stock_alert_threshold"
					bind:value={formData.stock_alert_threshold}
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

			<!-- Is Promo -->
			<label class="flex items-center">
				<input
					type="checkbox"
					bind:checked={formData.is_promo}
					class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
					disabled={submitting}
				/>
				<span class="ml-2 text-sm text-gray-700">On Promotion</span>
			</label>
		</div>
	</div>

	<!-- Sort Order -->
	<div class="space-y-4">
		<h2 class="text-xl font-semibold text-gray-900">Display Order</h2>
		
		<div>
			<label for="sort_order" class="block text-sm font-medium text-gray-700 mb-1">
				Sort Order
			</label>
			<input
				type="number"
				id="sort_order"
				bind:value={formData.sort_order}
				min="0"
				class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				placeholder="0"
				disabled={submitting}
			/>
			<p class="text-sm text-gray-500 mt-1">Lower numbers appear first</p>
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
