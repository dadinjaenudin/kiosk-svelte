<script>
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';
	import { cartItems, cartTotals, loadCart, addProductToCart, updateQuantity, removeCartItem, clearAllCart } from '$stores/cart.js';
	import { getProducts, getCategories } from '$db/index.js';
	import { browser } from '$app/environment';
	
	// SvelteKit props (suppress warnings)
	export let data = undefined;
	export let params = undefined;
	
	// State management
	let products = [];
	let categories = [];
	let selectedCategory = null;
	let isOnline = writable(browser ? navigator.onLine : true);
	let showCart = false;
	let isFullscreen = false;
	let loading = true;
	
	// Filtered products
	$: filteredProducts = selectedCategory 
		? products.filter(p => p.category_id === selectedCategory)
		: products;
	
	// Load data on mount
	onMount(async () => {
		try {
			// Load offline data
			await loadCart();
			categories = await getCategories();
			products = await getProducts();
			
			// Check for updates from server if online
			if ($isOnline) {
				await syncWithServer();
			}
			
			loading = false;
			
			// Request fullscreen on kiosk devices
			enterFullscreen();
			
			// Listen for online/offline events
			window.addEventListener('online', handleOnline);
			window.addEventListener('offline', handleOffline);
			
			// Keyboard shortcuts
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
	
	async function syncWithServer() {
		try {
			console.log('Syncing with server...');
			
			// Fetch categories from API
			const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:8001/api';
			
			const categoriesRes = await fetch(`${apiUrl}/products/categories/`);
			if (categoriesRes.ok) {
				const categoriesData = await categoriesRes.json();
				console.log('Categories API response:', categoriesData);
				
				// Handle both array and paginated response
				if (Array.isArray(categoriesData)) {
					categories = categoriesData;
				} else if (categoriesData.results) {
					categories = categoriesData.results; // Paginated response
				} else {
					categories = [];
					console.warn('Unexpected categories response format');
				}
				console.log('Categories loaded:', categories.length);
			} else {
				console.error('Categories API failed:', categoriesRes.status);
			}
			
			// Fetch products from API
			const productsRes = await fetch(`${apiUrl}/products/products/`);
			if (productsRes.ok) {
				const productsData = await productsRes.json();
				console.log('Products API response:', productsData);
				
				// Handle both array and paginated response
				if (Array.isArray(productsData)) {
					products = productsData;
				} else if (productsData.results) {
					products = productsData.results; // Paginated response
				} else {
					products = [];
					console.warn('Unexpected products response format');
				}
				console.log('Products loaded:', products.length);
			} else {
				console.error('Products API failed:', productsRes.status);
			}
		} catch (error) {
			console.error('Error syncing with server:', error);
		}
	}
	
	function handleOnline() {
		isOnline.set(true);
		syncWithServer();
	}
	
	function handleOffline() {
		isOnline.set(false);
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
			await addProductToCart(product, 1, []);
			// Show brief animation or toast
			playHapticFeedback();
		} catch (error) {
			console.error('Error adding to cart:', error);
			alert('Failed to add item to cart');
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
			if (browser) alert('Cart is empty!');
			return;
		}
		
		// Navigate to payment page
		if (browser) window.location.href = '/kiosk/payment';
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
	<title>POS Kiosk - Order Now</title>
</svelte:head>

<div class="h-screen-safe flex flex-col bg-gray-50 no-select tap-highlight-none">
	<!-- Header -->
	<header class="bg-primary text-white px-8 py-6 shadow-lg flex items-center justify-between">
		<div class="flex items-center gap-4">
			<h1 class="text-kiosk-3xl font-bold">🍽️ Restaurant POS</h1>
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
	</header>
	
	<!-- Main Content -->
	<div class="flex-1 flex overflow-hidden">
		<!-- Left Panel: Categories & Products -->
		<main class="flex-1 flex flex-col overflow-hidden">
			<!-- Categories -->
			<div class="bg-white px-8 py-6 shadow-sm overflow-x-auto scroll-smooth-touch">
				<div class="flex gap-4">
					<button 
						on:click={() => selectedCategory = null}
						class="category-pill {selectedCategory === null ? 'category-pill-active' : 'category-pill-inactive'}"
					>
						All Items
					</button>
					{#each categories as category}
						<button 
							on:click={() => selectedCategory = category.id}
							class="category-pill {selectedCategory === category.id ? 'category-pill-active' : 'category-pill-inactive'}"
						>
							{category.name}
						</button>
					{/each}
				</div>
			</div>
			
			<!-- Products Grid -->
			<div class="flex-1 overflow-y-auto scroll-smooth-touch p-8">
				{#if loading}
					<div class="flex items-center justify-center h-full">
						<div class="spinner w-24 h-24"></div>
					</div>
				{:else if filteredProducts.length === 0}
					<div class="flex flex-col items-center justify-center h-full text-gray-400">
						<div class="text-9xl mb-6">🍽️</div>
						<p class="text-kiosk-2xl font-semibold">No products available</p>
						<p class="text-kiosk-lg mt-2">Check back later or try another category</p>
					</div>
				{:else}
					<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
						{#each filteredProducts as product (product.id)}
							<button 
								on:click={() => handleAddToCart(product)}
								class="product-card ripple"
							>
								<div class="product-card-image">
									{#if product.image_url}
										<img src={product.image_url} alt={product.name} class="w-full h-full object-cover" />
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
			
			<!-- Cart Items -->
			<div class="flex-1 overflow-y-auto p-6 scroll-smooth-touch">
				{#if $cartItems.length === 0}
					<div class="flex flex-col items-center justify-center h-full text-gray-400">
						<div class="text-9xl mb-6">🛒</div>
						<p class="text-kiosk-xl font-semibold">Cart is empty</p>
						<p class="text-kiosk-base mt-2">Start adding items!</p>
					</div>
				{:else}
					{#each $cartItems as item (item.id)}
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
</div>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
