<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { kioskConfig, multiCart } from '$lib/stores/kioskStore';
	import { Search, Filter, ShoppingCart, X, Plus, Minus } from 'lucide-svelte';
	import { networkStatus } from '$lib/services/networkService';
	import { browser } from '$app/environment';
	import ConnectionStatus from '$lib/components/ConnectionStatus.svelte';
	
	interface Product {
		id: number;
		name: string;
		description: string;
		price: number;
		image: string;
		outlet_id: number;
		outlet_name: string;
		brand_name: string;
		tenant_name: string;
		tenant_color: string;
		category_name: string;
		is_available: boolean;
		is_featured: boolean;
		is_popular: boolean;
	}
	
	interface Brand {
		id: number;
		name: string;
		color: string;
		selected: boolean;
	}
	
	let products: Product[] = [];
	let filteredProducts: Product[] = [];
	let brands: Brand[] = [];
	let loading = true;
	let error = '';
	let offlineWarning = '';
	let searchQuery = '';
	let showFilters = false;
	let selectedCategory = '';
	let categories: string[] = [];
	let hasCheckedConfig = false;
	
	// Get store config
	$: storeCode = $kioskConfig.storeCode;
	$: isConfigured = $kioskConfig.isConfigured;
	$: cartItemsCount = Object.values($multiCart.carts).reduce((sum, cart) => 
		sum + cart.items.reduce((itemSum, item) => itemSum + item.quantity, 0), 0
	);
	
	onMount(async () => {
		// Only check once to prevent loop
		if (hasCheckedConfig) return;
		hasCheckedConfig = true;
		
		console.log('🛒 Products page mounted');
		console.log('📍 Store Code:', storeCode);
		console.log('✅ Is Configured:', isConfigured);
		
		if (!isConfigured || !storeCode) {
			console.warn('⚠️ Not configured, redirecting to setup...');
			goto('/kiosk');
			return;
		}
		
		await loadProducts();
	});
	
	async function loadProducts() {
		loading = true;
		error = '';
		offlineWarning = '';
		
		console.log('🔄 Loading products...');
		console.log('📍 Store Code:', storeCode);
		console.log('🌐 Network Status:', $networkStatus.isOnline ? 'Online' : 'Offline');
		console.log('🖥️ Browser:', browser);
		
		try {
			// Check if offline
			if (!$networkStatus.isOnline) {
				console.log('📴 Offline mode: Loading products from cache...');
				
				// Try to load from localStorage cache
				if (browser) {
					const cacheKey = `products_${storeCode}`;
					console.log('🔑 Cache key:', cacheKey);
					
					const cached = localStorage.getItem(cacheKey);
					console.log('💾 Cache found:', cached ? 'YES' : 'NO');
					
					if (cached) {
						const data = JSON.parse(cached);
						products = data.products || [];
						console.log('📦 Loaded products from cache:', products.length);
						
						// Extract brands and categories
						const brandMap = new Map<number, Brand>();
						products.forEach(p => {
							if (!brandMap.has(p.outlet_id)) {
								brandMap.set(p.outlet_id, {
									id: p.outlet_id,
									name: p.brand_name,
									color: p.tenant_color || '#3498db',
									selected: true
								});
							}
						});
						brands = Array.from(brandMap.values());
						
						const categorySet = new Set(products.map(p => p.category_name).filter(Boolean));
						categories = ['All', ...Array.from(categorySet)];
						selectedCategory = 'All';
						
						applyFilters();
						
						// Show offline warning (not error!)
						offlineWarning = '📴 Mode Offline: Menampilkan produk dari cache';
						console.log('✅ Loaded', products.length, 'products from cache');
						loading = false;
						return;
					} else {
						console.log('❌ No cache found for key:', cacheKey);
						throw new Error('Tidak ada data produk tersimpan. Harap hubungkan internet dan refresh halaman.');
					}
				} else {
					console.log('❌ Not in browser environment');
				}
			}
			
			// ONLINE MODE: Fetch from backend
			console.log('🌐 Online mode: Fetching from backend...');
			const response = await fetch(
				`/api/public/stores/${storeCode}/products/`
			);
			
			if (!response.ok) {
				throw new Error('Failed to load products');
			}
			
			const data = await response.json();
			products = data.products || [];
			console.log('📦 Fetched products:', products.length);
			
			// Cache products for offline use
			if (browser && products.length > 0) {
				const cacheKey = `products_${storeCode}`;
				localStorage.setItem(cacheKey, JSON.stringify(data));
				console.log('💾 Cached', products.length, 'products with key:', cacheKey);
				
				// Verify cache was saved
				const verify = localStorage.getItem(cacheKey);
				console.log('✅ Cache verification:', verify ? 'SUCCESS' : 'FAILED');
			}
			
			// Extract unique brands
			const brandMap = new Map<number, Brand>();
			products.forEach(p => {
				if (!brandMap.has(p.outlet_id)) {
					brandMap.set(p.outlet_id, {
						id: p.outlet_id,
						name: p.brand_name,
						color: p.tenant_color || '#3498db',
						selected: true // All brands selected by default
					});
				}
			});
			brands = Array.from(brandMap.values());
			
			// Extract unique categories
			const categorySet = new Set(products.map(p => p.category_name).filter(Boolean));
			categories = ['All', ...Array.from(categorySet)];
			selectedCategory = 'All';
			
			applyFilters();
		} catch (err) {
			console.error('Error loading products:', err);
			error = err instanceof Error ? err.message : 'Failed to load products. Please try again.';
			products = [];
			filteredProducts = [];
		} finally {
			loading = false;
		}
	}
	
	function applyFilters() {
		filteredProducts = products.filter(product => {
			// Brand filter
			const brandSelected = brands.find(b => b.id === product.outlet_id)?.selected ?? true;
			if (!brandSelected) return false;
			
			// Category filter
			if (selectedCategory !== 'All' && product.category_name !== selectedCategory) {
				return false;
			}
			
			// Search filter
			if (searchQuery && !product.name.toLowerCase().includes(searchQuery.toLowerCase())) {
				return false;
			}
			
			return true;
		});
	}
	
	function toggleBrandFilter(brandId: number) {
		brands = brands.map(b => 
			b.id === brandId ? { ...b, selected: !b.selected } : b
		);
		applyFilters();
	}
	
	function selectAllBrands() {
		brands = brands.map(b => ({ ...b, selected: true }));
		applyFilters();
	}
	
	function clearBrandFilters() {
		brands = brands.map(b => ({ ...b, selected: false }));
		applyFilters();
	}
	
	function handleSearch() {
		applyFilters();
	}
	
	function addToCart(product: Product) {
		multiCart.addItem(
			product.outlet_id,
			product.outlet_name,
			product.tenant_name,
			product.tenant_color,
			0.11, // taxRate 11%
			0.05, // serviceChargeRate 5%
			{
				id: product.id,
				name: product.name,
				sku: product.id.toString(),
				price: product.price,
				image: product.image
			},
			1, // quantity
			[], // modifiers
			'' // notes
		);
	}
	
	function goToCart() {
		goto('/kiosk/cart');
	}
</script>

<svelte:head>
	<title>Browse Products - {$kioskConfig.storeName || 'Kiosk'}</title>
</svelte:head>

<!-- Connection Status Widget -->
<ConnectionStatus position="top-right" />

<div class="products-page-wrapper">
	<!-- Header -->
	<header class="bg-white shadow-sm sticky top-0 z-10">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-2xl font-bold text-gray-900">Browse Menu</h1>
					<p class="text-sm text-gray-600">{$kioskConfig.storeName}</p>
				</div>
				
				<button
					on:click={goToCart}
					class="relative bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
				>
					<ShoppingCart class="inline w-5 h-5 mr-2" />
					Cart
					{#if cartItemsCount > 0}
						<span class="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
							{cartItemsCount}
						</span>
					{/if}
				</button>
			</div>
		</div>
	</header>
	
	<!-- Search & Filters -->
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
		<div class="bg-white rounded-lg shadow p-4 space-y-4">
			<!-- Search Bar -->
			<div class="flex gap-3">
				<div class="flex-1 relative">
					<Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
					<input
						type="text"
						bind:value={searchQuery}
						on:input={handleSearch}
						placeholder="Search products..."
						class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					/>
				</div>
				
				<button
					on:click={() => showFilters = !showFilters}
					class="bg-gray-100 hover:bg-gray-200 px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
				>
					<Filter class="w-5 h-5" />
					Filters
				</button>
			</div>
			
			<!-- Filters Panel -->
			{#if showFilters}
				<div class="border-t pt-4 space-y-4">
					<!-- Brand Filters -->
					<div>
						<div class="flex items-center justify-between mb-3">
							<h3 class="font-semibold text-gray-900">Brands</h3>
							<div class="flex gap-2">
								<button
									on:click={selectAllBrands}
									class="text-sm text-blue-600 hover:text-blue-700"
								>
									Select All
								</button>
								<span class="text-gray-300">|</span>
								<button
									on:click={clearBrandFilters}
									class="text-sm text-gray-600 hover:text-gray-700"
								>
									Clear
								</button>
							</div>
						</div>
						
						<div class="flex flex-wrap gap-2">
							{#each brands as brand}
								<button
									on:click={() => toggleBrandFilter(brand.id)}
									class="px-4 py-2 rounded-full font-medium transition-all"
									class:bg-blue-600={brand.selected}
									class:text-white={brand.selected}
									class:bg-gray-100={!brand.selected}
									class:text-gray-700={!brand.selected}
									style={brand.selected ? `background-color: ${brand.color}` : ''}
								>
									{brand.name}
								</button>
							{/each}
						</div>
					</div>
					
					<!-- Category Filter -->
					<div>
						<h3 class="font-semibold text-gray-900 mb-3">Category</h3>
						<div class="flex flex-wrap gap-2">
							{#each categories as category}
								<button
									on:click={() => { selectedCategory = category; applyFilters(); }}
									class="px-4 py-2 rounded-full font-medium transition-colors"
									class:bg-blue-600={selectedCategory === category}
									class:text-white={selectedCategory === category}
									class:bg-gray-100={selectedCategory !== category}
									class:text-gray-700={selectedCategory !== category}
								>
									{category}
								</button>
							{/each}
						</div>
					</div>
				</div>
			{/if}
		</div>
	</div>
	
	<!-- Products Grid -->
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
		<!-- Offline Warning Banner -->
		{#if offlineWarning}
			<div class="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center">
						<svg class="w-5 h-5 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<span class="text-yellow-800 font-medium">{offlineWarning}</span>
					</div>
					<button
						on:click={loadProducts}
						class="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
					>
						Retry
					</button>
				</div>
			</div>
		{/if}
		
		{#if loading}
			<div class="flex justify-center items-center py-20">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			</div>
		{:else if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
				<p class="text-red-800 font-medium">{error}</p>
				<button
					on:click={loadProducts}
					class="mt-4 bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
				>
					Retry
				</button>
			</div>
		{:else if filteredProducts.length === 0}
			<div class="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
				<p class="text-gray-600 text-lg">No products found</p>
				<p class="text-gray-500 text-sm mt-2">Try adjusting your filters or search query</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
				{#each filteredProducts as product}
					<div class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow overflow-hidden">
						<!-- Product Image -->
						<div class="relative aspect-video bg-gray-200">
							{#if product.image}
								<img
									src={product.image}
									alt={product.name}
									class="w-full h-full object-cover"
								/>
							{:else}
								<div class="w-full h-full flex items-center justify-center text-gray-400">
									<span class="text-4xl">🍽️</span>
								</div>
							{/if}
							
							<!-- Brand Badge -->
							<div 
								class="absolute top-2 right-2 px-3 py-1 rounded-full text-xs font-bold text-white shadow"
								style="background-color: {product.tenant_color || '#3498db'}"
							>
								{product.brand_name}
							</div>
							
							<!-- Featured/Popular Badges -->
							<div class="absolute top-2 left-2 flex gap-1">
								{#if product.is_featured}
									<span class="bg-yellow-500 text-white text-xs px-2 py-1 rounded-full font-bold">
										⭐ Featured
									</span>
								{/if}
								{#if product.is_popular}
									<span class="bg-orange-500 text-white text-xs px-2 py-1 rounded-full font-bold">
										🔥 Popular
									</span>
								{/if}
							</div>
						</div>
						
						<!-- Product Info -->
						<div class="p-4">
							<h3 class="font-bold text-lg text-gray-900 mb-1">{product.name}</h3>
							<p class="text-sm text-gray-600 mb-2">{product.category_name}</p>
							{#if product.description}
								<p class="text-sm text-gray-500 mb-3 line-clamp-2">{product.description}</p>
							{/if}
							
							<div class="flex items-center justify-between">
								<span class="text-2xl font-bold text-blue-600">
									Rp {product.price.toLocaleString('id-ID')}
								</span>
								
								<button
									on:click={() => addToCart(product)}
									class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
								>
									<Plus class="w-4 h-4" />
									Add
								</button>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.products-page-wrapper {
		min-height: 100vh;
		background-color: #f9fafb;
		overflow-y: auto;
	}

	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
