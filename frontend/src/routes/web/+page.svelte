<script>
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';
	import { cartItems, cartTotals, loadCart, addProductToCart, updateQuantity, removeCartItem, clearAllCart } from '$stores/cart.js';
	import { getProducts, getCategories } from '$db/index.js';
	import { browser } from '$app/environment';
	import { db, addToSyncQueue, saveOrder } from '$db/index.js';
	import { isOnline, startSync } from '$stores/offline.js';
	import { broadcastNewOrder, syncServerConnected } from '$lib/stores/localSync.js';
	import PaymentModal from '$lib/components/PaymentModal.svelte';
	import SuccessModal from '$lib/components/SuccessModal.svelte';
	import ModifierModal from '$lib/components/ModifierModal.svelte';
	
	export let data = undefined;
	
	let products = [];
	let categories = [];
	let tenants = [];
	let selectedCategory = null;
	let selectedTenant = null;
	let showCart = false;
	let showPaymentModal = false;
	let showSuccessModal = false;
	let showModifierModal = false;
	let showClearConfirm = false;
	let selectedProduct = null;
	let checkoutResult = null;
	let loading = true;
	let searchQuery = '';
	let showAvailable = true;
	
	// Web-specific: Delivery options
	let orderType = 'delivery'; // 'delivery' or 'pickup'
	
	$: filteredProducts = products.filter(p => {
		// Debug first product
		if (products.length > 0 && products[0] === p) {
			console.log('🔍 First product structure:', {
				id: p.id,
				name: p.name,
				category: p.category,
				category_id: p.category_id,
				tenant_id: p.tenant_id
			});
			console.log('🎯 Selected filters:', {
				selectedCategory,
				selectedTenant,
				showAvailable,
				searchQuery
			});
		}
		
		if (selectedTenant && p.tenant_id !== selectedTenant) return false;
		if (selectedCategory && p.category !== selectedCategory) return false;
		if (showAvailable && !p.is_available) return false;
		if (searchQuery && !p.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
		return true;
	});
	
	$: totalItems = $cartItems.reduce((sum, item) => sum + item.quantity, 0);
	
	// Group cart items by tenant
	$: groupedCartItems = Object.values(
		$cartItems.reduce((groups, item) => {
			const tenantId = item.tenant_id || 'unknown';
			if (!groups[tenantId]) {
				groups[tenantId] = {
					tenant_id: tenantId,
					tenant_name: item.tenant_name || 'Unknown',
					tenant_color: item.tenant_color || '#666',
					items: [],
					total: 0
				};
			}
			
			let parsedItem = { ...item };
			if (typeof item.modifiers === 'string') {
				try {
					parsedItem.modifiers = JSON.parse(item.modifiers);
				} catch (e) {
					parsedItem.modifiers = [];
				}
			}
			
			// Ensure modifiers is always an array
			if (!Array.isArray(parsedItem.modifiers)) {
				parsedItem.modifiers = [];
			}
			
			// Calculate item total including modifiers
			const modifiersTotal = parsedItem.modifiers.reduce((sum, mod) => {
				return sum + (parseFloat(mod.price_adjustment) || 0);
			}, 0);
			const itemTotal = (parseFloat(item.product_price) + modifiersTotal) * item.quantity;
			
			groups[tenantId].items.push(parsedItem);
			groups[tenantId].total += itemTotal;
			return groups;
		}, {})
	);
	
	$: grandTotal = groupedCartItems.reduce((sum, group) => sum + group.total, 0);
	
	onMount(async () => {
		if (browser) {
			await loadCart();
			await loadProducts();
			startSync();
			loading = false;
		}
	});
	
	async function loadProducts() {
		try {
		// 1. Load from cache first for instant display
		products = await getProducts();
		categories = await getCategories();
		
		console.log('📦 Loaded from cache:', products.length, 'products');
		
		// 2. If online, sync with server
		if ($isOnline) {
			console.log('🌐 Online - syncing with server...');
			try {
				const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:8001/api';
				
				// Fetch products from backend
				const productsRes = await fetch(`${apiUrl}/products/`);
				if (productsRes.ok) {
					const productsData = await productsRes.json();
					const freshProducts = productsData.results || productsData || [];
					
					if (freshProducts.length > 0) {
						// Update IndexedDB cache
						await db.products.clear();
						await db.products.bulkAdd(freshProducts);
						
						// Update UI
						products = freshProducts;
						console.log('✅ Synced:', freshProducts.length, 'products from server');
						console.log('🔍 Sample product after sync:', freshProducts[0]);
					}
				}
				
				// Fetch categories from backend
				const categoriesRes = await fetch(`${apiUrl}/categories/`);
				if (categoriesRes.ok) {
					const categoriesData = await categoriesRes.json();
					const freshCategories = categoriesData.results || categoriesData || [];
					
					if (freshCategories.length > 0) {
						await db.categories.clear();
						await db.categories.bulkAdd(freshCategories);
						categories = freshCategories;
						console.log('✅ Synced:', freshCategories.length, 'categories from server');
					}
				}
			} catch (error) {
				console.warn('⚠️ Server sync failed, using cached data:', error.message);
			}
	}
	
	const uniqueTenants = [...new Set(products.map(p => p.tenant_id))];
	tenants = uniqueTenants.map(id => {
		const product = products.find(p => p.tenant_id === id);
		return {
			id,
			name: product?.tenant_name || 'Unknown',
			color: product?.tenant_color || '#6366f1'
		};
	});
} catch (error) {
	console.error('Error loading products:', error);
}
}

function getImageUrl(imagePath) {
	if (!imagePath) {
		console.log('⚠️ No image path provided');
		return null;
	}
	
	// If already full URL, return as is
	if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
		console.log('✅ Image full URL:', imagePath);
		return imagePath;
	}
	
	// Construct full URL from backend
	const backendUrl = import.meta.env.PUBLIC_API_URL?.replace('/api', '') || 'http://localhost:8001';
	
	// Handle different path formats
	const fullUrl = imagePath.startsWith('/') 
		? `${backendUrl}${imagePath}`
		: `${backendUrl}/${imagePath}`;
	
	console.log('🖼️ Image URL constructed:', { imagePath, backendUrl, fullUrl });
	return fullUrl;
}

async function handleAddToCart(event) {
	const { product, quantity, modifiers, notes } = event.detail;
	
	try {
		const productWithTenant = {
			...product,
			tenant_id: product.tenant_id,
			tenant_name: product.tenant_name,
			tenant_color: product.tenant_color
		};
		
		await addProductToCart(productWithTenant, quantity, modifiers, notes);
		showModifierModal = false;
		selectedProduct = null; // Reset to close modal
	} catch (error) {
		console.error('Error adding to cart:', error);
	}
}

function selectProduct(product) {
	if (!product.is_available) {
		alert('This product is currently unavailable');
		return;
	}
	selectedProduct = product;
	showModifierModal = true;
}

function clearCart() {
	showClearConfirm = true;
}

async function confirmClearCart() {
	try {
		await clearAllCart();
		showClearConfirm = false;
		console.log('🗑️ Cart cleared');
	} catch (error) {
		console.error('Error clearing cart:', error);
	}
}

function handleCheckout() {
	if (totalItems === 0) return;
	showPaymentModal = true;
}

function handleSuccessClose() {
	// Immediately hide modal
	showSuccessModal = false;
	
	// Reset state after a short delay to allow modal to close smoothly
	setTimeout(() => {
		checkoutResult = null;
		
		// Reset filters to show all products
		selectedCategory = null;
		selectedTenant = null;
		searchQuery = '';
		
		// Scroll to top
		if (browser) {
			window.scrollTo({ top: 0, behavior: 'smooth' });
		}
	}, 100);
}

async function processCheckout(event) {
	const { paymentMethod, customerName: custName, customerPhone: custPhone, tableNumber: tblNum, notes } = event.detail;
	
	try {
		const checkoutData = {
			items: $cartItems.map(item => ({
				product_id: item.product_id,
				quantity: item.quantity,
				modifiers: typeof item.modifiers === 'string' 
					? JSON.parse(item.modifiers || '[]')
					: (item.modifiers || []),
				notes: item.notes || ''
			})),
			payment_method: paymentMethod,
			customer_name: custName,
			customer_phone: custPhone,
			table_number: tblNum,
			notes: notes
		};
		
		let result;
		
		if ($isOnline) {
			try {
				const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:8001/api';
				const response = await fetch(`${apiUrl}/orders/checkout/`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(checkoutData)
				});
				
				if (!response.ok) {
					const error = await response.json();
					throw new Error(error.error || error.detail || 'Checkout failed');
				}
				
				result = await response.json();
				
				if (result.orders && Array.isArray(result.orders)) {
					result.orders.forEach(order => broadcastNewOrder(order));
				}
			} catch (fetchError) {
				console.warn('Online checkout failed, using offline:', fetchError.message);
				alert('Checkout will be saved offline');
				return;
			}
		} else {
			alert('Offline mode not yet implemented for web ordering');
			return;
		}
		
		await clearAllCart();
		
		checkoutResult = result;
		showPaymentModal = false;
		showCart = false; // Close cart sidebar
		showSuccessModal = true;
		
	} catch (error) {
		console.error('Checkout error:', error);
		alert(`Checkout gagal: ${error.message}`);
	}
}
</script>

<svelte:head>
	<title>Online Order - Food Court</title>
</svelte:head>

{#if loading}
	<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-500 to-teal-600">
		<div class="text-center text-white">
			<div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white mx-auto mb-4"></div>
			<p class="text-xl font-semibold">Loading Online Ordering...</p>
		</div>
	</div>
{:else}
	<div class="web-ordering min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
		
		<!-- Header - Web Modern Style (Emerald/Teal Theme) -->
		<header class="web-header sticky top-0 z-40 bg-white shadow-md">
			<div class="container mx-auto px-4 py-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
							<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
							</svg>
						</div>
						<div>
							<h1 class="text-xl font-bold text-gray-800">🌐 Online Order</h1>
							<p class="text-xs text-gray-500">Food Court Yogyakarta</p>
						</div>
					</div>
					
					<button on:click={() => showCart = !showCart} class="cart-button-web">
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
						</svg>
						{#if totalItems > 0}
							<span class="badge-web">{totalItems}</span>
						{/if}
					</button>
				</div>
				
				<!-- Delivery Type Selector - WEB UNIQUE FEATURE -->
				<div class="mt-4 flex gap-2">
					<button 
						class="delivery-option {orderType === 'delivery' ? 'active' : ''}"
						on:click={() => orderType = 'delivery'}
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0" />
						</svg>
						🚚 Delivery
					</button>
					<button 
						class="delivery-option {orderType === 'pickup' ? 'active' : ''}"
						on:click={() => orderType = 'pickup'}
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
						</svg>
						🏪 Pickup
					</button>
				</div>
				
				<!-- Search -->
				<div class="mt-4">
					<input 
						type="search" 
						bind:value={searchQuery}
						placeholder="🔍 Search menu..."
						class="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-emerald-500 focus:outline-none"
					/>
				</div>
			</div>
		</header>
		
		<!-- Main Content -->
		<main class="container mx-auto px-4 py-6 pb-32">
			
			<!-- Tenant Filters -->
			{#if tenants.length > 0}
				<div class="mb-4">
					<h3 class="text-sm font-semibold text-gray-600 mb-2">🏪 Filter by Tenant</h3>
					<div class="flex gap-2 overflow-x-auto pb-2">
						<button 
							class="tenant-chip {!selectedTenant ? 'active' : ''}"
							on:click={() => selectedTenant = null}
						>
							All Tenants
						</button>
						{#each tenants as tenant}
							<button 
								class="tenant-chip {selectedTenant === tenant.id ? 'active' : ''}"
								style="--tenant-color: {tenant.color}"
								on:click={() => selectedTenant = tenant.id}
							>
								{tenant.name}
							</button>
						{/each}
					</div>
				</div>
			{/if}
			
			<!-- Category Filters -->
			{#if categories.length > 0}
				<div class="mb-6">
					<h3 class="text-sm font-semibold text-gray-600 mb-2">📂 Filter by Category</h3>
					<div class="flex gap-2 overflow-x-auto pb-2">
						<button 
							class="category-chip {!selectedCategory ? 'active' : ''}"
							on:click={() => selectedCategory = null}
						>
							All Menu
						</button>
						{#each categories as category}
							<button 
								class="category-chip {selectedCategory === category.id ? 'active' : ''}"
								on:click={() => selectedCategory = category.id}
							>
								{category.name}
							</button>
						{/each}
					</div>
				</div>
			{/if}
			
			<!-- Products Grid - More spacious web layout -->
			<div class="mb-4">
				<p class="text-sm text-gray-600">
					{#if filteredProducts.length === 0}
						❌ No products found
					{:else}
						✅ Showing {filteredProducts.length} {filteredProducts.length === 1 ? 'product' : 'products'}
					{/if}
				</p>
			</div>
			
			<div class="products-grid-web">
				{#each filteredProducts as product}
					<div class="product-card-web" on:click={() => selectProduct(product)}>
					{#if getImageUrl(product.image)}
						<img 
							src={getImageUrl(product.image)} 
							alt={product.name} 
							class="product-image-web" 
							on:error={(e) => {
								console.error('❌ Image failed to load:', getImageUrl(product.image));
								e.target.style.display = 'none';
								e.target.nextElementSibling.style.display = 'flex';
							}}
						/>
						<div class="product-image-placeholder-web" style="display: none;">
							<svg class="w-16 h-16 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
							</svg>
						</div>
					{:else}
						<div class="product-image-placeholder-web">
							<svg class="w-16 h-16 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
						</svg>
					</div>
				{/if}
				
				<div class="p-4">
							<div class="flex items-start justify-between mb-2">
								<h3 class="font-semibold text-gray-800 flex-1">{product.name}</h3>
								{#if !product.is_available}
									<span class="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">Unavailable</span>
								{/if}
							</div>
							
							<p class="text-sm text-gray-500 mb-3 line-clamp-2">{product.description || 'Delicious food'}</p>
							
							<div class="flex items-center justify-between">
								<span class="text-lg font-bold text-emerald-600">
									Rp {product.price.toLocaleString('id-ID')}
								</span>
								<span class="tenant-badge-web" style="background-color: {product.tenant_color}20; color: {product.tenant_color}">
									{product.tenant_name}
								</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
			
		</main>
		
		<!-- Floating Checkout Button -->
		{#if totalItems > 0}
			<div class="fixed bottom-0 left-0 right-0 p-4 bg-white shadow-lg border-t-2 border-emerald-500 z-30">
				<button on:click={handleCheckout} class="checkout-button-web w-full">
					<div class="flex items-center justify-between">
						<span class="font-bold">🛒 {totalItems} Items</span>
						<span class="font-bold">Checkout - Rp {$cartTotals.total.toLocaleString('id-ID')}</span>
					</div>
				</button>
			</div>
		{/if}
		
		<!-- Cart Sidebar -->
		{#if showCart}
			<div class="cart-overlay-web" on:click={() => showCart = false}>
				<div class="cart-sidebar-web" on:click|stopPropagation>
					<div class="cart-header-web">
						<h2 class="text-xl font-bold">🛒 Your Order</h2>
						<div class="flex gap-2">
							{#if $cartItems.length > 0}
								<button on:click={clearCart} class="text-red-500 hover:text-red-700" title="Clear cart">
									<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
									</svg>
								</button>
							{/if}
							<button on:click={() => showCart = false} class="text-gray-500 hover:text-gray-700">
								<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</div>
					</div>
					
					<div class="cart-body-web">
						{#if $cartItems.length === 0}
							<div class="text-center py-12 text-gray-400">
								<svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
								<p>Your cart is empty</p>
							</div>
						{:else}
							{#each $cartItems as item}
								<div class="cart-item-web">
									<div class="flex-1">
								<h4 class="font-semibold text-gray-800">{item.product_name}</h4>
								<p class="text-sm text-gray-500">{item.tenant_name}</p>
								<p class="text-emerald-600 font-semibold">Rp {item.product_price?.toLocaleString('id-ID')}</p>
									</div>
									<div class="flex items-center gap-2">
										<button on:click={() => updateQuantity(item.id, item.quantity - 1)} class="qty-btn-web">-</button>
										<span class="font-semibold">{item.quantity}</span>
										<button on:click={() => updateQuantity(item.id, item.quantity + 1)} class="qty-btn-web">+</button>
										<button on:click={() => removeCartItem(item.id)} class="text-red-500 hover:text-red-700 ml-2">
											<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
											</svg>
										</button>
									</div>
								</div>
							{/each}
						{/if}
					</div>
					
					{#if $cartItems.length > 0}
						<div class="cart-footer-web">
							<div class="text-lg font-bold flex justify-between mb-4">
								<span>Total</span>
								<span class="text-emerald-600">Rp {$cartTotals.total.toLocaleString('id-ID')}</span>
							</div>
							<button on:click={handleCheckout} class="checkout-button-web w-full">
								Proceed to Checkout →
							</button>
						</div>
					{/if}
				</div>
			</div>
		{/if}
		
	</div>
{/if}

<ModifierModal 
	bind:show={showModifierModal} 
	bind:product={selectedProduct} 
	on:addToCart={handleAddToCart}
	on:close={() => selectedProduct = null}
/>

{#if showPaymentModal}
	<PaymentModal 
		groupedCartItems={groupedCartItems}
		grandTotal={grandTotal}
		on:checkout={processCheckout}
		on:cancel={() => showPaymentModal = false}
	/>
{/if}

{#if showSuccessModal && checkoutResult}
	<SuccessModal 
		orders={checkoutResult.orders}
		payments={checkoutResult.payments}
		totalAmount={parseFloat(checkoutResult.total_amount)}
		paymentMethod={checkoutResult.payment_method}
		offline={checkoutResult.offline || false}
		on:close={handleSuccessClose}
	/>
{/if}

<!-- Clear Cart Confirmation Modal -->
{#if showClearConfirm}
	<div class="modal-overlay" on:click={() => showClearConfirm = false}>
		<div class="modal-content-clear" on:click|stopPropagation>
			<div class="modal-icon-danger">
				<svg class="w-16 h-16 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
				</svg>
			</div>
			<h3 class="text-2xl font-bold text-gray-800 mb-2">Clear Cart?</h3>
			<p class="text-gray-600 mb-6">Are you sure you want to remove all <span class="font-bold text-emerald-600">{$cartItems.length} items</span> from your cart? This action cannot be undone.</p>
			<div class="flex gap-3">
				<button 
					on:click={() => showClearConfirm = false}
					class="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-all"
				>
					Cancel
				</button>
				<button 
					on:click={confirmClearCart}
					class="flex-1 px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-semibold hover:from-red-600 hover:to-red-700 transition-all shadow-lg"
				>
					Clear All
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	/* 🌐 WEB MODERN THEME - Emerald/Teal (Customer-Facing) */
	:global(body) {
		overflow-y: auto !important;
		min-height: 100vh;
	}
	
	.web-ordering {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
		overflow-y: auto;
	}
	
	.web-header {
		backdrop-filter: blur(10px);
	}
	
	.cart-button-web {
		position: relative;
		padding: 0.75rem;
		background: linear-gradient(135deg, #10b981, #14b8a6);
		border-radius: 1rem;
		color: white;
		transition: transform 0.2s;
		box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
	}
	
	.cart-button-web:hover {
		transform: scale(1.05);
	}
	
	.badge-web {
		position: absolute;
		top: -8px;
		right: -8px;
		background: #ef4444;
		color: white;
		border-radius: 9999px;
		padding: 0.125rem 0.5rem;
		font-size: 0.75rem;
		font-weight: bold;
		box-shadow: 0 2px 4px rgba(0,0,0,0.2);
	}
	
	.delivery-option {
		flex: 1;
		padding: 0.75rem 1rem;
		border-radius: 0.75rem;
		border: 2px solid #e5e7eb;
		background: white;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		font-weight: 600;
		color: #6b7280;
		transition: all 0.2s;
	}
	
	.delivery-option.active {
		background: linear-gradient(135deg, #10b981, #14b8a6);
		border-color: #10b981;
		color: white;
		box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
	}
	
	.category-chip {
		padding: 0.5rem 1.25rem;
		border-radius: 9999px;
		background: white;
		border: 2px solid #e5e7eb;
		font-weight: 600;
		color: #6b7280;
		white-space: nowrap;
		transition: all 0.2s;
		box-shadow: 0 1px 2px rgba(0,0,0,0.05);
	}
	
	.category-chip.active {
		background: linear-gradient(135deg, #10b981, #14b8a6);
		border-color: #10b981;
		color: white;
		box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
	}
	
	.tenant-chip {
		padding: 0.5rem 1.25rem;
		border-radius: 9999px;
		background: white;
		border: 2px solid #e5e7eb;
		font-weight: 600;
		color: #6b7280;
		white-space: nowrap;
		transition: all 0.2s;
		box-shadow: 0 1px 2px rgba(0,0,0,0.05);
		cursor: pointer;
	}
	
	.tenant-chip:hover {
		border-color: #10b981;
		transform: translateY(-1px);
	}
	
	.tenant-chip.active {
		background: var(--tenant-color, #10b981);
		border-color: var(--tenant-color, #10b981);
		color: white;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
	}
	
	.products-grid-web {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 1.5rem;
		padding-bottom: 6rem;
	}
	
	.product-card-web {
		background: white;
		border-radius: 1rem;
		overflow: hidden;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
		transition: all 0.3s;
		cursor: pointer;
	}
	
	.product-card-web:hover {
		transform: translateY(-4px);
		box-shadow: 0 20px 25px -5px rgba(16, 185, 129, 0.2);
	}
	
	.product-image-web {
		width: 100%;
		height: 200px;
		object-fit: cover;
	}
	
	.product-image-placeholder-web {
		width: 100%;
		height: 200px;
		background: linear-gradient(135deg, #f0fdf4, #ccfbf1);
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.tenant-badge-web {
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 600;
	}
	
	.checkout-button-web {
		padding: 1rem 2rem;
		background: linear-gradient(135deg, #10b981, #14b8a6);
		color: white;
		border-radius: 1rem;
		font-size: 1.125rem;
		transition: all 0.2s;
		box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
	}
	
	.checkout-button-web:hover {
		transform: scale(1.02);
		box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3);
	}
	
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 9999;
		animation: fadeIn 0.2s ease-out;
	}
	
	.modal-content-clear {
		background: white;
		padding: 2rem;
		border-radius: 1.5rem;
		max-width: 400px;
		width: 90%;
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
		animation: modalSlideIn 0.3s ease-out;
		text-align: center;
	}
	
	.modal-icon-danger {
		width: 80px;
		height: 80px;
		margin: 0 auto 1.5rem;
		background: linear-gradient(135deg, #fee2e2, #fecaca);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		animation: iconPulse 2s ease-in-out infinite;
	}
	
	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
	
	@keyframes modalSlideIn {
		from {
			transform: translateY(-20px);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}
	
	@keyframes iconPulse {
		0%, 100% {
			transform: scale(1);
			box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
		}
		50% {
			transform: scale(1.05);
			box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
		}
	}
	
	.cart-overlay-web {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		z-index: 50;
		backdrop-filter: blur(4px);
	}
	
	.cart-sidebar-web {
		position: fixed;
		top: 0;
		right: 0;
		bottom: 0;
		width: 100%;
		max-width: 400px;
		background: white;
		box-shadow: -4px 0 6px -1px rgba(0, 0, 0, 0.1);
		display: flex;
		flex-direction: column;
	}
	
	.cart-header-web {
		padding: 1.5rem;
		border-bottom: 2px solid #f3f4f6;
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: linear-gradient(135deg, #f0fdf4, #ccfbf1);
	}
	
	.cart-body-web {
		flex: 1;
		overflow-y: auto;
		padding: 1.5rem;
	}
	
	.cart-item-web {
		display: flex;
		gap: 1rem;
		padding: 1rem;
		background: #f9fafb;
		border-radius: 0.75rem;
		margin-bottom: 1rem;
		border: 1px solid #e5e7eb;
	}
	
	.qty-btn-web {
		width: 2rem;
		height: 2rem;
		border-radius: 0.5rem;
		background: #10b981;
		color: white;
		font-weight: bold;
		transition: background 0.2s;
		box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
	}
	
	.qty-btn-web:hover {
		background: #059669;
	}
	
	.cart-footer-web {
		padding: 1.5rem;
		border-top: 2px solid #f3f4f6;
		background: white;
	}
	
	@media (max-width: 640px) {
		.products-grid-web {
			grid-template-columns: 1fr;
		}
		
		.cart-sidebar-web {
			max-width: 100%;
		}
	}
</style>
