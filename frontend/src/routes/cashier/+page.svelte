<script>
	import { onMount } from 'svelte';
	import { cartItems, cartTotals, loadCart, addProductToCart, updateQuantity, removeCartItem, clearAllCart } from '$stores/cart.js';
	import { getProducts, getCategories } from '$db/index.js';
	import { browser } from '$app/environment';
	import { db } from '$db/index.js';
	import { isOnline, startSync } from '$stores/offline.js';
	import { broadcastNewOrder } from '$lib/stores/localSync.js';
	import PaymentModal from '$lib/components/PaymentModal.svelte';
	import SuccessModal from '$lib/components/SuccessModal.svelte';
	import ModifierModal from '$lib/components/ModifierModal.svelte';
	
	let products = [];
	let categories = [];
	let tenants = [];
	let selectedCategory = null;
	let selectedTenant = null;
	let showPaymentModal = false;
	let showSuccessModal = false;
	let showModifierModal = false;
	let selectedProduct = null;
	let checkoutResult = null;
	let loading = true;
	let searchQuery = '';
	
	// Customer info
	let customerName = '';
	let customerPhone = '';
	let tableNumber = '';
	
	$: filteredProducts = products.filter(p => {
		if (selectedTenant && p.tenant_id !== selectedTenant) return false;
		if (selectedCategory && p.category_name !== selectedCategory) return false;
		if (searchQuery && !p.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
		return p.is_available;
	});
	
	$: totalItems = $cartItems.reduce((sum, item) => sum + item.quantity, 0);
	$: totalAmount = parseFloat($cartTotals.total);
	
	// Group cart items by tenant
	$: groupedCartItems = Object.values(
		$cartItems.reduce((groups, item) => {
			const tenantId = item.tenant_id || 0;
			if (!groups[tenantId]) {
				groups[tenantId] = {
					tenant_id: tenantId,
					tenant_name: item.tenant_name || 'Unknown',
					tenant_color: item.tenant_color || '#6b7280',
					items: [],
					total: 0
				};
			}
			
			const parsedItem = {
				...item,
				modifiers: typeof item.modifiers === 'string' 
					? JSON.parse(item.modifiers || '[]') 
					: (item.modifiers || [])
			};
			
			groups[tenantId].items.push(parsedItem);
			
			const modifiersTotal = parsedItem.modifiers.reduce((sum, mod) => 
				sum + (parseFloat(mod.price_adjustment) || 0), 0);
			const itemTotal = (parseFloat(item.product_price) + modifiersTotal) * item.quantity;
			groups[tenantId].total += itemTotal;
			
			return groups;
		}, {})
	);
	
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
			
			if ($isOnline) {
				try {
					const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:8001/api';
					
					const productsRes = await fetch(`${apiUrl}/products/`);
					if (productsRes.ok) {
						const productsData = await productsRes.json();
						const freshProducts = productsData.results || productsData || [];
						
						if (freshProducts.length > 0) {
							await db.products.clear();
							await db.products.bulkAdd(freshProducts);
							products = freshProducts;
						}
					}
					
					const categoriesRes = await fetch(`${apiUrl}/categories/`);
					if (categoriesRes.ok) {
						const categoriesData = await categoriesRes.json();
						const freshCategories = categoriesData.results || categoriesData || [];
						
						if (freshCategories.length > 0) {
							await db.categories.clear();
							await db.categories.bulkAdd(freshCategories);
							categories = freshCategories;
						}
					}
				} catch (error) {
					console.warn('Sync failed:', error);
				}
			}
			
			// Extract unique tenants
			const uniqueTenants = [...new Set(products.map(p => p.tenant_id))].filter(Boolean);
			tenants = uniqueTenants.map(id => {
				const product = products.find(p => p.tenant_id === id);
				return {
					id,
					name: product?.tenant_name || `Tenant ${id}`,
					color: product?.tenant_color || '#6b7280'
				};
			});
		} catch (error) {
			console.error('Error loading products:', error);
		}
	}
	
	function getImageUrl(imagePath) {
		if (!imagePath) return null;
		if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
			return imagePath;
		}
		const backendUrl = import.meta.env.PUBLIC_API_URL?.replace('/api', '') || 'http://localhost:8001';
		return imagePath.startsWith('/') 
			? `${backendUrl}${imagePath}`
			: `${backendUrl}/${imagePath}`;
	}
	
	function selectProduct(product) {
		if (!product.is_available) return;
		selectedProduct = product;
		showModifierModal = true;
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
			selectedProduct = null;
		} catch (error) {
			console.error('Error adding to cart:', error);
		}
	}
	
	function handleCheckout() {
		if (totalItems === 0) return;
		showPaymentModal = true;
	}
	
	async function processCheckout(event) {
		const { paymentMethod } = event.detail;
		
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
				customer_name: customerName,
				customer_phone: customerPhone,
				table_number: tableNumber
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
					
					console.log('[Cashier] Checkout result:', result);
					
					if (result.orders && Array.isArray(result.orders)) {
						result.orders.forEach(order => {
							console.log('[Cashier] Broadcasting order:', order);
							broadcastNewOrder(order);
						});
					}
				} catch (fetchError) {
					console.warn('Online checkout failed:', fetchError.message);
					alert('Checkout failed: ' + fetchError.message);
					return;
				}
			} else {
				alert('Offline mode: Please connect to complete checkout');
				return;
			}
			
			await clearAllCart();
			
			// Reset customer info
			customerName = '';
			customerPhone = '';
			tableNumber = '';
			
			checkoutResult = result;
			showPaymentModal = false;
			showSuccessModal = true;
			
		} catch (error) {
			console.error('Checkout error:', error);
			alert(`Checkout failed: ${error.message}`);
		}
	}
	
	function handleSuccessClose() {
		showSuccessModal = false;
		setTimeout(() => {
			checkoutResult = null;
			selectedCategory = null;
			selectedTenant = null;
			searchQuery = '';
		}, 100);
	}
	
	async function clearCart() {
		if (!confirm('Clear all items from cart?')) return;
		await clearAllCart();
	}
</script>

<svelte:head>
	<title>Cashier POS - Food Court</title>
</svelte:head>

{#if loading}
	<div class="loading-screen">
		<div class="spinner"></div>
		<p>Loading POS System...</p>
	</div>
{:else}
	<div class="cashier-layout">
		<!-- LEFT: Product Selection -->
		<div class="products-section">
			<!-- Header -->
			<div class="section-header">
				<h2 class="text-xl font-bold text-gray-800">Products</h2>
				<input 
					type="search" 
					bind:value={searchQuery}
					placeholder="🔍 Search products..."
					class="search-input"
				/>
			</div>
			
			<!-- Filters -->
			<div class="filters-row">
				<div class="filter-group">
					<button 
						class="filter-chip {!selectedTenant ? 'active' : ''}"
						on:click={() => selectedTenant = null}
					>
						All Tenants
					</button>
					{#each tenants as tenant}
						<button 
							class="filter-chip {selectedTenant === tenant.id ? 'active' : ''}"
							style="--tenant-color: {tenant.color}"
							on:click={() => selectedTenant = tenant.id}
						>
							{tenant.name}
						</button>
					{/each}
				</div>
				
				<div class="filter-group">
					<button 
						class="filter-chip {!selectedCategory ? 'active' : ''}"
						on:click={() => selectedCategory = null}
					>
						All Categories
					</button>
					{#each categories as category}
						<button 
							class="filter-chip {selectedCategory === category.name ? 'active' : ''}"
							on:click={() => selectedCategory = category.name}
						>
							{category.name}
						</button>
					{/each}
				</div>
			</div>
			
			<!-- Products Grid -->
			<div class="products-grid">
				{#each filteredProducts as product}
					<button class="product-card" on:click={() => selectProduct(product)}>
						{#if getImageUrl(product.image)}
							<img src={getImageUrl(product.image)} alt={product.name} class="product-image" />
						{:else}
							<div class="product-placeholder">
								<svg class="w-12 h-12 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
								</svg>
							</div>
						{/if}
						<div class="product-info">
							<h3 class="product-name">{product.name}</h3>
							<p class="product-tenant">{product.tenant_name}</p>
							<p class="product-price">Rp {product.price.toLocaleString('id-ID')}</p>
						</div>
					</button>
				{/each}
			</div>
		</div>
		
		<!-- RIGHT: Cart Panel -->
		<div class="cart-section">
			<div class="cart-header">
				<h2>Current Order</h2>
				{#if $cartItems.length > 0}
					<button on:click={clearCart} class="btn-clear">Clear</button>
				{/if}
			</div>
			
			<!-- Customer Info -->
			<div class="customer-info">
				<input 
					type="text" 
					bind:value={customerName}
					placeholder="Customer Name"
					class="input-field"
				/>
				<input 
					type="tel" 
					bind:value={customerPhone}
					placeholder="Phone"
					class="input-field"
				/>
				<input 
					type="text" 
					bind:value={tableNumber}
					placeholder="Table #"
					class="input-field"
				/>
			</div>
			
			<!-- Cart Items -->
			<div class="cart-items">
				{#if $cartItems.length === 0}
					<div class="empty-cart">
						<svg class="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
						</svg>
						<p>No items</p>
					</div>
				{:else}
					{#each $cartItems as item}
						<div class="cart-item">
							<div class="item-info">
								<h4>{item.product_name}</h4>
								<p class="item-tenant">{item.tenant_name}</p>
								<p class="item-price">Rp {item.product_price?.toLocaleString('id-ID')}</p>
							</div>
							<div class="item-controls">
								<button on:click={() => updateQuantity(item.id, item.quantity - 1)} class="qty-btn">-</button>
								<span class="qty">{item.quantity}</span>
								<button on:click={() => updateQuantity(item.id, item.quantity + 1)} class="qty-btn">+</button>
								<button on:click={() => removeCartItem(item.id)} class="btn-remove">×</button>
							</div>
						</div>
					{/each}
				{/if}
			</div>
			
			<!-- Cart Footer -->
			{#if $cartItems.length > 0}
				<div class="cart-footer">
					<div class="totals">
						<div class="total-row">
							<span>Subtotal:</span>
							<span>Rp {$cartTotals.subtotal.toLocaleString('id-ID')}</span>
						</div>
						<div class="total-row">
							<span>Tax (10%):</span>
							<span>Rp {$cartTotals.tax.toLocaleString('id-ID')}</span>
						</div>
						<div class="total-row grand-total">
							<span>TOTAL:</span>
							<span>Rp {$cartTotals.total.toLocaleString('id-ID')}</span>
						</div>
					</div>
					<button on:click={handleCheckout} class="btn-checkout">
						Process Payment
					</button>
				</div>
			{/if}
		</div>
	</div>
{/if}

<!-- Modals -->
<ModifierModal 
	bind:product={selectedProduct} 
	on:addToCart={handleAddToCart}
	on:close={() => selectedProduct = null}
/>

{#if showPaymentModal}
	<PaymentModal 
		groupedCartItems={groupedCartItems}
		grandTotal={totalAmount}
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

<style>
	.loading-screen {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
		color: white;
	}
	
	.spinner {
		width: 48px;
		height: 48px;
		border: 4px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
		margin-bottom: 1rem;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
	
	.cashier-layout {
		min-height: 100vh;
		background: #f3f4f6;
		display: grid;
		grid-template-columns: 2fr 1fr;
		gap: 1rem;
		padding: 1rem;
	}
	
	.products-section {
		background: white;
		border-radius: 16px;
		padding: 1.5rem;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
		overflow-y: auto;
		max-height: calc(100vh - 2rem);
	}
	
	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1.5rem;
	}
	
	.search-input {
		width: 300px;
		padding: 0.75rem 1rem;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 0.875rem;
	}
	
	.search-input:focus {
		outline: none;
		border-color: #3b82f6;
	}
	
	.filters-row {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}
	
	.filter-group {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	
	.filter-chip {
		padding: 0.5rem 1rem;
		border-radius: 20px;
		border: 2px solid #e5e7eb;
		background: white;
		color: #6b7280;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.filter-chip:hover {
		border-color: #3b82f6;
		color: #3b82f6;
	}
	
	.filter-chip.active {
		background: var(--tenant-color, #3b82f6);
		border-color: var(--tenant-color, #3b82f6);
		color: white;
	}
	
	.products-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
		gap: 1rem;
	}
	
	.product-card {
		background: white;
		border: 2px solid #e5e7eb;
		border-radius: 12px;
		padding: 0;
		cursor: pointer;
		transition: all 0.2s;
		overflow: hidden;
	}
	
	.product-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.1);
		border-color: #3b82f6;
	}
	
	.product-image {
		width: 100%;
		height: 120px;
		object-fit: cover;
	}
	
	.product-placeholder {
		width: 100%;
		height: 120px;
		background: #f3f4f6;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.product-info {
		padding: 0.75rem;
	}
	
	.product-name {
		font-size: 0.875rem;
		font-weight: 600;
		color: #1f2937;
		margin-bottom: 0.25rem;
	}
	
	.product-tenant {
		font-size: 0.75rem;
		color: #6b7280;
		margin-bottom: 0.5rem;
	}
	
	.product-price {
		font-size: 1rem;
		font-weight: 700;
		color: #3b82f6;
	}
	
	.cart-section {
		background: white;
		border-radius: 16px;
		padding: 1.5rem;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
		display: flex;
		flex-direction: column;
		max-height: calc(100vh - 2rem);
		position: sticky;
		top: 1rem;
	}
	
	.cart-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
		padding-bottom: 1rem;
		border-bottom: 2px solid #e5e7eb;
	}
	
	.cart-header h2 {
		font-size: 1.25rem;
		font-weight: 700;
		color: #1f2937;
	}
	
	.btn-clear {
		padding: 0.5rem 1rem;
		background: #fee2e2;
		color: #dc2626;
		border-radius: 8px;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-clear:hover {
		background: #fecaca;
	}
	
	.customer-info {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}
	
	.input-field {
		padding: 0.625rem;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 0.875rem;
	}
	
	.input-field:focus {
		outline: none;
		border-color: #3b82f6;
	}
	
	.cart-items {
		flex: 1;
		overflow-y: auto;
		margin-bottom: 1rem;
	}
	
	.empty-cart {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 3rem 1rem;
		color: #9ca3af;
	}
	
	.cart-item {
		display: flex;
		gap: 0.75rem;
		padding: 0.75rem;
		border-bottom: 1px solid #e5e7eb;
	}
	
	.item-info {
		flex: 1;
	}
	
	.item-info h4 {
		font-size: 0.875rem;
		font-weight: 600;
		color: #1f2937;
		margin-bottom: 0.25rem;
	}
	
	.item-tenant {
		font-size: 0.75rem;
		color: #6b7280;
		margin-bottom: 0.25rem;
	}
	
	.item-price {
		font-size: 0.875rem;
		font-weight: 700;
		color: #3b82f6;
	}
	
	.item-controls {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	
	.qty-btn {
		width: 28px;
		height: 28px;
		border-radius: 6px;
		background: #f3f4f6;
		color: #374151;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.qty-btn:hover {
		background: #e5e7eb;
	}
	
	.qty {
		width: 32px;
		text-align: center;
		font-weight: 600;
	}
	
	.btn-remove {
		width: 28px;
		height: 28px;
		border-radius: 6px;
		background: #fee2e2;
		color: #dc2626;
		font-size: 1.25rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-remove:hover {
		background: #fecaca;
	}
	
	.cart-footer {
		padding-top: 1rem;
		border-top: 2px solid #e5e7eb;
	}
	
	.totals {
		margin-bottom: 1rem;
	}
	
	.total-row {
		display: flex;
		justify-content: space-between;
		font-size: 0.875rem;
		margin-bottom: 0.5rem;
	}
	
	.grand-total {
		font-size: 1.125rem;
		font-weight: 700;
		color: #1f2937;
		padding-top: 0.5rem;
		border-top: 2px solid #e5e7eb;
		margin-top: 0.5rem;
	}
	
	.grand-total span:last-child {
		color: #3b82f6;
	}
	
	.btn-checkout {
		width: 100%;
		padding: 1rem;
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
		color: white;
		border-radius: 12px;
		font-size: 1rem;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.2s;
		box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
	}
	
	.btn-checkout:hover {
		transform: translateY(-2px);
		box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
	}
	
	@media (max-width: 1024px) {
		.cashier-layout {
			grid-template-columns: 1fr;
		}
		
		.cart-section {
			position: relative;
			max-height: none;
		}
	}
</style>
