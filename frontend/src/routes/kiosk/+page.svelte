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
	
	// SvelteKit props (suppress warnings)
	export let data = undefined;
	
	// State management
	let products = [];
	let categories = [];
	let tenants = [];
	let outlets = [];  // Available outlets
	let selectedOutlet = null;  // Current outlet for this kiosk
	let selectedCategory = null;
	let selectedTenant = null;  // For filtering, not selection!
	// isOnline imported from $stores/offline.js
	let showCart = false;
	let showPaymentModal = false;
	let showSuccessModal = false;
	let showModifierModal = false;
	let selectedProduct = null;
	let checkoutResult = null;
	let isFullscreen = false;
	let loading = true;
	let showFilters = false; // Mobile filter menu
	let searchQuery = '';
	let showPopular = false;
	let showPromo = false;
	let showAvailable = true; // Default: show available only
	let pendingSyncCount = 0; // Track pending offline orders
	
	// Check pending sync count on mount and update periodically
	async function updatePendingSyncCount() {
		if (browser) {
			const queue = await db.sync_queue.count();
			pendingSyncCount = queue;
		}
	}
	
	// Load outlets from API
	async function loadOutlets() {
		try {
			const response = await fetch('http://localhost:8001/api/public/outlets/');
			if (response.ok) {
				const data = await response.json();
				outlets = data.results || data || [];
				console.log('[Kiosk] Loaded outlets:', outlets.length);
				
				// Try to restore selected outlet from localStorage
				const savedOutletId = localStorage.getItem('kiosk_outlet_id');
				if (savedOutletId) {
					const outlet = outlets.find(o => o.id === parseInt(savedOutletId));
					if (outlet) {
						selectedOutlet = outlet;
						console.log('[Kiosk] Restored outlet:', outlet.name);
					}
				}
				
				// If no outlet selected and only 1 outlet available, auto-select
				if (!selectedOutlet && outlets.length === 1) {
					selectedOutlet = outlets[0];
					localStorage.setItem('kiosk_outlet_id', outlets[0].id);
					console.log('[Kiosk] Auto-selected single outlet:', outlets[0].name);
				}
			} else {
				console.error('[Kiosk] Failed to load outlets:', response.status);
			}
		} catch (error) {
			console.error('[Kiosk] Error loading outlets:', error);
		}
	}
	
	// Change outlet and save to localStorage
	function changeOutlet(outletId) {
		const outlet = outlets.find(o => o.id === parseInt(outletId));
		if (outlet) {
			selectedOutlet = outlet;
			localStorage.setItem('kiosk_outlet_id', outlet.id);
			console.log('[Kiosk] Changed outlet to:', outlet.name);
		}
	}
	
	// Filtered products by tenant, category, search, and quick filters
	$: filteredProducts = products.filter(p => {
		// Tenant filter
		if (selectedTenant && p.tenant_id !== selectedTenant) return false;
		
		// Category filter
		if (selectedCategory && p.category !== selectedCategory) return false;
		
		// Search filter
		if (searchQuery) {
			const query = searchQuery.toLowerCase();
			const matchName = p.name?.toLowerCase().includes(query);
			const matchDesc = p.description?.toLowerCase().includes(query);
			const matchTenant = p.tenant_name?.toLowerCase().includes(query);
			if (!matchName && !matchDesc && !matchTenant) return false;
		}
		
		// Quick filters
		if (showPopular && !p.is_popular) return false;
		if (showPromo && !p.has_promo) return false;
		if (showAvailable && !p.is_available) return false;
		
		return true;
	});
	
	// Count filtered results
	$: resultCount = filteredProducts.length;
	
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
			
			// Parse modifiers if stored as JSON string
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
			
			// Debug logging
			console.log(`💰 Cart Item: ${item.product_name}`);
			console.log(`   Base: ${parseFloat(item.product_price)}, Modifiers: ${modifiersTotal}, Qty: ${item.quantity}`);
			console.log(`   Item Total: ${itemTotal}`);
			
			groups[tenantId].items.push(parsedItem);
			groups[tenantId].total += itemTotal;
			return groups;
		}, {})
	);
	
	// Calculate grand total from grouped items
	$: grandTotal = groupedCartItems.reduce((sum, group) => sum + group.total, 0);
	
	// API URL - dynamically determine based on hostname
	const getApiUrl = () => {
		if (typeof window === 'undefined') return 'http://localhost:8001/api';
		
		// Check env variable first
		if (import.meta.env.PUBLIC_API_URL) {
			console.log('Kiosk using API URL from env:', import.meta.env.PUBLIC_API_URL);
			return import.meta.env.PUBLIC_API_URL;
		}
		
		// Construct from current hostname
		const protocol = window.location.protocol;
		const hostname = window.location.hostname;
		const url = `${protocol}//${hostname}:8001/api`;
		console.log('Kiosk constructed API URL:', url);
		return url;
	};
	
	const apiUrl = getApiUrl();
	console.log('Kiosk final API URL:', apiUrl);
	
	// Load data on mount
	onMount(async () => {
		try {
			// Load cart from IndexedDB
			await loadCart();
			
			// Load outlets first (needed for sync)
			await loadOutlets();
			
			// Load kiosk data
			await loadKioskData();
			
			// Update pending sync count
			await updatePendingSyncCount();
			
			loading = false;
			
			// Note: Fullscreen must be triggered by user gesture (F11 key or button click)
			// Auto-fullscreen on mount is not allowed by browsers
			
			// Listen for online/offline events
			window.addEventListener('online', handleOnline);
			window.addEventListener('offline', handleOffline);
			window.addEventListener('keydown', handleKeyboard);
			
			// Update sync count every 10 seconds
			const syncCountInterval = setInterval(updatePendingSyncCount, 10000);
			
			return () => {
				window.removeEventListener('online', handleOnline);
				window.removeEventListener('offline', handleOffline);
				window.removeEventListener('keydown', handleKeyboard);
				clearInterval(syncCountInterval);
			};
			
		} catch (error) {
			console.error('Error loading kiosk data:', error);
			loading = false;
		}
	});
	
	/**
	 * Load ALL kiosk data (products, categories, tenants)
	 * FOOD COURT MODE: No tenant selection required
	 * OFFLINE-FIRST: Load from IndexedDB cache first, then sync with server
	 */
	async function loadKioskData() {
		try {
			console.log('🔄 Loading kiosk data (offline-first)...');
			
			// 1. Load from IndexedDB cache first (instant, works offline)
			const cachedProducts = await db.products.toArray();
			const cachedCategories = await db.categories.toArray();
			
			if (cachedProducts.length > 0) {
				products = cachedProducts;
				console.log('📦 Loaded from cache:', cachedProducts.length, 'products');
				
				// Extract tenants from cached products
				const tenantMap = new Map();
				products.forEach(p => {
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
			}
			
			if (cachedCategories.length > 0) {
				categories = cachedCategories;
				console.log('📦 Loaded from cache:', cachedCategories.length, 'categories');
			}
			
			// 2. If online, sync with server in background
			if ($isOnline) {
				console.log('🌐 Online - syncing with server...');
				try {
					// Fetch fresh data from server
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
							
							// Update tenants
							const tenantMap = new Map();
							products.forEach(p => {
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
						}
					}
					
					// Sync categories
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
			} else {
				console.log('📴 Offline - using cached data only');
			}
			
			// 3. If no data at all (first time), show message
			if (products.length === 0) {
				console.warn('⚠️ No products available (cache empty, offline)');
				alert('Tidak ada data produk. Silakan hubungkan internet untuk pertama kali.');
			}
			
		} catch (error) {
			console.error('❌ Error loading kiosk data:', error);
		}
	}
	
	async function syncWithServer() {
		if ($isOnline) {
			await loadKioskData();
		}
	}
	
	function handleOnline() {
		isOnline.set(true);
		console.log('🌐 Connection restored - syncing...');
		syncWithServer();
		// Sync pending orders
		startSync().then(() => {
			console.log('✅ Background sync completed');
		}).catch(err => {
			console.error('❌ Background sync failed:', err);
		});
	}
	
	function handleOffline() {
		isOnline.set(false);
		console.log('📴 Offline mode activated');
		alert('📴 Mode Offline: Transaksi akan disimpan dan dikirim otomatis saat online');
	}
	
	function selectCategory(categoryId) {
		selectedCategory = categoryId;
		console.log('Category selected:', categoryId);
	}
	
	function selectTenant(tenantId) {
		selectedTenant = tenantId;
		console.log('🏪 Tenant filter changed:', tenantId);
		console.log('📊 Products before filter:', products.length);
		
		// Debug: Check product tenant_id values
		const sampleProducts = products.slice(0, 5);
		console.log('🔍 Sample products tenant_id:', sampleProducts.map(p => ({
			name: p.name,
			tenant_id: p.tenant_id,
			tenant_name: p.tenant_name
		})));
		
		console.log('📊 Products after filter:', filteredProducts.length);
		console.log('🔍 Filtered products:', filteredProducts.slice(0, 3).map(p => p.name));
		
		if (tenantId) {
			const tenant = tenants.find(t => t.id === tenantId);
			console.log('🏪 Selected tenant:', tenant?.name);
			console.log('🔍 Looking for tenant_id:', tenantId);
			
			// Count products by tenant
			const productsByTenant = products.filter(p => p.tenant_id === tenantId);
			console.log(`📊 Products for tenant ${tenantId}:`, productsByTenant.length);
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
	
	// Open modifier modal when product clicked
	function handleProductClick(product) {
		console.log('🎯 Product clicked:', product?.name);
		console.log('📦 Product data:', product);
		selectedProduct = product;
		showModifierModal = true;
		console.log('✅ Modal state:', { showModifierModal, selectedProduct: selectedProduct?.name });
	}

	// Add to cart with modifiers
	async function handleAddToCart(event) {
		console.log('🎯 handleAddToCart called', event);
		
		const { product, quantity, modifiers, notes } = event.detail;
		
		console.log('📦 Adding to cart:', {
			product: product?.name,
			quantity,
			modifiers: modifiers?.length || 0,
			notes
		});
		
		try {
			// Add tenant info to product for cart grouping
			const productWithTenant = {
				...product,
				tenant_id: product.tenant_id,
				tenant_name: product.tenant_name,
				tenant_color: product.tenant_color
			};
			
			console.log('✅ Product with tenant:', productWithTenant);
			
			await addProductToCart(productWithTenant, quantity, modifiers, notes);
			
			console.log('✅ Product added to cart successfully');
			
			playHapticFeedback();
			showModifierModal = false;
			selectedProduct = null;
		} catch (error) {
			console.error('❌ Error adding to cart:', error);
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
				// Silent fail - fullscreen requires user gesture
				// Users can press F11 or use fullscreen button
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
		
		// Check if outlet is selected (required for kitchen routing)
		if (!selectedOutlet) {
			if (browser) alert('⚠️ Silahkan pilih outlet terlebih dahulu!\n\nOutlet diperlukan untuk mengirim pesanan ke kitchen yang benar.');
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
			
			let result;
			
			// OFFLINE-FIRST: Try online checkout first, fallback to offline queue
			if ($isOnline) {
				try {
					// Try online checkout
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
						
						// If network error, fallback to offline
						if (response.status >= 500 || response.status === 0) {
							throw new Error('Server error - will queue offline');
						}
						
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
					
					result = await response.json();
					console.log('✅ Online checkout successful:', result);
					
					// 📡 BROADCAST TO KITCHEN SYNC SERVER (Local Network)
					// Even if online to backend, still broadcast to local kitchen displays
					if (result.orders && Array.isArray(result.orders)) {
						result.orders.forEach(order => {
							broadcastNewOrder(order);
						});
					}
					
				} catch (fetchError) {
					console.warn('⚠️ Online checkout failed, queuing offline:', fetchError.message);
					// Fall through to offline handling
					result = await handleOfflineCheckout(checkoutData);
				}
			} else {
				// Offline mode - queue for later sync
				console.log('📴 Offline mode - queuing checkout');
				result = await handleOfflineCheckout(checkoutData);
			}
			
			// Clear cart
			await clearAllCart();
			
			// Update pending sync count
			await updatePendingSyncCount();
			
			// Show success modal
			checkoutResult = result;
			showPaymentModal = false;
			showSuccessModal = true;
			
		} catch (error) {
			console.error('❌ Checkout error:', error);
			alert(`Checkout gagal: ${error.message}`);
		}
	}
	
	/**
	 * Handle offline checkout - save to IndexedDB and queue for sync
	 */
	async function handleOfflineCheckout(checkoutData) {
		console.log('💾 Saving order offline...');
		
		// Generate offline order number
		const timestamp = Date.now();
		const orderNumber = `OFF-${timestamp}`;
		
		// Calculate total from cart
		const total = $cartTotals.total;
		
		// Group items by tenant for multi-tenant orders
		const itemsByTenant = {};
		$cartItems.forEach(item => {
			const tenantId = item.tenant_id || 'unknown';
			if (!itemsByTenant[tenantId]) {
				itemsByTenant[tenantId] = {
					tenant_id: tenantId,
					tenant_name: item.tenant_name,
					tenant_color: item.tenant_color,
					items: []
				};
			}
			itemsByTenant[tenantId].items.push(item);
		});
		
		// Create offline orders (one per tenant)
		const offlineOrders = [];
		
		for (const [tenantId, group] of Object.entries(itemsByTenant)) {
			const tenantOrderNumber = `${orderNumber}-T${tenantId}`;
			
			// Calculate tenant total
			const tenantTotal = group.items.reduce((sum, item) => {
				const modifiersTotal = (item.modifiers || []).reduce((mSum, mod) => 
					mSum + (parseFloat(mod.price_adjustment) || 0), 0);
				return sum + ((parseFloat(item.product_price) + modifiersTotal) * item.quantity);
			}, 0);
			
			const orderData = {
				order_number: tenantOrderNumber,
				outlet_id: selectedOutlet?.id || null,  // Add outlet_id for kitchen routing
				tenant_id: group.tenant_id,
				tenant_name: group.tenant_name,
				status: 'pending',
				payment_status: 'paid',
				payment_method: checkoutData.payment_method,
				customer_name: checkoutData.customer_name,
				customer_phone: checkoutData.customer_phone,
				table_number: checkoutData.table_number,
				notes: checkoutData.notes,
				subtotal: tenantTotal,
				tax: tenantTotal * 0.1,
				service_charge: tenantTotal * 0.05,
				total: tenantTotal * 1.15,
				items: group.items.map(item => ({
					product_id: item.product_id,
					product_name: item.product_name,
					quantity: item.quantity,
					price: item.product_price,
					modifiers: item.modifiers || [],
					notes: item.notes || ''
				})),
				created_at: new Date().toISOString(),
				sync_status: 'pending'
			};
			
			// Save to IndexedDB
			const orderId = await saveOrder(orderData);
			console.log(`💾 Saved offline order: ${tenantOrderNumber} (ID: ${orderId})`);
			
			// Add to sync queue
			await addToSyncQueue('order', orderId, 'create', orderData);
			console.log('📤 Added to sync queue');
			
			// 📡 BROADCAST TO KITCHEN SYNC SERVER (Local Network)
			broadcastNewOrder(orderData);
			
			offlineOrders.push({
				...orderData,
				id: orderId
			});
		}
		
		// Return result in same format as online checkout
		return {
			orders: offlineOrders,
			total_amount: total.toString(),
			payment_method: checkoutData.payment_method,
			offline: true,
			message: '📴 Order disimpan offline. Akan dikirim otomatis saat online.'
		};
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
	<header class="bg-primary text-white px-4 md:px-8 py-3 md:py-6 shadow-lg">
		<div class="flex items-center justify-between gap-2">
			<div class="flex items-center gap-2 md:gap-4 min-w-0 flex-1">
				<!-- Mobile: Filter Burger Button -->
				<button 
					on:click={() => showFilters = !showFilters}
					class="md:hidden btn-kiosk-secondary px-2 py-2 flex-shrink-0 relative"
					aria-label="Toggle filters"
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
					</svg>
					<!-- Active filter indicator -->
					{#if selectedTenant || selectedCategory}
						<span class="absolute -top-1 -right-1 bg-yellow-400 w-3 h-3 rounded-full"></span>
					{/if}
				</button>
				
				<h1 class="text-lg md:text-kiosk-3xl font-bold leading-tight">
					<span class="hidden md:inline">🍽️ Food Court Kiosk</span>
					<span class="md:hidden">🍽️ Food Court Kiosk</span>
				</h1>
				
				<!-- Outlet Selector -->
				{#if outlets.length > 0}
					<select
						bind:value={selectedOutlet}
						on:change={(e) => changeOutlet(e.target.value?.id || e.target.value)}
						class="hidden md:block px-3 py-2 bg-white text-gray-800 rounded-lg border-2 border-white/20 font-medium text-sm shadow-md hover:bg-gray-50 transition-colors"
					>
						<option value={null}>Select Outlet...</option>
						{#each outlets as outlet (outlet.id)}
							<option value={outlet.id} selected={selectedOutlet?.id === outlet.id}>
								📍 {outlet.name}
							</option>
						{/each}
					</select>
				{/if}
				
				{#if !$isOnline}
					<span class="offline-indicator text-kiosk-base px-3 py-1 bg-yellow-400 text-yellow-900 rounded-full font-semibold shadow-md">
						📴 Offline
					</span>
				{/if}
				{#if pendingSyncCount > 0}
					<span class="pending-sync-indicator text-sm px-2 py-1 bg-orange-500 text-white rounded-full font-semibold shadow-md">
						⏳ {pendingSyncCount} pending
					</span>
				{/if}
			</div>
			
			<button 
				on:click={() => showCart = !showCart}
				class="cart-button relative px-3 py-2 md:px-8 md:py-3 flex-shrink-0"
			>
				<span class="text-base md:text-kiosk-xl flex items-center gap-2">
					<!-- Cart Icon SVG -->
					<svg class="w-6 h-6 md:w-7 md:h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
					</svg>
					<span class="hidden md:inline">Cart</span>
				</span>
				{#if $cartTotals.itemCount > 0}
					<span class="absolute -top-1 -right-1 md:-top-2 md:-right-2 bg-red-500 text-white rounded-full w-6 h-6 md:w-12 md:h-12 flex items-center justify-center text-xs md:text-kiosk-base font-bold shadow-lg">
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
			<!-- Mobile Filter Panel (Slide Down) -->
			{#if showFilters}
				<div class="md:hidden fixed inset-0 z-50 bg-black bg-opacity-50" on:click={() => showFilters = false}>
					<div class="bg-white max-h-[70vh] overflow-y-auto" on:click|stopPropagation>
						<!-- Close button -->
						<div class="sticky top-0 bg-white border-b-2 border-gray-200 px-4 py-3 flex items-center justify-between">
							<h2 class="text-lg font-bold text-gray-800">Filters</h2>
							<button 
								on:click={() => showFilters = false}
								class="p-2 hover:bg-gray-100 rounded-lg"
							>
								<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
								</svg>
							</button>
						</div>
						
						<!-- Tenant Filters -->
						{#if tenants.length > 0}
							<div class="px-4 py-4 border-b-2 border-gray-200">
								<h3 class="text-sm font-semibold text-gray-600 mb-3">FILTER BY RESTAURANT:</h3>
								<div class="flex flex-wrap gap-2">
									<button 
										on:click={() => { selectTenant(null); showFilters = false; }}
										class="tenant-filter {selectedTenant === null ? 'tenant-filter-active' : 'tenant-filter-inactive'}"
									>
										All Restaurants
									</button>
									{#each tenants as tenant}
										<button 
											on:click={() => { selectTenant(tenant.id); showFilters = false; }}
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
						
						<!-- Category Filters -->
						<div class="px-4 py-4">
							<h3 class="text-sm font-semibold text-gray-600 mb-3">FILTER BY CATEGORY:</h3>
							<div class="flex flex-wrap gap-2">
								<button 
									on:click={() => { selectCategory(null); showFilters = false; }}
									class="category-pill {selectedCategory === null ? 'category-pill-active' : 'category-pill-inactive'}"
								>
									All Items
								</button>
								{#each categories as category}
									<button 
										on:click={() => { selectCategory(category.id); showFilters = false; }}
										class="category-pill {selectedCategory === category.id ? 'category-pill-active' : 'category-pill-inactive'}"
									>
										{category.name}
									</button>
								{/each}
							</div>
						</div>
					</div>
				</div>
			{/if}
			
			<!-- Desktop: Tenant Filter Tabs -->
			{#if tenants.length > 0}
				<div class="hidden md:block bg-white px-4 md:px-8 py-3 md:py-4 shadow-sm border-b-2 border-gray-200">
					<h3 class="text-xs md:text-sm font-semibold text-gray-600 mb-2">FILTER BY RESTAURANT:</h3>
					<div class="flex gap-2 md:gap-3 overflow-x-auto pb-1 scrollbar-thin">
						<button 
							on:click={() => selectTenant(null)}
							class="tenant-filter {selectedTenant === null ? 'tenant-filter-active' : 'tenant-filter-inactive'}"
						>
							<span class="hidden md:inline">All Restaurants</span>
							<span class="md:hidden">All</span>
						</button>
						{#each tenants as tenant}
							<button 
								on:click={() => selectTenant(tenant.id)}
								class="tenant-filter {selectedTenant === tenant.id ? 'tenant-filter-active' : 'tenant-filter-inactive'}"
								style="border-color: {selectedTenant === tenant.id ? tenant.color : '#e2e8f0'}; background: {selectedTenant === tenant.id ? tenant.color + '15' : 'white'}"
							>
								<span class="tenant-badge-dot" style="background: {tenant.color}"></span>
								<span class="hidden md:inline">{tenant.name}</span>
								<span class="md:hidden">{tenant.name.split(' ')[0]}</span>
							</button>
						{/each}
					</div>
				</div>
			{/if}
			
			<!-- Desktop: Category Tabs -->
			<div class="hidden md:block bg-white px-4 md:px-8 py-3 md:py-6 shadow-sm overflow-x-auto scroll-smooth-touch">
				<h3 class="text-xs md:text-sm font-semibold text-gray-600 mb-2">FILTER BY CATEGORY:</h3>
				<div class="flex gap-2 md:gap-4 pb-1">
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
			
			<!-- Search Bar & Quick Filters -->
			<div class="bg-white px-4 md:px-8 py-4 shadow-sm border-b-2 border-gray-200">
				<!-- Search Input -->
				<div class="relative mb-3">
					<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
						<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
						</svg>
					</div>
					<input 
						type="text"
						bind:value={searchQuery}
						placeholder="🔍 Cari menu atau restoran..."
						class="search-input w-full pl-10 pr-4 py-3 md:py-2 border-2 border-gray-300 rounded-xl focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
					/>
					{#if searchQuery}
						<button 
							on:click={() => searchQuery = ''}
							class="absolute inset-y-0 right-0 pr-3 flex items-center"
						>
							<svg class="w-5 h-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
							</svg>
						</button>
					{/if}
				</div>
				
				<!-- Quick Filters -->
				<div class="flex gap-2 flex-wrap">
					<button 
						on:click={() => showPopular = !showPopular}
						class="quick-filter {showPopular ? 'quick-filter-active' : 'quick-filter-inactive'}"
					>
						⭐ Populer
					</button>
					<button 
						on:click={() => showPromo = !showPromo}
						class="quick-filter {showPromo ? 'quick-filter-active' : 'quick-filter-inactive'}"
					>
						🔥 Promo
					</button>
					<button 
						on:click={() => showAvailable = !showAvailable}
						class="quick-filter {showAvailable ? 'quick-filter-active' : 'quick-filter-inactive'}"
					>
						✓ Tersedia
					</button>
				</div>
				
				<!-- Results Count -->
				{#if searchQuery || showPopular || showPromo || !showAvailable}
					<div class="mt-3 text-sm text-gray-600">
						<span class="font-semibold">Results:</span> {resultCount} produk ditemukan
					</div>
				{/if}
			</div>
			
			<!-- Products Grid -->
			<div class="flex-1 overflow-y-auto scroll-smooth-touch p-4 md:p-8 bg-gray-50">
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
					<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-6">
						{#each filteredProducts as product (product.id)}
							<button 
								on:click={() => handleProductClick(product)}
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
										<h3 class="font-bold text-sm md:text-kiosk-lg mb-1 line-clamp-1">{product.name}</h3>
										<p class="text-gray-600 text-xs md:text-kiosk-sm line-clamp-1 md:line-clamp-2 hidden md:block">{product.description || 'Delicious food item'}</p>
									</div>
									<p class="text-primary font-bold text-base md:text-kiosk-xl mt-2 md:mt-3">
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
			class="cart-panel w-full md:w-[480px] bg-white shadow-2xl transform transition-transform duration-300 {showCart ? 'translate-x-0' : 'translate-x-full'} fixed md:relative right-0 top-0 h-full z-40 flex flex-col overflow-x-hidden"
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
								{@const modifiersTotal = (item.modifiers || []).reduce((sum, mod) => sum + (parseFloat(mod.price_adjustment) || 0), 0)}
								
								<div class="flex gap-4 mb-4 pb-4 border-b border-gray-200 last:border-0">
									<div class="flex-1 min-w-0">
										<div class="flex items-start justify-between gap-2 mb-1">
											<h4 class="font-bold text-kiosk-base truncate flex-1">{item.product_name}</h4>
											<button 
												on:click={() => removeCartItem(item.id)}
												class="flex-shrink-0 w-8 h-8 bg-red-500 text-white rounded-lg text-sm font-bold hover:bg-red-600 active:scale-95 transition-all"
												title="Delete"
											>
												🗑️
											</button>
										</div>
										<p class="text-primary font-semibold text-kiosk-lg">
											{formatPrice(item.product_price)}
										</p>
										
										<!-- Modifiers Display -->
										{#if item.modifiers && item.modifiers.length > 0}
											<div class="mt-2 space-y-1">
												{#each item.modifiers as modifier}
													<div class="flex items-center gap-2 text-sm text-gray-600">
														<span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
														<span>{modifier.name}</span>
														{#if modifier.price_adjustment > 0}
															<span class="text-green-600 font-semibold">+{formatPrice(modifier.price_adjustment)}</span>
														{:else if modifier.price_adjustment < 0}
															<span class="text-red-600 font-semibold">{formatPrice(modifier.price_adjustment)}</span>
														{/if}
													</div>
												{/each}
											</div>
										{/if}
										
										<!-- Notes Display -->
										{#if item.notes}
											<div class="mt-2 text-sm text-gray-500 italic">
												📝 {item.notes}
											</div>
										{/if}
										
										<!-- Quantity Controls -->
										<div class="flex items-center gap-2 mt-3">
											<button 
												on:click={() => updateQuantity(item.id, item.quantity - 1)}
												class="w-10 h-10 bg-gray-200 rounded-lg text-xl font-bold hover:bg-gray-300 active:scale-95 transition-all"
											>
												−
											</button>
											<span class="text-xl font-bold min-w-[2.5rem] text-center">
												{item.quantity}
											</span>
											<button 
												on:click={() => updateQuantity(item.id, item.quantity + 1)}
												class="w-10 h-10 bg-primary text-white rounded-lg text-xl font-bold hover:bg-primary/90 active:scale-95 transition-all"
											>
												+
											</button>
										</div>
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
	
	<!-- Modifier Modal -->
	{#if showModifierModal && selectedProduct}
		<ModifierModal
			product={selectedProduct}
			on:close={() => { showModifierModal = false; selectedProduct = null; }}
			on:addToCart={handleAddToCart}
		/>
	{/if}
	
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
			offline={checkoutResult.offline || false}
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
		padding: 0.5rem 0.875rem;
		border-radius: 0.5rem;
		border: 2px solid;
		font-size: 0.7rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		white-space: nowrap;
		display: flex;
		align-items: center;
		gap: 0.25rem;
		flex-shrink: 0;
	}
	
	@media (min-width: 768px) {
		.tenant-filter {
			padding: 0.75rem 1.5rem;
			border-radius: 0.75rem;
			font-size: 0.875rem;
			gap: 0.5rem;
		}
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
		top: 0.25rem;
		left: 0.25rem;
		padding: 0.125rem 0.5rem;
		border-radius: 0.375rem;
		font-size: 0.625rem;
		font-weight: 700;
		color: white;
		z-index: 10;
		box-shadow: 0 2px 4px rgba(0,0,0,0.2);
	}
	
	@media (min-width: 768px) {
		.tenant-badge {
			top: 0.5rem;
			left: 0.5rem;
			padding: 0.25rem 0.75rem;
			border-radius: 0.5rem;
			font-size: 0.75rem;
		}
	}
	
	.tenant-badge-dot {
		display: inline-block;
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 50%;
		margin-right: 0.25rem;
	}
	
	@media (min-width: 768px) {
		.tenant-badge-dot {
			width: 0.75rem;
			height: 0.75rem;
		}
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
	
	/* Scrollbar styling for horizontal scroll */
	.scrollbar-thin {
		scrollbar-width: thin;
		scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
	}
	
	.scrollbar-thin::-webkit-scrollbar {
		height: 4px;
	}
	
	.scrollbar-thin::-webkit-scrollbar-track {
		background: transparent;
	}
	
	.scrollbar-thin::-webkit-scrollbar-thumb {
		background: rgba(156, 163, 175, 0.5);
		border-radius: 2px;
	}
	
	.scrollbar-thin::-webkit-scrollbar-thumb:hover {
		background: rgba(156, 163, 175, 0.7);
	}
	
	/* Mobile: Show scroll indicator shadow */
	@media (max-width: 767px) {
		.scrollbar-thin {
			position: relative;
		}
		
		.scrollbar-thin::after {
			content: '';
			position: absolute;
			right: 0;
			top: 0;
			bottom: 0;
			width: 40px;
			background: linear-gradient(to right, transparent, rgba(255,255,255,0.9));
			pointer-events: none;
		}
	}
	
	/* Cart Button - More prominent on mobile */
	.cart-button {
		background: rgba(255, 255, 255, 0.25);
		border: 2px solid rgba(255, 255, 255, 0.4);
		border-radius: 0.75rem;
		color: white;
		font-weight: 600;
		transition: all 0.2s;
		backdrop-filter: blur(10px);
		-webkit-backdrop-filter: blur(10px);
	}
	
	.cart-button:hover {
		background: rgba(255, 255, 255, 0.35);
		border-color: rgba(255, 255, 255, 0.6);
		transform: scale(1.05);
	}
	
	.cart-button:active {
		transform: scale(0.95);
	}
	
	@media (min-width: 768px) {
		.cart-button {
			background: var(--color-secondary);
			border-color: var(--color-secondary);
		}
		
		.cart-button:hover {
			background: rgba(var(--color-secondary-rgb), 0.9);
			border-color: var(--color-secondary);
		}
	}
	
	/* Search Input */
	.search-input {
		font-size: 0.875rem;
	}
	
	.search-input::placeholder {
		color: #9ca3af;
	}
	
	@media (min-width: 768px) {
		.search-input {
			font-size: 1rem;
		}
	}
	
	/* Quick Filter Buttons */
	.quick-filter {
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		border: 2px solid;
		cursor: pointer;
		transition: all 0.2s;
		white-space: nowrap;
	}
	
	.quick-filter-active {
		background: #10B981;
		border-color: #10B981;
		color: white;
	}
	
	.quick-filter-inactive {
		background: white;
		border-color: #e5e7eb;
		color: #4b5563;
	}
	
	.quick-filter-inactive:hover {
		border-color: #10B981;
		background: #f0fdf4;
		color: #10B981;
	}
	
	.quick-filter-active:hover {
		background: #059669;
	}

</style>
