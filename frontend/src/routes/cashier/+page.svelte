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
	let showCart = true; // Cashier: Always show cart for quick entry
	let showPaymentModal = false;
	let showSuccessModal = false;
	let showModifierModal = false;
	let selectedProduct = null;
	let checkoutResult = null;
	let loading = true;
	let searchQuery = '';
	let showAvailable = true;
	
	// Cashier-specific fields
	let customerName = '';
	let customerPhone = '';
	let tableNumber = '';
	let orderNotes = '';
	let showCustomerForm = false;
	
	$: filteredProducts = products.filter(p => {
		if (selectedTenant && p.tenant_id !== selectedTenant) return false;
		if (selectedCategory && p.category_id !== selectedCategory) return false;
		if (showAvailable && !p.is_available) return false;
		if (searchQuery && !p.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
		return true;
	});
	
	$: totalItems = $cartItems.reduce((sum, item) => sum + item.quantity, 0);
	
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
			products = await getProducts();
			categories = await getCategories();
			
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
	
	function selectProduct(product) {
		if (!product.is_available) return;
		selectedProduct = product;
		showModifierModal = true;
	}
	
	function handleCheckout() {
		if (totalItems === 0) return;
		showPaymentModal = true;
	}
	
	async function handlePaymentComplete(event) {
		showPaymentModal = false;
		checkoutResult = event.detail;
		showSuccessModal = true;
		
		// Reset customer form
		customerName = '';
		customerPhone = '';
		tableNumber = '';
		orderNotes = '';
		showCustomerForm = false;
		
		await broadcastNewOrder(event.detail.order);
	}
	
	function quickAddProduct(product) {
		if (!product.is_available) return;
		// Quick add without modifiers
		addProductToCart(product, [], '');
	}
</script>

<svelte:head>
	<title>Cashier POS - Food Court</title>
</svelte:head>

{#if loading}
	<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-700 to-gray-900">
		<div class="text-center text-white">
			<div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white mx-auto mb-4"></div>
			<p class="text-xl font-semibold">Loading Cashier POS...</p>
		</div>
	</div>
{:else}
	<div class="cashier-pos min-h-screen bg-gray-100">
		
		<!-- Header - Cashier Professional Style (Gray/Dark Theme) -->
		<header class="cashier-header sticky top-0 z-40 bg-gradient-to-r from-gray-800 to-gray-900 text-white shadow-lg">
			<div class="container mx-auto px-4 py-3">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
							<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
						</div>
						<div>
							<h1 class="text-lg font-bold">💰 Cashier POS</h1>
							<p class="text-xs text-gray-300">Staff Terminal</p>
						</div>
					</div>
					
					<div class="flex items-center gap-4">
						<div class="text-sm">
							<div class="text-gray-300">Online Status</div>
							<div class="font-semibold {$isOnline ? 'text-green-400' : 'text-red-400'}">
								{$isOnline ? '🟢 Connected' : '🔴 Offline'}
							</div>
						</div>
						
						<button on:click={() => showCustomerForm = !showCustomerForm} class="btn-cashier-secondary">
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
							Customer
						</button>
					</div>
				</div>
				
				<!-- Customer Form (Expandable) -->
				{#if showCustomerForm}
					<div class="mt-4 bg-gray-700 rounded-lg p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
						<input 
							type="text" 
							bind:value={customerName}
							placeholder="Customer Name"
							class="input-cashier"
						/>
						<input 
							type="tel" 
							bind:value={customerPhone}
							placeholder="Phone Number"
							class="input-cashier"
						/>
						<input 
							type="text" 
							bind:value={tableNumber}
							placeholder="Table Number"
							class="input-cashier"
						/>
						<input 
							type="text" 
							bind:value={orderNotes}
							placeholder="Order Notes"
							class="input-cashier"
						/>
					</div>
				{/if}
			</div>
		</header>
		
		<!-- Main Content - Split View (Products | Cart) -->
		<main class="container mx-auto px-4 py-4">
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
				
				<!-- LEFT: Products Panel -->
				<div class="lg:col-span-2">
					
					<!-- Search Bar -->
					<div class="mb-4">
						<input 
							type="search" 
							bind:value={searchQuery}
							placeholder="🔍 Search products... (Quick entry)"
							class="w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:border-blue-500 focus:outline-none bg-white"
						/>
					</div>
					
					<!-- Category Filters - Compact -->
					{#if categories.length > 0}
						<div class="mb-4">
							<div class="flex gap-2 overflow-x-auto pb-2">
								<button 
									class="category-chip-cashier {!selectedCategory ? 'active' : ''}"
									on:click={() => selectedCategory = null}
								>
									All
								</button>
								{#each categories as category}
									<button 
										class="category-chip-cashier {selectedCategory === category.id ? 'active' : ''}"
										on:click={() => selectedCategory = category.id}
									>
										{category.name}
									</button>
								{/each}
							</div>
						</div>
					{/if}
					
					<!-- Products Grid - Compact List View -->
					<div class="products-list-cashier">
						{#each filteredProducts as product}
							<div class="product-row-cashier" on:click={() => selectProduct(product)}>
								<div class="flex items-center gap-3 flex-1">
									{#if product.image_url}
										<img src={product.image_url} alt={product.name} class="product-thumb-cashier" />
									{:else}
										<div class="product-thumb-placeholder-cashier">
											<svg class="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
											</svg>
										</div>
									{/if}
									
									<div class="flex-1">
										<h3 class="font-semibold text-gray-800">{product.name}</h3>
										<p class="text-xs text-gray-500">{product.tenant_name}</p>
									</div>
								</div>
								
								<div class="flex items-center gap-3">
									<span class="text-lg font-bold text-gray-800">
										Rp {product.price.toLocaleString('id-ID')}
									</span>
									<button 
										on:click|stopPropagation={() => quickAddProduct(product)}
										class="btn-quick-add"
										disabled={!product.is_available}
									>
										{#if product.is_available}
											<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
											</svg>
										{:else}
											<span class="text-xs">N/A</span>
										{/if}
									</button>
								</div>
							</div>
						{/each}
					</div>
				</div>
				
				<!-- RIGHT: Cart Panel (Always Visible for Cashier) -->
				<div class="lg:col-span-1">
					<div class="cart-panel-cashier sticky top-20">
						<div class="cart-header-cashier">
							<h2 class="text-lg font-bold">📋 Current Order</h2>
							{#if $cartItems.length > 0}
								<button on:click={clearAllCart} class="text-red-600 hover:text-red-700 text-sm font-semibold">
									Clear All
								</button>
							{/if}
						</div>
						
						<div class="cart-body-cashier">
							{#if $cartItems.length === 0}
								<div class="text-center py-12 text-gray-400">
									<svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
									</svg>
									<p class="text-sm">No items</p>
								</div>
							{:else}
								{#each $cartItems as item}
									<div class="cart-item-cashier">
										<div class="flex-1">
											<h4 class="font-semibold text-gray-800 text-sm">{item.name}</h4>
											<p class="text-xs text-gray-500">{item.tenant_name}</p>
											<p class="text-blue-600 font-semibold text-sm">Rp {item.price.toLocaleString('id-ID')}</p>
										</div>
										<div class="flex items-center gap-1">
											<button on:click={() => updateQuantity(item.id, item.quantity - 1)} class="qty-btn-cashier">-</button>
											<span class="font-semibold text-sm w-8 text-center">{item.quantity}</span>
											<button on:click={() => updateQuantity(item.id, item.quantity + 1)} class="qty-btn-cashier">+</button>
											<button on:click={() => removeCartItem(item.id)} class="text-red-500 hover:text-red-700 ml-1">
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
												</svg>
											</button>
										</div>
									</div>
								{/each}
							{/if}
						</div>
						
						{#if $cartItems.length > 0}
							<div class="cart-footer-cashier">
								<div class="space-y-2 mb-4">
									<div class="flex justify-between text-sm">
										<span>Subtotal:</span>
										<span>Rp {$cartTotals.subtotal.toLocaleString('id-ID')}</span>
									</div>
									<div class="flex justify-between text-sm">
										<span>Tax ({$cartTotals.taxRate}%):</span>
										<span>Rp {$cartTotals.tax.toLocaleString('id-ID')}</span>
									</div>
									<div class="flex justify-between text-lg font-bold border-t-2 border-gray-300 pt-2">
										<span>TOTAL:</span>
										<span class="text-blue-600">Rp {$cartTotals.total.toLocaleString('id-ID')}</span>
									</div>
								</div>
								<button on:click={handleCheckout} class="btn-checkout-cashier w-full">
									💳 Process Payment
								</button>
							</div>
						{/if}
					</div>
				</div>
				
			</div>
		</main>
		
	</div>
{/if}

<ModifierModal 
	bind:show={showModifierModal} 
	bind:product={selectedProduct} 
	on:addToCart
/>

<PaymentModal 
	bind:show={showPaymentModal}
	on:complete={handlePaymentComplete}
	on:cancel={() => showPaymentModal = false}
/>

<SuccessModal 
	bind:show={showSuccessModal}
	orderData={checkoutResult}
	on:close={() => showSuccessModal = false}
/>

<style>
	/* 💰 CASHIER PROFESSIONAL THEME - Gray/Dark (Staff-Facing) */
	.cashier-pos {
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
	}
	
	.btn-cashier-secondary {
		padding: 0.5rem 1rem;
		background: rgba(255, 255, 255, 0.1);
		border: 1px solid rgba(255, 255, 255, 0.3);
		border-radius: 0.5rem;
		color: white;
		font-weight: 600;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		transition: all 0.2s;
	}
	
	.btn-cashier-secondary:hover {
		background: rgba(255, 255, 255, 0.2);
	}
	
	.input-cashier {
		padding: 0.5rem 0.75rem;
		border-radius: 0.5rem;
		border: 1px solid rgba(255, 255, 255, 0.3);
		background: rgba(255, 255, 255, 0.1);
		color: white;
		font-size: 0.875rem;
	}
	
	.input-cashier::placeholder {
		color: rgba(255, 255, 255, 0.5);
	}
	
	.category-chip-cashier {
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		background: white;
		border: 2px solid #e5e7eb;
		font-weight: 600;
		font-size: 0.875rem;
		color: #4b5563;
		white-space: nowrap;
		transition: all 0.2s;
	}
	
	.category-chip-cashier.active {
		background: #3b82f6;
		border-color: #3b82f6;
		color: white;
	}
	
	.products-list-cashier {
		background: white;
		border-radius: 0.75rem;
		overflow: hidden;
		box-shadow: 0 1px 3px rgba(0,0,0,0.1);
		max-height: calc(100vh - 280px);
		overflow-y: auto;
	}
	
	.product-row-cashier {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem 1rem;
		border-bottom: 1px solid #f3f4f6;
		cursor: pointer;
		transition: background 0.2s;
	}
	
	.product-row-cashier:hover {
		background: #f9fafb;
	}
	
	.product-thumb-cashier {
		width: 48px;
		height: 48px;
		border-radius: 0.5rem;
		object-fit: cover;
	}
	
	.product-thumb-placeholder-cashier {
		width: 48px;
		height: 48px;
		border-radius: 0.5rem;
		background: #f3f4f6;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.btn-quick-add {
		padding: 0.5rem;
		background: #3b82f6;
		border-radius: 0.5rem;
		color: white;
		transition: background 0.2s;
	}
	
	.btn-quick-add:hover:not(:disabled) {
		background: #2563eb;
	}
	
	.btn-quick-add:disabled {
		background: #e5e7eb;
		color: #9ca3af;
		cursor: not-allowed;
	}
	
	.cart-panel-cashier {
		background: white;
		border-radius: 0.75rem;
		box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
		overflow: hidden;
		display: flex;
		flex-direction: column;
		max-height: calc(100vh - 120px);
	}
	
	.cart-header-cashier {
		padding: 1rem;
		background: linear-gradient(135deg, #1f2937, #374151);
		color: white;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	
	.cart-body-cashier {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
		min-height: 300px;
	}
	
	.cart-item-cashier {
		display: flex;
		gap: 0.75rem;
		padding: 0.75rem;
		background: #f9fafb;
		border-radius: 0.5rem;
		margin-bottom: 0.75rem;
		border: 1px solid #e5e7eb;
	}
	
	.qty-btn-cashier {
		width: 1.75rem;
		height: 1.75rem;
		border-radius: 0.375rem;
		background: #3b82f6;
		color: white;
		font-weight: bold;
		font-size: 0.875rem;
		transition: background 0.2s;
	}
	
	.qty-btn-cashier:hover {
		background: #2563eb;
	}
	
	.cart-footer-cashier {
		padding: 1rem;
		border-top: 2px solid #e5e7eb;
		background: #f9fafb;
	}
	
	.btn-checkout-cashier {
		padding: 0.875rem 1.5rem;
		background: linear-gradient(135deg, #3b82f6, #2563eb);
		color: white;
		border-radius: 0.75rem;
		font-size: 1rem;
		font-weight: bold;
		transition: all 0.2s;
		box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.4);
	}
	
	.btn-checkout-cashier:hover {
		transform: scale(1.02);
		box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
	}
	
	@media (max-width: 1024px) {
		.cart-panel-cashier {
			max-height: none;
		}
	}
</style>
