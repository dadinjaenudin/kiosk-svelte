<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { kioskConfig, multiCart } from '$lib/stores/kioskStore';
	import ModifierModal from '$lib/components/ModifierModal.svelte';
	
	const API_BASE = 'http://localhost:8001/api';
	
	let outletId: number;
	let outlet: any = null;
	let products: any[] = [];
	let categories: any[] = [];
	let selectedCategory: string | null = null;
	let loading = true;
	let error = '';
	let searchQuery = '';
	
	// Modifier modal
	let showModifierModal = false;
	let selectedProduct: any = null;
	
	$: outletId = parseInt($page.params.outletId);
	$: cartItemsCount = $multiCart.itemsCount;
	$: cartTotal = $multiCart.totalAmount;
	
	// Filter products by category and search
	$: filteredProducts = products.filter(p => {
		if (selectedCategory && p.category !== selectedCategory) return false;
		if (searchQuery) {
			const query = searchQuery.toLowerCase();
			return p.name?.toLowerCase().includes(query) || 
			       p.description?.toLowerCase().includes(query);
		}
		return true;
	});
	
	onMount(async () => {
		console.log('🍔 Menu page mounted, outlet:', outletId);
		await loadOutletData();
		await loadProducts();
	});
	
	async function loadOutletData() {
		try {
			const response = await fetch(`${API_BASE}/public/outlets/${outletId}/`);
			if (response.ok) {
				outlet = await response.json();
				console.log('✅ Outlet loaded:', outlet.name);
			} else {
				error = 'Failed to load restaurant data';
			}
		} catch (err) {
			error = 'Connection error';
			console.error('Load outlet error:', err);
		}
	}
	
	async function loadProducts() {
		loading = true;
		try {
			const response = await fetch(
				`${API_BASE}/public/products/?outlet=${outletId}&is_available=true`
			);
			
			if (response.ok) {
				const data = await response.json();
				products = data.results || data || [];
				
				// Extract unique categories
				categories = [...new Set(products.map(p => p.category))].filter(Boolean);
				
				console.log('✅ Loaded', products.length, 'products');
			} else {
				error = 'Failed to load menu';
			}
		} catch (err) {
			error = 'Connection error';
			console.error('Load products error:', err);
		} finally {
			loading = false;
		}
	}
	
	function selectCategory(category: string | null) {
		selectedCategory = category;
	}
	
	function openProductModal(product: any) {
		selectedProduct = product;
		showModifierModal = true;
	}
	
	function handleAddToCart(event: CustomEvent) {
		const { product, quantity, modifiers, notes } = event.detail;
		
		if (!outlet) return;
		
		multiCart.addItem(
			outlet.id,
			outlet.name,
			outlet.tenant.name,
			outlet.tenant.primary_color || '#667eea',
			product,
			quantity,
			modifiers,
			notes
		);
		
		showModifierModal = false;
		selectedProduct = null;
		
		console.log('✅ Added to cart:', product.name);
	}
	
	function backToOutlets() {
		goto('/kiosk');
	}
	
	function viewCart() {
		goto('/kiosk/cart');
	}
	
	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
</script>

<div class="menu-page">
	<!-- Header -->
	<header class="menu-header">
		<button class="btn-back" on:click={backToOutlets}>
			<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
		</button>
		
		<div class="outlet-info">
			{#if outlet}
				<div 
					class="outlet-badge" 
					style="background-color: {outlet.tenant.primary_color || '#667eea'}"
				></div>
				<div>
					<h1>{outlet.name}</h1>
					<p class="tenant-name">{outlet.tenant.name}</p>
				</div>
			{:else}
				<h1>Loading...</h1>
			{/if}
		</div>
		
		{#if cartItemsCount > 0}
			<button class="cart-btn" on:click={viewCart}>
				<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
						d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
				</svg>
				<span class="cart-badge">{cartItemsCount}</span>
			</button>
		{/if}
	</header>
	
	<!-- Search Bar -->
	<div class="search-bar">
		<svg class="icon-search" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
				d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
		</svg>
		<input
			type="text"
			placeholder="Search menu..."
			bind:value={searchQuery}
		/>
	</div>
	
	<!-- Categories -->
	{#if categories.length > 0}
		<div class="categories">
			<button 
				class="category-chip"
				class:active={!selectedCategory}
				on:click={() => selectCategory(null)}
			>
				All
			</button>
			{#each categories as category}
				<button 
					class="category-chip"
					class:active={selectedCategory === category}
					on:click={() => selectCategory(category)}
				>
					{category}
				</button>
			{/each}
		</div>
	{/if}
	
	<!-- Products Grid -->
	<div class="products-container">
		{#if loading}
			<div class="loading">
				<div class="spinner"></div>
				<p>Loading menu...</p>
			</div>
		{:else if error}
			<div class="error-message">
				<p>⚠️ {error}</p>
				<button class="btn-retry" on:click={loadProducts}>Try Again</button>
			</div>
		{:else if filteredProducts.length === 0}
			<div class="empty-state">
				<p>No products found</p>
			</div>
		{:else}
			<div class="products-grid">
				{#each filteredProducts as product (product.id)}
					<button class="product-card" on:click={() => openProductModal(product)}>
						{#if product.image}
							<img src={product.image} alt={product.name} class="product-image" />
						{:else}
							<div class="product-image-placeholder">
								<svg class="icon-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
										d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
								</svg>
							</div>
						{/if}
						
						<div class="product-info">
							<h3>{product.name}</h3>
							{#if product.description}
								<p class="product-description">{product.description}</p>
							{/if}
							<p class="product-price">{formatCurrency(product.price)}</p>
							
							{#if product.has_promo}
								<span class="promo-badge">🔥 Promo</span>
							{/if}
						</div>
					</button>
				{/each}
			</div>
		{/if}
	</div>
	
	<!-- Cart Floating Button -->
	{#if cartItemsCount > 0}
		<button class="cart-floating" on:click={viewCart}>
			<div class="cart-floating-content">
				<div>
					<span class="cart-floating-count">{cartItemsCount} items</span>
					<span class="cart-floating-total">{formatCurrency(cartTotal)}</span>
				</div>
				<span class="cart-floating-arrow">→</span>
			</div>
		</button>
	{/if}
</div>

<!-- Modifier Modal -->
{#if showModifierModal && selectedProduct}
	<ModifierModal
		product={selectedProduct}
		on:add={handleAddToCart}
		on:close={() => {
			showModifierModal = false;
			selectedProduct = null;
		}}
	/>
{/if}

<style>
	.menu-page {
		min-height: 100vh;
		background: #f5f5f5;
		padding-bottom: 100px;
	}
	
	.menu-header {
		background: white;
		padding: 16px 20px;
		display: flex;
		align-items: center;
		gap: 16px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		position: sticky;
		top: 0;
		z-index: 100;
	}
	
	.btn-back {
		background: none;
		border: none;
		padding: 8px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 8px;
		transition: background 0.2s;
	}
	
	.btn-back:hover {
		background: #f0f0f0;
	}
	
	.icon {
		width: 24px;
		height: 24px;
	}
	
	.outlet-info {
		flex: 1;
		display: flex;
		align-items: center;
		gap: 12px;
	}
	
	.outlet-badge {
		width: 12px;
		height: 40px;
		border-radius: 6px;
	}
	
	.outlet-info h1 {
		font-size: 20px;
		font-weight: 600;
		margin: 0;
		color: #1a1a1a;
	}
	
	.tenant-name {
		font-size: 14px;
		color: #666;
		margin: 0;
	}
	
	.cart-btn {
		position: relative;
		background: #667eea;
		color: white;
		border: none;
		padding: 10px 16px;
		border-radius: 8px;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 8px;
		transition: all 0.2s;
	}
	
	.cart-btn:hover {
		background: #5568d3;
		transform: translateY(-2px);
	}
	
	.cart-badge {
		background: #ff6b6b;
		color: white;
		font-size: 12px;
		font-weight: 600;
		padding: 2px 8px;
		border-radius: 12px;
		min-width: 20px;
		text-align: center;
	}
	
	.search-bar {
		padding: 16px 20px;
		background: white;
		display: flex;
		align-items: center;
		gap: 12px;
	}
	
	.icon-search {
		width: 20px;
		height: 20px;
		color: #999;
	}
	
	.search-bar input {
		flex: 1;
		border: none;
		outline: none;
		font-size: 16px;
		color: #1a1a1a;
	}
	
	.categories {
		padding: 16px 20px;
		display: flex;
		gap: 8px;
		overflow-x: auto;
		background: white;
		border-bottom: 1px solid #e0e0e0;
	}
	
	.category-chip {
		padding: 8px 16px;
		border: 1px solid #e0e0e0;
		border-radius: 20px;
		background: white;
		color: #666;
		font-size: 14px;
		cursor: pointer;
		white-space: nowrap;
		transition: all 0.2s;
	}
	
	.category-chip.active {
		background: #667eea;
		color: white;
		border-color: #667eea;
	}
	
	.category-chip:hover {
		border-color: #667eea;
	}
	
	.products-container {
		padding: 20px;
	}
	
	.products-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 20px;
	}
	
	.product-card {
		background: white;
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		cursor: pointer;
		transition: all 0.3s;
		border: none;
		text-align: left;
		padding: 0;
	}
	
	.product-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
	}
	
	.product-image {
		width: 100%;
		height: 200px;
		object-fit: cover;
	}
	
	.product-image-placeholder {
		width: 100%;
		height: 200px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.icon-lg {
		width: 64px;
		height: 64px;
		color: rgba(255, 255, 255, 0.8);
	}
	
	.product-info {
		padding: 16px;
	}
	
	.product-info h3 {
		font-size: 18px;
		font-weight: 600;
		margin: 0 0 8px 0;
		color: #1a1a1a;
	}
	
	.product-description {
		font-size: 14px;
		color: #666;
		margin: 0 0 12px 0;
		line-height: 1.4;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
	
	.product-price {
		font-size: 20px;
		font-weight: 700;
		color: #667eea;
		margin: 0;
	}
	
	.promo-badge {
		display: inline-block;
		margin-top: 8px;
		padding: 4px 8px;
		background: #ff6b6b;
		color: white;
		font-size: 12px;
		border-radius: 4px;
		font-weight: 600;
	}
	
	.loading, .error-message, .empty-state {
		text-align: center;
		padding: 60px 20px;
		color: #666;
	}
	
	.spinner {
		width: 48px;
		height: 48px;
		border: 4px solid #e0e0e0;
		border-top-color: #667eea;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 16px;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
	
	.btn-retry {
		margin-top: 16px;
		padding: 10px 24px;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		font-size: 16px;
	}
	
	.cart-floating {
		position: fixed;
		bottom: 20px;
		left: 20px;
		right: 20px;
		background: #667eea;
		color: white;
		border: none;
		padding: 16px 24px;
		border-radius: 12px;
		box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
		cursor: pointer;
		transition: all 0.3s;
		z-index: 90;
	}
	
	.cart-floating:hover {
		transform: translateY(-4px);
		box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
	}
	
	.cart-floating-content {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	
	.cart-floating-count {
		font-size: 14px;
		display: block;
		opacity: 0.9;
	}
	
	.cart-floating-total {
		font-size: 20px;
		font-weight: 700;
		display: block;
	}
	
	.cart-floating-arrow {
		font-size: 24px;
		font-weight: 700;
	}
</style>
