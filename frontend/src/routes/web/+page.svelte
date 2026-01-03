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
	let selectedProduct = null;
	let checkoutResult = null;
	let loading = true;
	let searchQuery = '';
	let showAvailable = true;
	
	// Web-specific: Delivery options
	let orderType = 'delivery'; // 'delivery' or 'pickup'
	
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
		
		await broadcastNewOrder(event.detail.order);
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
		<main class="container mx-auto px-4 py-6">
			
			<!-- Category Filters -->
			{#if categories.length > 0}
				<div class="mb-6">
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
			<div class="products-grid-web">
				{#each filteredProducts as product}
					<div class="product-card-web" on:click={() => selectProduct(product)}>
						{#if product.image_url}
							<img src={product.image_url} alt={product.name} class="product-image-web" />
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
						<button on:click={() => showCart = false} class="text-gray-500 hover:text-gray-700">
							<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
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
										<h4 class="font-semibold text-gray-800">{item.name}</h4>
										<p class="text-sm text-gray-500">{item.tenant_name}</p>
										<p class="text-emerald-600 font-semibold">Rp {item.price.toLocaleString('id-ID')}</p>
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
	/* 🌐 WEB MODERN THEME - Emerald/Teal (Customer-Facing) */
	.web-ordering {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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
