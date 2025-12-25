<script>
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { writable } from 'svelte/store';
	
	// Props
	export let data = undefined;
	export let params = undefined;
	
	// Tenant state
	let tenants = [];
	let selectedTenant = null;
	let selectedOutlet = null;
	let outlets = [];
	let loading = true;
	let error = null;
	
	// Products state
	let categories = [];
	let products = [];
	let selectedCategory = null;
	let showCart = false;
	let isFullscreen = false;
	
	// Cart store
	import { cartItems, cartTotals, loadCart, addProductToCart, updateQuantity, removeCartItem, clearAllCart } from '$lib/stores/cart.js';
	
	const isOnline = writable(browser ? navigator.onLine : true);
	
	// Reactive: filter products by category
	$: filteredProducts = selectedCategory 
		? products.filter(p => p.category === selectedCategory)
		: products;
	
	// API base URL
	const apiUrl = browser ? (import.meta.env.PUBLIC_API_URL || 'http://localhost:8001/api') : 'http://localhost:8001/api';
	
	/**
	 * Load tenants list
	 */
	async function loadTenants() {
		try {
			const response = await fetch(`${apiUrl}/tenants/`);
			if (response.ok) {
				const data = await response.json();
				tenants = data.results || data || [];
				console.log('Tenants loaded:', tenants.length);
				
				// Auto-select if only one tenant
				if (tenants.length === 1) {
					await selectTenant(tenants[0]);
				}
			} else {
				console.error('Failed to load tenants:', response.status);
			}
		} catch (err) {
			console.error('Error loading tenants:', err);
		}
	}
	
	/**
	 * Select tenant and load outlets
	 */
	async function selectTenant(tenant) {
		selectedTenant = tenant;
		
		// Save to localStorage
		if (browser) {
			localStorage.setItem('kiosk_tenant_id', tenant.id);
		}
		
		// Load outlets for this tenant
		await loadOutlets(tenant.id);
	}
	
	/**
	 * Load outlets for selected tenant
	 */
	async function loadOutlets(tenantId) {
		try {
			const response = await fetch(`${apiUrl}/tenants/${tenantId}/outlets/`);
			if (response.ok) {
				const data = await response.json();
				outlets = data.results || data || [];
				console.log('Outlets loaded:', outlets.length);
				
				// Auto-select if only one outlet
				if (outlets.length === 1) {
					selectOutlet(outlets[0]);
				} else if (outlets.length === 0) {
					// No outlets, proceed anyway
					await loadKioskData();
				}
			} else {
				console.error('Failed to load outlets:', response.status);
				// Proceed anyway even if outlets API fails
				await loadKioskData();
			}
		} catch (err) {
			console.error('Error loading outlets:', err);
			// Proceed anyway
			await loadKioskData();
		}
	}
	
	/**
	 * Select outlet and load kiosk data
	 */
	async function selectOutlet(outlet) {
		selectedOutlet = outlet;
		
		// Save to localStorage
		if (browser) {
			localStorage.setItem('kiosk_outlet_id', outlet.id);
		}
		
		// Load kiosk data
		await loadKioskData();
	}
	
	/**
	 * Load kiosk data (categories and products)
	 */
	async function loadKioskData() {
		try {
			loading = true;
			
			// Load cart from IndexedDB
			await loadCart();
			
			// Sync with server if online
			if ($isOnline) {
				await syncWithServer();
			}
			
			loading = false;
			
			// Try to enter fullscreen on kiosk devices
			if (browser && document.body.requestFullscreen) {
				try {
					await enterFullscreen();
				} catch (err) {
					console.log('Fullscreen request failed:', err);
				}
			}
		} catch (err) {
			console.error('Error loading kiosk data:', err);
			error = err.message;
			loading = false;
		}
	}
	
	/**
	 * Sync with server (categories and products)
	 */
	async function syncWithServer() {
		try {
			console.log('Syncing with server...');
			
			// Build headers with tenant/outlet context
			const headers = {};
			if (selectedTenant) {
				headers['X-Tenant-ID'] = selectedTenant.id;
			}
			if (selectedOutlet) {
				headers['X-Outlet-ID'] = selectedOutlet.id;
			}
			
			// Fetch categories
			const categoriesRes = await fetch(`${apiUrl}/products/categories/`, { headers });
			
			if (categoriesRes.ok) {
				const categoriesData = await categoriesRes.json();
				console.log('Categories API response:', categoriesData);
				
				// Handle pagination
				if (categoriesData && categoriesData.results) {
					categories = categoriesData.results;
				} else if (Array.isArray(categoriesData)) {
					categories = categoriesData;
				} else {
					categories = [];
					console.warn('Unexpected categories response format:', categoriesData);
				}
				
				console.log('Categories loaded:', categories.length);
			} else {
				console.error('Categories API failed:', categoriesRes.status);
			}
			
			// Fetch products
			const productsRes = await fetch(`${apiUrl}/products/products/`, { headers });
			
			if (productsRes.ok) {
				const productsData = await productsRes.json();
				console.log('Products API response:', productsData);
				
				// Handle pagination
				if (productsData && productsData.results) {
					products = productsData.results;
				} else if (Array.isArray(productsData)) {
					products = productsData;
				} else {
					products = [];
					console.warn('Unexpected products response format:', productsData);
				}
				
				console.log('Products loaded:', products.length);
			} else {
				console.error('Products API failed:', productsRes.status);
			}
			
		} catch (err) {
			console.error('Error syncing with server:', err);
		}
	}
	
	/**
	 * Handle online/offline status
	 */
	function handleOnline() {
		isOnline.set(true);
		syncWithServer();
	}
	
	function handleOffline() {
		isOnline.set(false);
	}
	
	/**
	 * Handle keyboard shortcuts
	 */
	function handleKeyboard(event) {
		if (event.key === 'F11') {
			event.preventDefault();
			toggleFullscreen();
		} else if (event.key === 'Escape') {
			showCart = false;
		}
	}
	
	/**
	 * Toggle fullscreen
	 */
	async function toggleFullscreen() {
		if (!document.fullscreenElement) {
			await enterFullscreen();
		} else {
			await exitFullscreen();
		}
	}
	
	async function enterFullscreen() {
		try {
			await document.body.requestFullscreen();
			isFullscreen = true;
		} catch (err) {
			console.log('Fullscreen request failed:', err);
		}
	}
	
	async function exitFullscreen() {
		try {
			await document.exitFullscreen();
			isFullscreen = false;
		} catch (err) {
			console.log('Exit fullscreen failed:', err);
		}
	}
	
	/**
	 * Select category filter
	 */
	function selectCategory(categoryId) {
		selectedCategory = categoryId;
		console.log('Category selected:', categoryId);
		console.log('Filtered products:', filteredProducts.length);
		if (filteredProducts.length > 0) {
			console.log('First product:', filteredProducts[0]);
			console.log('Product category:', filteredProducts[0].category);
		}
	}
	
	/**
	 * Add product to cart
	 */
	async function handleAddToCart(product) {
		try {
			await addProductToCart(product, 1, []);
			console.log('Added to cart:', product.name);
		} catch (err) {
			console.error('Error adding to cart:', err);
		}
	}
	
	/**
	 * Component lifecycle
	 */
	onMount(async () => {
		if (browser) {
			// Try to restore tenant/outlet from localStorage
			const savedTenantId = localStorage.getItem('kiosk_tenant_id');
			const savedOutletId = localStorage.getItem('kiosk_outlet_id');
			
			// Load tenants first
			await loadTenants();
			
			// If saved tenant, try to restore
			if (savedTenantId && tenants.length > 0) {
				const tenant = tenants.find(t => t.id == savedTenantId);
				if (tenant) {
					await selectTenant(tenant);
				}
			}
			
			// Add event listeners
			window.addEventListener('online', handleOnline);
			window.addEventListener('offline', handleOffline);
			window.addEventListener('keydown', handleKeyboard);
			
			// Cleanup
			return () => {
				window.removeEventListener('online', handleOnline);
				window.removeEventListener('offline', handleOffline);
				window.removeEventListener('keydown', handleKeyboard);
			};
		}
	});
</script>

<style>
	/* Tenant selection screen */
	.tenant-selection {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	}
	
	.tenant-card {
		background: white;
		border-radius: 1rem;
		padding: 2rem;
		box-shadow: 0 20px 60px rgba(0,0,0,0.3);
		max-width: 500px;
		width: 100%;
	}
	
	.tenant-list {
		display: grid;
		gap: 1rem;
		margin-top: 1.5rem;
	}
	
	.tenant-item {
		padding: 1.5rem;
		border: 2px solid #e2e8f0;
		border-radius: 0.75rem;
		cursor: pointer;
		transition: all 0.2s;
		background: white;
	}
	
	.tenant-item:hover {
		border-color: #667eea;
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
		transform: translateY(-2px);
	}
	
	.outlet-list {
		display: grid;
		gap: 1rem;
		margin-top: 1.5rem;
	}
	
	.outlet-item {
		padding: 1.5rem;
		border: 2px solid #e2e8f0;
		border-radius: 0.75rem;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.outlet-item:hover {
		border-color: #667eea;
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
	}
	
	/* Rest of existing styles... */
	.kiosk-container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background-color: #f7fafc;
	}
	
	/* ... (keep all existing styles) ... */
</style>

<!-- Tenant Selection Screen -->
{#if !selectedTenant && !loading}
<div class="tenant-selection">
	<div class="tenant-card">
		<h1 style="font-size: 2rem; font-weight: bold; text-align: center; margin-bottom: 0.5rem;">
			🏪 Select Restaurant
		</h1>
		<p style="text-align: center; color: #64748b; margin-bottom: 1.5rem;">
			Choose your restaurant to begin
		</p>
		
		<div class="tenant-list">
			{#each tenants as tenant}
			<div class="tenant-item" on:click={() => selectTenant(tenant)}>
				<h3 style="font-weight: 600; font-size: 1.25rem; margin-bottom: 0.25rem;">
					{tenant.name}
				</h3>
				{#if tenant.description}
				<p style="color: #64748b; font-size: 0.875rem;">
					{tenant.description}
				</p>
				{/if}
			</div>
			{/each}
		</div>
	</div>
</div>

<!-- Outlet Selection Screen -->
{:else if selectedTenant && outlets.length > 1 && !selectedOutlet && !loading}
<div class="tenant-selection">
	<div class="tenant-card">
		<button 
			on:click={() => { selectedTenant = null; outlets = []; }}
			style="margin-bottom: 1rem; padding: 0.5rem 1rem; border-radius: 0.5rem; border: 1px solid #cbd5e0;"
		>
			← Back
		</button>
		
		<h1 style="font-size: 2rem; font-weight: bold; text-align: center; margin-bottom: 0.5rem;">
			📍 Select Location
		</h1>
		<p style="text-align: center; color: #64748b; margin-bottom: 1.5rem;">
			{selectedTenant.name}
		</p>
		
		<div class="outlet-list">
			{#each outlets as outlet}
			<div class="outlet-item" on:click={() => selectOutlet(outlet)}>
				<h3 style="font-weight: 600; font-size: 1.25rem; margin-bottom: 0.25rem;">
					{outlet.name}
				</h3>
				<p style="color: #64748b; font-size: 0.875rem;">
					{outlet.address}, {outlet.city}
				</p>
			</div>
			{/each}
		</div>
	</div>
</div>

<!-- Loading Screen -->
{:else if loading}
<div class="tenant-selection">
	<div style="text-align: center;">
		<div style="font-size: 4rem; margin-bottom: 1rem;">⏳</div>
		<h2 style="color: white; font-size: 1.5rem;">Loading...</h2>
	</div>
</div>

<!-- Main Kiosk Screen -->
{:else}
<div class="kiosk-container">
	<!-- Keep all existing kiosk UI here -->
	<!-- Header, Categories, Products, Cart, etc. -->
	<div style="padding: 1rem; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
		<div style="display: flex; justify-content: space-between; align-items: center;">
			<div>
				<h1 style="font-size: 1.5rem; font-weight: bold;">{selectedTenant?.name || 'Kiosk'}</h1>
				{#if selectedOutlet}
				<p style="color: #64748b; font-size: 0.875rem;">{selectedOutlet.name}</p>
				{/if}
			</div>
			<button on:click={() => { selectedTenant = null; selectedOutlet = null; outlets = []; }}>
				Change Location
			</button>
		</div>
	</div>
	
	<!-- Rest of kiosk UI... -->
	<p style="padding: 2rem; text-align: center;">
		Kiosk UI for {selectedTenant.name}
		<br>Categories: {categories.length}
		<br>Products: {products.length}
	</p>
</div>
{/if}
