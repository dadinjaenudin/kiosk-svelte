<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getPromotion, updatePromotion } from '$lib/api/promotions';
	import { user } from '$lib/stores/auth';
	import ProductSelector from '$lib/components/ProductSelector.svelte';
	import SchedulePicker from '$lib/components/SchedulePicker.svelte';
	import Swal from 'sweetalert2';

	$: id = $page.params.id;

	// Form data
	let formData = {
		name: '',
		description: '',
		code: '',
		tenant: null,
		promo_type: 'percentage',
		discount_value: '',
		max_discount_amount: '',
		min_purchase_amount: '0',
		buy_quantity: '',
		get_quantity: '',
		start_date: '',
		end_date: '',
		monday: true,
		tuesday: true,
		wednesday: true,
		thursday: true,
		friday: true,
		saturday: true,
		sunday: true,
		time_start: '',
		time_end: '',
		usage_limit: '',
		usage_limit_per_customer: '',
		status: 'draft',
		is_active: false,
		is_featured: false,
		product_ids: []
	};

	let loading = false;
	let loadingData = true;
	let error = '';
	let errors = {};
	let selectedProducts = [];

	const promoTypes = [
		{ value: 'percentage', label: 'Percentage Discount', icon: '%' },
		{ value: 'fixed', label: 'Fixed Amount', icon: 'Rp' },
		{ value: 'buy_x_get_y', label: 'Buy X Get Y', icon: '+' },
		{ value: 'bundle', label: 'Bundle Deal', icon: '📦' }
	];

	onMount(() => {
		loadPromotion();
	});

	async function loadPromotion() {
		try {
			loadingData = true;
			const promotion = await getPromotion(id);
			
			// Populate form with existing data
			formData = {
				name: promotion.name || '',
				description: promotion.description || '',
				code: promotion.code || '',
				tenant: promotion.tenant || null,
				promo_type: promotion.promo_type || 'percentage',
				discount_value: promotion.discount_value || '',
				max_discount_amount: promotion.max_discount_amount || '',
				min_purchase_amount: promotion.min_purchase_amount || '0',
				buy_quantity: promotion.buy_quantity || '',
				get_quantity: promotion.get_quantity || '',
				start_date: formatDateTimeForInput(new Date(promotion.start_date)),
				end_date: formatDateTimeForInput(new Date(promotion.end_date)),
				monday: promotion.monday !== undefined ? promotion.monday : true,
				tuesday: promotion.tuesday !== undefined ? promotion.tuesday : true,
				wednesday: promotion.wednesday !== undefined ? promotion.wednesday : true,
				thursday: promotion.thursday !== undefined ? promotion.thursday : true,
				friday: promotion.friday !== undefined ? promotion.friday : true,
				saturday: promotion.saturday !== undefined ? promotion.saturday : true,
				sunday: promotion.sunday !== undefined ? promotion.sunday : true,
				time_start: promotion.time_start || '',
				time_end: promotion.time_end || '',
				usage_limit: promotion.usage_limit || '',
				usage_limit_per_customer: promotion.usage_limit_per_customer || '',
				status: promotion.status || 'draft',
				is_active: promotion.is_active || false,
				is_featured: promotion.is_featured || false,
				product_ids: []
			};

			// Set selected products only if they exist and are valid
			// Filter out any products that might have been deleted
			if (promotion.products && promotion.products.length > 0) {
				console.log('📦 Raw promotion.products from API:', promotion.products);
				console.log('📦 First product structure:', JSON.stringify(promotion.products[0], null, 2));
				
				// Map PromotionProduct objects to product objects for ProductSelector
				selectedProducts = promotion.products
					.filter(pp => pp && (pp.product_id || pp.product))
					.map(pp => {
						const productId = pp.product_id || pp.product;
						const productName = pp.product_name;
						const productPrice = pp.product_price;
						const productRole = pp.product_role || 'both';
						
						console.log(`🔍 Mapping product ${productId}:`, {
							id: productId,
							name: productName,
							price: productPrice,
							role: productRole,
							hasName: !!productName,
							hasPrice: productPrice !== null && productPrice !== undefined
						});
						
						return {
							id: productId,
							name: productName || `Product ${productId}`,
							price: productPrice !== null && productPrice !== undefined ? productPrice : 0,
							role: productRole
						};
					});
				
				formData.product_ids = selectedProducts.map(p => p.id);
				console.log('✅ Loaded products:', selectedProducts);
				console.log('✅ Product IDs:', formData.product_ids);
			} else {
				console.log('⚠️ No products found in promotion data');
			}
		} catch (err) {
			console.error('Error loading promotion:', err);
			error = err.message;
			Swal.fire('Error!', 'Failed to load promotion data', 'error');
		} finally {
			loadingData = false;
		}
	}

	function formatDateTimeForInput(date) {
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, '0');
		const day = String(date.getDate()).padStart(2, '0');
		const hours = String(date.getHours()).padStart(2, '0');
		const minutes = String(date.getMinutes()).padStart(2, '0');
		return `${year}-${month}-${day}T${hours}:${minutes}`;
	}

	function validate() {
		errors = {};

		if (!formData.name.trim()) {
			errors.name = 'Promotion name is required';
		}

		if (!formData.discount_value || parseFloat(formData.discount_value) <= 0) {
			errors.discount_value = 'Discount value must be greater than 0';
		}

		if (formData.promo_type === 'percentage' && parseFloat(formData.discount_value) > 100) {
			errors.discount_value = 'Percentage cannot exceed 100%';
		}

		if (formData.promo_type === 'buy_x_get_y') {
			if (!formData.buy_quantity || parseInt(formData.buy_quantity) <= 0) {
				errors.buy_quantity = 'Buy quantity is required';
			}
			if (!formData.get_quantity || parseInt(formData.get_quantity) <= 0) {
				errors.get_quantity = 'Get quantity is required';
			}
		}

		if (!formData.start_date) {
			errors.start_date = 'Start date is required';
		}

		if (!formData.end_date) {
			errors.end_date = 'End date is required';
		}

		if (formData.start_date && formData.end_date) {
			const start = new Date(formData.start_date);
			const end = new Date(formData.end_date);
			if (start >= end) {
				errors.end_date = 'End date must be after start date';
			}
		}

		return Object.keys(errors).length === 0;
	}

	async function handleSubmit() {
		if (!validate()) {
			error = 'Please fix the errors in the form';
			return;
		}

		try {
			loading = true;
			error = '';

			// Prepare products with roles for Buy X Get Y
			const productsWithRoles = selectedProducts.map(p => ({
				id: p.id,
				role: p.role || 'both'
			}));

			// Prepare data for submission
			const submitData = {
				...formData,
				products_with_roles: productsWithRoles,
				discount_value: parseFloat(formData.discount_value),
				max_discount_amount: formData.max_discount_amount
					? parseFloat(formData.max_discount_amount)
					: null,
				min_purchase_amount: parseFloat(formData.min_purchase_amount) || 0,
				buy_quantity: formData.buy_quantity ? parseInt(formData.buy_quantity) : null,
				get_quantity: formData.get_quantity ? parseInt(formData.get_quantity) : null,
				usage_limit: formData.usage_limit ? parseInt(formData.usage_limit) : null,
				usage_limit_per_customer: formData.usage_limit_per_customer
					? parseInt(formData.usage_limit_per_customer)
					: null
			};

			// Remove empty strings
			Object.keys(submitData).forEach((key) => {
				if (submitData[key] === '') {
					submitData[key] = null;
				}
			});

			console.log('📤 Updating promotion:', submitData);

			await updatePromotion(id, submitData);
			
			await Swal.fire('Success!', 'Promotion updated successfully', 'success');
			goto(`/promotions/${id}`);
		} catch (err) {
			console.error('❌ Error updating promotion:', err);
			error = err.message;
			Swal.fire('Error!', err.message, 'error');
		} finally {
			loading = false;
		}
	}

	function handleProductsChange(event) {
		selectedProducts = event.detail;
		// Filter out any invalid products (products without valid IDs)
		const validProducts = selectedProducts.filter(p => p && p.id && typeof p.id === 'number');
		formData.product_ids = validProducts.map((p) => p.id);
		console.log('✅ Valid product IDs:', formData.product_ids);
	}

	function handleScheduleChange(event) {
		const schedule = event.detail;
		formData.start_date = schedule.start_date;
		formData.end_date = schedule.end_date;
		formData.monday = schedule.days.monday;
		formData.tuesday = schedule.days.tuesday;
		formData.wednesday = schedule.days.wednesday;
		formData.thursday = schedule.days.thursday;
		formData.friday = schedule.days.friday;
		formData.saturday = schedule.days.saturday;
		formData.sunday = schedule.days.sunday;
		formData.time_start = schedule.time_start || '';
		formData.time_end = schedule.time_end || '';
		delete errors.start_date;
		delete errors.end_date;
	}
</script>

<svelte:head>
	<title>Edit Promotion - Admin Panel</title>
</svelte:head>

<div class="p-6 max-w-5xl mx-auto">
	<!-- Header -->
	<div class="mb-6">
		<button
			on:click={() => goto(`/promotions/${id}`)}
			class="text-gray-600 hover:text-gray-900 mb-4 inline-flex items-center gap-2"
		>
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M10 19l-7-7m0 0l7-7m-7 7h18"
				/>
			</svg>
			Back to Promotion
		</button>
		<h1 class="text-2xl font-bold text-gray-900">Edit Promotion</h1>
		<p class="text-gray-600 mt-1">Update promotion details and settings</p>
	</div>

	{#if loadingData}
		<div class="flex justify-center items-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
		</div>
	{:else}
		<!-- Error Message -->
		{#if error}
			<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
				{error}
			</div>
		{/if}

		<form on:submit|preventDefault={handleSubmit} class="space-y-6">
			<!-- Basic Information -->
			<div class="bg-white rounded-lg shadow-sm p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<!-- Promotion Name -->
					<div class="md:col-span-2">
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Promotion Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.name}
							placeholder="e.g., Weekend Special 50% Off"
							class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 {errors.name
								? 'border-red-500'
								: 'border-gray-300'}"
						/>
						{#if errors.name}
							<p class="mt-1 text-sm text-red-600">{errors.name}</p>
						{/if}
					</div>

					<!-- Description -->
					<div class="md:col-span-2">
						<label class="block text-sm font-medium text-gray-700 mb-2"> Description </label>
						<textarea
							bind:value={formData.description}
							rows="3"
							placeholder="Describe the promotion details..."
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						></textarea>
					</div>

					<!-- Promo Code (Optional) -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Promo Code (Optional)
						</label>
						<input
							type="text"
							bind:value={formData.code}
							placeholder="e.g., WEEKEND50"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>

					<!-- Status -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2"> Status </label>
						<select
							bind:value={formData.status}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						>
							<option value="draft">Draft</option>
							<option value="scheduled">Scheduled</option>
							<option value="active">Active</option>
							<option value="expired">Expired</option>
							<option value="paused">Paused</option>
						</select>
					</div>
				</div>

				<!-- Flags -->
				<div class="mt-6 flex gap-6">
					<label class="flex items-center gap-2">
						<input
							type="checkbox"
							bind:checked={formData.is_active}
							class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
						/>
						<span class="text-sm text-gray-700">Active now</span>
					</label>
					<label class="flex items-center gap-2">
						<input
							type="checkbox"
							bind:checked={formData.is_featured}
							class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
						/>
						<span class="text-sm text-gray-700">Featured promotion</span>
					</label>
				</div>
			</div>

			<!-- Promotion Type & Discount -->
			<div class="bg-white rounded-lg shadow-sm p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Discount Configuration</h2>

				<!-- Promo Type Selector -->
				<div class="mb-6">
					<label class="block text-sm font-medium text-gray-700 mb-3">
						Promotion Type <span class="text-red-500">*</span>
					</label>
					<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
						{#each promoTypes as type}
							<button
								type="button"
								on:click={() => (formData.promo_type = type.value)}
								class="p-4 border-2 rounded-lg text-center transition-all {formData.promo_type ===
								type.value
									? 'border-blue-600 bg-blue-50 text-blue-900'
									: 'border-gray-300 hover:border-gray-400'}"
							>
								<div class="text-2xl mb-2">{type.icon}</div>
								<div class="text-sm font-medium">{type.label}</div>
							</button>
						{/each}
					</div>
				</div>

				<!-- Discount Value -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Discount Value <span class="text-red-500">*</span>
						</label>
						<div class="relative">
							<input
								type="number"
								bind:value={formData.discount_value}
								step="0.01"
								min="0"
								{...(formData.promo_type === 'percentage' ? { max: 100 } : {})}
								class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 {errors.discount_value
									? 'border-red-500'
									: 'border-gray-300'}"
							/>
							<span class="absolute right-3 top-2.5 text-gray-500">
								{formData.promo_type === 'percentage' ? '%' : 'IDR'}
							</span>
						</div>
						{#if errors.discount_value}
							<p class="mt-1 text-sm text-red-600">{errors.discount_value}</p>
						{/if}
					</div>

					<!-- Max Discount (for percentage) -->
					{#if formData.promo_type === 'percentage'}
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">
								Max Discount Amount (Optional)
							</label>
							<input
								type="number"
								bind:value={formData.max_discount_amount}
								step="1000"
								min="0"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>
					{/if}

					<!-- Min Purchase -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Minimum Purchase Amount
						</label>
						<input
							type="number"
							bind:value={formData.min_purchase_amount}
							step="1000"
							min="0"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				<!-- Buy X Get Y Fields -->
				{#if formData.promo_type === 'buy_x_get_y'}
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6 p-4 bg-blue-50 rounded-lg">
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">
								Buy Quantity <span class="text-red-500">*</span>
							</label>
							<input
								type="number"
								bind:value={formData.buy_quantity}
								min="1"
								class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 {errors.buy_quantity
									? 'border-red-500'
									: 'border-gray-300'}"
							/>
							{#if errors.buy_quantity}
								<p class="mt-1 text-sm text-red-600">{errors.buy_quantity}</p>
							{/if}
						</div>
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">
								Get Quantity <span class="text-red-500">*</span>
							</label>
							<input
								type="number"
								bind:value={formData.get_quantity}
								min="1"
								class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 {errors.get_quantity
									? 'border-red-500'
									: 'border-gray-300'}"
							/>
							{#if errors.get_quantity}
								<p class="mt-1 text-sm text-red-600">{errors.get_quantity}</p>
							{/if}
						</div>
					</div>
				{/if}
			</div>

			<!-- Product Selection -->
			<div class="bg-white rounded-lg shadow-sm p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Select Products</h2>
				<ProductSelector
					tenantId={formData.tenant}
					promoType={formData.promo_type}
					selected={selectedProducts}
					on:change={handleProductsChange}
				/>
			</div>

			<!-- Schedule -->
			<div class="bg-white rounded-lg shadow-sm p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Schedule</h2>
				<SchedulePicker
					startDate={formData.start_date}
					endDate={formData.end_date}
					days={{
						monday: formData.monday,
						tuesday: formData.tuesday,
						wednesday: formData.wednesday,
						thursday: formData.thursday,
						friday: formData.friday,
						saturday: formData.saturday,
						sunday: formData.sunday
					}}
					timeStart={formData.time_start}
					timeEnd={formData.time_end}
					on:change={handleScheduleChange}
					{errors}
				/>
			</div>

			<!-- Usage Limits -->
			<div class="bg-white rounded-lg shadow-sm p-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Usage Limits (Optional)</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Total Usage Limit
						</label>
						<input
							type="number"
							bind:value={formData.usage_limit}
							min="1"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							Usage Limit Per Customer
						</label>
						<input
							type="number"
							bind:value={formData.usage_limit_per_customer}
							min="1"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>
			</div>

			<!-- Form Actions -->
			<div class="flex justify-end gap-4 pt-6">
				<button
					type="button"
					on:click={() => goto(`/promotions/${id}`)}
					class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
				>
					Cancel
				</button>
				<button
					type="submit"
					disabled={loading}
					class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
				>
					{#if loading}
						<div class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
					{/if}
					Update Promotion
				</button>
			</div>
		</form>
	{/if}
</div>
