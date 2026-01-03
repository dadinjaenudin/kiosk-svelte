<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { getProductsForSelector } from '$lib/api/promotions';

	export let tenantId = null;
	export let selected = [];

	const dispatch = createEventDispatcher();

	let products = [];
	let loading = false;
	let searchQuery = '';
	let showDropdown = false;
	let selectedProducts = [...selected];

	$: selectedIds = selectedProducts.map((p) => p.id);

	// Load products when tenantId changes
	$: if (tenantId) {
		console.log('🔄 TenantId changed to:', tenantId);
		loadProducts();
	}

	onMount(() => {
		console.log('🎬 ProductSelector mounted with tenantId:', tenantId);
		if (tenantId) {
			loadProducts();
		}
	});

	async function loadProducts() {
		if (!tenantId) {
			console.log('⚠️ No tenantId, skipping load');
			products = [];
			return;
		}

		try {
			loading = true;
			console.log('📦 Loading products for tenant:', tenantId);
			const filters = {
				is_available: true,
				tenant: tenantId
			};

			if (searchQuery) {
				filters.search = searchQuery;
			}

			const data = await getProductsForSelector(filters);
			products = data.results || data;
			console.log('✅ Loaded products:', products.length, products);
		} catch (err) {
			console.error('❌ Error loading products:', err);
			products = [];
		} finally {
			loading = false;
		}
	}

	function handleSearch() {
		loadProducts();
	}

	function toggleProduct(product) {
		const index = selectedProducts.findIndex((p) => p.id === product.id);

		if (index > -1) {
			selectedProducts = selectedProducts.filter((p) => p.id !== product.id);
		} else {
			selectedProducts = [...selectedProducts, product];
		}

		dispatch('change', selectedProducts);
	}

	function removeProduct(product) {
		selectedProducts = selectedProducts.filter((p) => p.id !== product.id);
		dispatch('change', selectedProducts);
	}

	function formatCurrency(amount) {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
</script>

<div class="space-y-4">
	<!-- Debug Info -->
	{#if !tenantId}
		<div class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
			⚠️ Please select a tenant first to see available products
		</div>
	{/if}

	<!-- Search Input -->
	<div class="relative">
		<input
			type="text"
			bind:value={searchQuery}
			on:input={handleSearch}
			on:focus={() => (showDropdown = true)}
			placeholder="Search products by name..."
			class="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
		/>
		<svg
			class="absolute left-3 top-2.5 w-5 h-5 text-gray-400"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
			/>
		</svg>

		<!-- Dropdown -->
		{#if showDropdown}
			<div
				class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
			>
				{#if loading}
					<div class="p-4 text-center text-gray-500">Loading...</div>
				{:else if !tenantId}
					<div class="p-4 text-center text-gray-500">Please select a tenant first</div>
				{:else if products.length === 0}
					<div class="p-4 text-center text-gray-500">No products found</div>
				{:else}
					{#each products as product}
						<button
							type="button"
							on:click={() => toggleProduct(product)}
							class="w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 text-left transition-colors {selectedIds.includes(
								product.id
							)
								? 'bg-blue-50'
								: ''}"
						>
							<!-- Checkbox -->
							<input
								type="checkbox"
								checked={selectedIds.includes(product.id)}
								class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
								on:click|stopPropagation
							/>

							<!-- Product Image -->
							{#if product.image}
								<img
									src={product.image}
									alt={product.name}
									class="w-12 h-12 object-cover rounded"
								/>
							{:else}
								<div
									class="w-12 h-12 bg-gray-200 rounded flex items-center justify-center text-gray-400"
								>
									<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
										/>
									</svg>
								</div>
							{/if}

							<!-- Product Info -->
							<div class="flex-1">
								<div class="font-medium text-gray-900">{product.name}</div>
								<div class="text-sm text-gray-500">{formatCurrency(product.price)}</div>
								{#if product.tenant_name}
									<div class="text-xs text-gray-400">{product.tenant_name}</div>
								{/if}
							</div>

							<!-- Check Icon -->
							{#if selectedIds.includes(product.id)}
								<svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
										clip-rule="evenodd"
									/>
								</svg>
							{/if}
						</button>
					{/each}
				{/if}
			</div>
		{/if}
	</div>

	<!-- Selected Products -->
	{#if selectedProducts.length > 0}
		<div class="space-y-2">
			<div class="flex items-center justify-between">
				<h3 class="text-sm font-medium text-gray-700">
					Selected Products ({selectedProducts.length})
				</h3>
				<button
					type="button"
					on:click={() => {
						selectedProducts = [];
						dispatch('change', selectedProducts);
					}}
					class="text-sm text-red-600 hover:text-red-700"
				>
					Clear All
				</button>
			</div>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
				{#each selectedProducts as product}
					<div
						class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
					>
						{#if product.image}
							<img
								src={product.image}
								alt={product.name}
								class="w-12 h-12 object-cover rounded"
							/>
						{:else}
							<div
								class="w-12 h-12 bg-gray-300 rounded flex items-center justify-center text-gray-500"
							>
								<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
									/>
								</svg>
							</div>
						{/if}
						<div class="flex-1">
							<div class="font-medium text-sm text-gray-900">{product.name}</div>
							<div class="text-sm text-gray-600">{formatCurrency(product.price)}</div>
						</div>
						<button
							type="button"
							on:click={() => removeProduct(product)}
							class="text-gray-400 hover:text-red-600 transition-colors"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<!-- Click outside to close dropdown -->
<svelte:window
	on:click={(e) => {
		if (!e.target.closest('.relative')) {
			showDropdown = false;
		}
	}}
/>
