<script>
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';
	import { cartItems, cartTotals, loadCart, addProductToCart, updateQuantity, removeCartItem, clearAllCart } from '$stores/cart.js';
	import { getProducts, getCategories } from '$db/index.js';
	import { browser } from '$app/environment';
	import PaymentModal from '$lib/components/PaymentModal.svelte';
	import SuccessModal from '$lib/components/SuccessModal.svelte';
	
	// SvelteKit props (suppress warnings)
	export let data = undefined;
	
	// State management
	let products = [];
	let categories = [];
	let tenants = [];
	let selectedCategory = null;
	let selectedTenant = null;  // For filtering, not selection!
	let isOnline = writable(browser ? navigator.onLine : true);
	let showCart = false;
	let showPaymentModal = false;
	let showSuccessModal = false;
	let checkoutResult = null;
	let isFullscreen = false;
	let loading = true;
	
	// Filtered products by tenant AND category
	$: filteredProducts = products.filter(p => {
		if (selectedTenant && p.tenant_id !== selectedTenant) return false;
		if (selectedCategory && p.category !== selectedCategory) return false;
		return true;
	});
	
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
			groups[tenantId].items.push(item);
			groups[tenantId].total += item.product_price * item.quantity;
			return groups;
		}, {})
	);
	
	// Calculate grand total from grouped items
	$: grandTotal = groupedCartItems.reduce((sum, group) => sum + group.total, 0);
	
	// API URL
	const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:8001/api';
	
	// Load data on mount
	onMount(async () => {
		try {
			// Load cart from IndexedDB
			await loadCart();
			
			// Load kiosk data
			await loadKioskData();
			
			loading = false;
			
			// Request fullscreen on kiosk devices
			enterFullscreen();
			
			// Listen for online/offline events
			window.addEventListener('online', handleOnline);
			window.addEventListener('offline', handleOffline);
			window.addEventListener('keydown', handleKeyboard);
			
		} catch (error) {
			console.error('Error loading kiosk data:', error);
			loading = false;
		}
		
		return () => {
			window.removeEventListener('online', handleOnline);
			window.removeEventListener('offline', handleOffline);
			window.removeEventListener('keydown', handleKeyboard);
		};
	});
	
	/**
	 * Load ALL kiosk data (products, categories, tenants)
	 * FOOD COURT MODE: No tenant selection required
	 */
	async function loadKioskData() {
		try {
			console.log('Loading food court data...');
			
			// Load ALL products from ALL tenants
			const productsRes = await fetch(`${apiUrl}/products/products/`);
			if (productsRes.ok) {
				const productsData = await productsRes.json();
				products = productsData.results || productsData || [];
				console.log('✅ Products loaded:', products.length);
				console.log('📦 First product:', products[0]);  // Debug: show first product
				
				// Extract unique tenants from products
				const tenantMap = new Map();
				products.forEach(p => {
					console.log(`Product: ${p.name}, Tenant ID: ${p.tenant_id}, Tenant Name: ${p.tenant_name}`);  // Debug each product
					if (p.tenant_id && !tenantMap.has(p.tenant_id)) {
						tenantMap.set(p.tenant_id, {
							id: p.tenant_id,
							name: p.tenant_name,
							slug: p.tenant_slug,
							color: p.tenant_color
						});
					}
				});
				tenants = Array.from(tenantMap.values());
				console.log('✅ Tenants extracted:', tenants.length);
				console.log('🏪 Tenants:', tenants);  // Debug: show all tenants
			}
			
			// Load ALL categories
			const categoriesRes = await fetch(`${apiUrl}/products/categories/`);
			if (categoriesRes.ok) {
				const categoriesData = await categoriesRes.json();
				categories = categoriesData.results || categoriesData || [];
				console.log('Categories loaded:', categories.length);
			}
			
		} catch (error) {
			console.error('Error loading kiosk data:', error);
		}
	}
	
	async function syncWithServer() {
		if ($isOnline) {
			await loadKioskData();
		}
	}
	
	function handleOnline() {
		isOnline.set(true);
		syncWithServer();
	}
	
	function handleOffline() {
		isOnline.set(false);
	}
	
	function selectCategory(categoryId) {
		selectedCategory = categoryId;
		console.log('Category selected:', categoryId);
	}
	
	function selectTenant(tenantId) {
		selectedTenant = tenantId;
		console.log('🏪 Tenant filter changed:', tenantId);
		console.log('📊 Products before filter:', products.length);
		console.log('📊 Products after filter:', filteredProducts.length);
		if (tenantId) {
			const tenant = tenants.find(t => t.id === tenantId);
			console.log('🏪 Selected tenant:', tenant?.name);
		} else {
			console.log('🏪 Showing all restaurants');
		}
	}
	
	function handleKeyboard(e) {
		if (e.key === 'F11') {
			e.preventDefault();
			toggleFullscreen();
		} else if (e.key === 'Escape') {
			if (showCart) showCart = false;
		}
	}
	
	async function handleAddToCart(product) {
		try {
			// Add tenant info to product for cart grouping
			const productWithTenant = {
				...product,
				tenant_id: product.tenant_id,
				tenant_name: product.tenant_name,
				tenant_color: product.tenant_color
			};
			await addProductToCart(productWithTenant, 1, []);
			playHapticFeedback();
		} catch (error) {
			console.error('Error adding to cart:', error);
			if (browser) alert('Failed to add item to cart');
		}
	}
	
	function playHapticFeedback() {
		if (browser && navigator.vibrate) {
			navigator.vibrate(50);
		}
	}
	
	function enterFullscreen() {
		if (!browser) return;
		const elem = document.documentElement;
		if (elem.requestFullscreen) {
			elem.requestFullscreen().catch(err => {
				console.log('Fullscreen request failed:', err);
			});
		}
	}
	
	function toggleFullscreen() {
		if (!browser) return;
		if (!document.fullscreenElement) {
			enterFullscreen();
			isFullscreen = true;
		} else {
			if (document.exitFullscreen) {
				document.exitFullscreen();
				isFullscreen = false;
			}
		}
	}
	
	async function handleCheckout() {
		if ($cartItems.length === 0) {
			if (browser) alert('Keranjang kosong!');
			return;
		}
		
		// Show payment modal
		showCart = false;
		showPaymentModal = true;
	}
	
	async function processCheckout(event) {
		const { paymentMethod, customerName, customerPhone, tableNumber, notes } = event.detail;
		
		try {
			// Debug: Log cart items
			console.log('🛒 Cart items:', $cartItems);
			
			// Prepare checkout data
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
				customer_name: customerName,
				customer_phone: customerPhone,
				table_number: tableNumber,
				notes: notes
			};
			
			console.log('💳 Processing checkout:', checkoutData);
			
			// Call checkout API
			const response = await fetch(`${apiUrl}/orders/checkout/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(checkoutData)
			});
			
			if (!response.ok) {
				const error = await response.json();
				console.error('❌ Checkout error response:', error);
				console.error('❌ Full error object:', JSON.stringify(error, null, 2));
				
				// Extract detailed error message
				let errorMessage = 'Checkout failed';
				if (error.error) {
					errorMessage = error.error;
				} else if (error.detail) {
					errorMessage = error.detail;
				} else if (error.items && Array.isArray(error.items)) {
					errorMessage = error.items.join(', ');
				} else if (typeof error === 'object') {
					errorMessage = JSON.stringify(error);
				}
				
				throw new Error(errorMessage);
			}
			
			const result = await response.json();
			console.log('✅ Checkout successful:', result);
			console.log('📦 Orders created:', result.orders?.map(o => ({
				order_number: o.order_number,
				tenant_id: o.tenant?.id || o.tenant_id,
				tenant_name: o.tenant?.name || o.tenant_name,
				status: o.status,
				payment_status: o.payment_status,
				items_count: o.items?.length || 0
			})));
			
			// Clear cart
			await clearAllCart();
			
			// Show success modal
			checkoutResult = result;
			showPaymentModal = false;
			showSuccessModal = true;
			
		} catch (error) {
			console.error('❌ Checkout error:', error);
			alert(`Checkout gagal: ${error.message}`);
		}
	}
	
	function cancelPayment() {
		showPaymentModal = false;
	}
	
	function closeSuccessModal() {
		showSuccessModal = false;
		checkoutResult = null;
	}
	
	function formatPrice(price) {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(price);
	}
</script>

<svelte:head>
	<title>Food Court Kiosk - Order Now</title>
</svelte:head>

<div class="h-screen-safe flex flex-col bg-gray-50 no-select tap-highlight-none">
	<!-- Header -->
	<header class="bg-primary text-white px-8 py-6 shadow-lg">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-4">
				<h1 class="text-kiosk-3xl font-bold">🍽️ Food Court Kiosk</h1>
				{#if !$isOnline}
					<span class="offline-indicator text-kiosk-base">
						📴 Offline Mode
					</span>
				{/if}
			</div>
			
			<button 
				on:click={() => showCart = !showCart}
				class="btn-kiosk-secondary relative px-8"
			>
				<span class="text-kiosk-xl">🛒 Cart</span>
				{#if $cartTotals.itemCount > 0}
					<span class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-12 h-12 flex items-center justify-center text-kiosk-base font-bold animate-bounce-in">
						{$cartTotals.itemCount}
					</span>
				{/if}
			</button>
		</div>
	</header>
	
	<!-- Main Content -->
	<div class="flex-1 flex overflow-hidden">
		<!-- Left Panel: Filters & Products -->
		<main class="flex-1 flex flex-col overflow-hidden">
			<!-- Tenant Filter Tabs -->
			{#if tenants.length > 0}
				<div class="bg-white px-8 py-4 shadow-sm border-b-2 border-gray-200">
					<h3 class="text-sm font-semibold text-gray-600 mb-2">FILTER BY RESTAURANT:</h3>
					<div class="flex gap-3 overflow-x-auto scroll-smooth-touch">
						<button 
							on:click={() => selectTenant(null)}
							class="tenant-filter {selectedTenant === null ? 'tenant-filter-active' : 'tenant-filter-inactive'}"
						>
							All Restaurants
						</button>
						{#each tenants as tenant}
							<button 
								on:click={() => selectTenant(tenant.id)}
								class="tenant-filter {selectedTenant === tenant.id ? 'tenant-filter-active' : 'tenant-filter-inactive'}"
								style="border-color: {selectedTenant === tenant.id ? tenant.color : '#e2e8f0'}; background: {selectedTenant === tenant.id ? tenant.color + '15' : 'white'}"
							>
								<span class="tenant-badge-dot" style="background: {tenant.color}"></span>
								{tenant.name}
							</button>
						{/each}
					</div>
				</div>
			{/if}
			
			<!-- Category Tabs -->
			<div class="bg-white px-8 py-6 shadow-sm overflow-x-auto scroll-smooth-touch">
				<h3 class="text-sm font-semibold text-gray-600 mb-2">FILTER BY CATEGORY:</h3>
				<div class="flex gap-4">
					<button 
						on:click={() => selectCategory(null)}
						class="category-pill {selectedCategory === null ? 'category-pill-active' : 'category-pill-inactive'}"
					>
						All Items
					</button>
					{#each categories as category}
						<button 
							on:click={() => selectCategory(category.id)}
							class="category-pill {selectedCategory === category.id ? 'category-pill-active' : 'category-pill-inactive'}"
						>
							{category.name}
						</button>
					{/each}
				</div>
			</div>
			
			<!-- Products Grid -->
			<div class="flex-1 overflow-y-auto scroll-smooth-touch p-8 bg-gray-50">
				{#if loading}
					<div class="flex items-center justify-center h-full">
						<div class="spinner w-24 h-24"></div>
					</div>
				{:else if filteredProducts.length === 0}
					<div class="flex flex-col items-center justify-center h-full text-gray-400">
						<div class="text-9xl mb-6">🍽️</div>
						<p class="text-kiosk-2xl font-semibold">No products available</p>
						<p class="text-kiosk-lg mt-2">Try different filters</p>
					</div>
				{:else}
					<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
						{#each filteredProducts as product (product.id)}
							<button 
								on:click={() => handleAddToCart(product)}
								class="product-card ripple"
							>
								<!-- Tenant Badge -->
								<div class="tenant-badge" style="background: {product.tenant_color}">
									{product.tenant_name}
								</div>
								
								<div class="product-card-image">
									{#if product.image}
										<img src={product.image} alt={product.name} class="w-full h-full object-cover" />
									{:else}
										<div class="flex items-center justify-center h-full text-6xl">
											🍔
										</div>
									{/if}
								</div>
								<div class="product-card-body">
									<div>
										<h3 class="font-bold text-kiosk-lg mb-1">{product.name}</h3>
										<p class="text-gray-600 text-kiosk-sm line-clamp-2">{product.description || 'Delicious food item'}</p>
									</div>
									<p class="text-primary font-bold text-kiosk-xl mt-3">
										{formatPrice(product.price)}
									</p>
								</div>
							</button>
						{/each}
					</div>
				{/if}
			</div>
		</main>
		
		<!-- Right Panel: Cart (Sliding) -->
		<aside 
			class="cart-panel w-full md:w-[480px] bg-white shadow-2xl transform transition-transform duration-300 {showCart ? 'translate-x-0' : 'translate-x-full'} fixed md:relative right-0 top-0 h-full z-40 flex flex-col"
		>
			<!-- Cart Header -->
			<div class="bg-gradient-to-r from-primary to-secondary text-white px-6 py-6 flex items-center justify-between">
				<h2 class="text-kiosk-2xl font-bold">Your Order</h2>
				<button 
					on:click={() => showCart = false}
					class="text-kiosk-2xl md:hidden hover:scale-110 transition-transform"
				>
					✕
				</button>
			</div>
			
			<!-- Cart Items (Grouped by Tenant) -->
			<div class="flex-1 overflow-y-auto p-6 scroll-smooth-touch">
				{#if $cartItems.length === 0}
					<div class="flex flex-col items-center justify-center h-full text-gray-400">
						<div class="text-9xl mb-6">🛒</div>
						<p class="text-kiosk-xl font-semibold">Cart is empty</p>
						<p class="text-kiosk-base mt-2">Start adding items!</p>
					</div>
				{:else}
					{#each groupedCartItems as tenantGroup}
						<div class="tenant-group mb-6">
							<h4 class="tenant-group-header" style="color: {tenantGroup.tenant_color}; border-color: {tenantGroup.tenant_color}">
								<span class="tenant-badge-dot" style="background: {tenantGroup.tenant_color}"></span>
								{tenantGroup.tenant_name}
							</h4>
							
							{#each tenantGroup.items as item (item.id)}
								<div class="cart-item">
									<div class="flex-1">
										<h4 class="font-bold text-kiosk-base">{item.product_name}</h4>
										<p class="text-primary font-semibold text-kiosk-lg">
											{formatPrice(item.product_price)}
										</p>
									</div>
									
									<div class="flex items-center gap-3">
										<button 
											on:click={() => updateQuantity(item.id, item.quantity - 1)}
											class="w-14 h-14 bg-gray-200 rounded-lg text-kiosk-xl font-bold hover:bg-gray-300 active:scale-95 transition-all"
										>
											−
										</button>
										<span class="text-kiosk-xl font-bold min-w-[3rem] text-center">
											{item.quantity}
										</span>
										<button 
											on:click={() => updateQuantity(item.id, item.quantity + 1)}
											class="w-14 h-14 bg-primary text-white rounded-lg text-kiosk-xl font-bold hover:bg-primary/90 active:scale-95 transition-all"
										>
											+
										</button>
										<button 
											on:click={() => removeCartItem(item.id)}
											class="w-14 h-14 bg-red-500 text-white rounded-lg text-kiosk-xl font-bold hover:bg-red-600 active:scale-95 transition-all ml-2"
										>
											🗑️
										</button>
									</div>
								</div>
							{/each}
							
							<div class="tenant-group-total">
								Subtotal: {formatPrice(tenantGroup.total)}
							</div>
						</div>
					{/each}
				{/if}
			</div>
			
			<!-- Cart Summary & Checkout -->
			{#if $cartItems.length > 0}
				<div class="border-t-4 border-gray-200 p-6 bg-gray-50">
					<div class="space-y-2 mb-6">
						<div class="flex justify-between text-kiosk-base">
							<span class="text-gray-600">Subtotal:</span>
							<span class="font-semibold">{formatPrice($cartTotals.subtotal)}</span>
						</div>
						<div class="flex justify-between text-kiosk-base">
							<span class="text-gray-600">Tax (10%):</span>
							<span class="font-semibold">{formatPrice($cartTotals.tax)}</span>
						</div>
						<div class="flex justify-between text-kiosk-base">
							<span class="text-gray-600">Service (5%):</span>
							<span class="font-semibold">{formatPrice($cartTotals.serviceCharge)}</span>
						</div>
						<div class="flex justify-between text-kiosk-2xl font-bold text-primary pt-3 border-t-2 border-gray-300">
							<span>Total:</span>
							<span>{formatPrice($cartTotals.total)}</span>
						</div>
					</div>
					
					<div class="flex gap-3">
						<button 
							on:click={clearAllCart}
							class="flex-1 btn-kiosk bg-gray-300 text-gray-700 hover:bg-gray-400"
						>
							Clear Cart
						</button>
						<button 
							on:click={handleCheckout}
							class="flex-[2] btn-kiosk-primary"
						>
							Checkout →
						</button>
					</div>
				</div>
			{/if}
		</aside>
	</div>
	
	<!-- Payment Modal -->
	{#if showPaymentModal}
		<PaymentModal
			groupedCartItems={groupedCartItems}
			grandTotal={grandTotal}
			on:checkout={processCheckout}
			on:cancel={cancelPayment}
		/>
	{/if}
	
	<!-- Success Modal -->
	{#if showSuccessModal && checkoutResult}
		<SuccessModal
			orders={checkoutResult.orders}
			payments={checkoutResult.payments}
			totalAmount={parseFloat(checkoutResult.total_amount)}
			paymentMethod={checkoutResult.payment_method}
			on:close={closeSuccessModal}
		/>
	{/if}
</div>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
	
	.tenant-filter {
		padding: 0.75rem 1.5rem;
		border-radius: 0.75rem;
		border: 2px solid;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		white-space: nowrap;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	
	.tenant-filter-active {
		border-color: var(--color-primary);
		background: rgba(102, 126, 234, 0.1);
		color: var(--color-primary);
	}
	
	.tenant-filter-inactive {
		border-color: #e2e8f0;
		background: white;
		color: #4a5568;
	}
	
	.tenant-filter:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(0,0,0,0.1);
	}
	
	.tenant-badge {
		position: absolute;
		top: 0.5rem;
		left: 0.5rem;
		padding: 0.25rem 0.75rem;
		border-radius: 0.5rem;
		font-size: 0.75rem;
		font-weight: 700;
		color: white;
		z-index: 10;
		box-shadow: 0 2px 4px rgba(0,0,0,0.2);
	}
	
	.tenant-badge-dot {
		display: inline-block;
		width: 0.75rem;
		height: 0.75rem;
		border-radius: 50%;
		margin-right: 0.25rem;
	}
	
	.tenant-group {
		border: 2px solid #e2e8f0;
		border-radius: 1rem;
		padding: 1rem;
		background: white;
	}
	
	.tenant-group-header {
		font-size: 1.125rem;
		font-weight: 700;
		padding-bottom: 0.75rem;
		margin-bottom: 0.75rem;
		border-bottom: 2px solid;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	
	.tenant-group-total {
		margin-top: 0.75rem;
		padding-top: 0.75rem;
		border-top: 1px solid #e2e8f0;
		text-align: right;
		font-weight: 600;
		color: #4a5568;
	}
</style>
