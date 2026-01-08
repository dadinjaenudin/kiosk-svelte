<script lang="ts">
	import { onMount, createEventDispatcher } from 'svelte';
	import { kioskConfig, multiCart } from '$lib/stores/kioskStore';
	import { goto } from '$app/navigation';
	
	const dispatch = createEventDispatcher();
	
	let outlets: any[] = [];
	let loading = true;
	let error = '';
	
	const API_BASE = 'http://localhost:8001/api';
	
	$: storeCode = $kioskConfig.storeCode;
	$: storeName = $kioskConfig.storeName;
	$: tenantName = $kioskConfig.tenantName;
	$: cartSummary = {
		outlets: Object.keys($multiCart.carts).length,
		items: $multiCart.itemsCount,
		total: $multiCart.totalAmount
	};
	
	onMount(async () => {
		if (!storeCode) {
			error = 'No store configured';
			loading = false;
			return;
		}
		
		await loadOutlets();
	});
	
	async function loadOutlets() {
		loading = true;
		error = '';
		
		try {
			const response = await fetch(
				`${API_BASE}/public/stores/${storeCode}/outlets/`
			);
			
			if (response.ok) {
				const data = await response.json();
				outlets = data.outlets || [];
			} else {
				error = 'Failed to load restaurants';
			}
		} catch (err) {
			error = 'Connection error';
			console.error('Load outlets error:', err);
		} finally {
			loading = false;
		}
	}
	
	function selectOutlet(outlet: any) {
		dispatch('select', outlet);
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
	
	// Check if outlet is open (simplified - you can add time logic)
	function isOutletOpen(outlet: any): boolean {
		// TODO: Check opening_time and closing_time against current time
		return outlet.is_active;
	}
	
	function getOutletStatus(outlet: any): string {
		return isOutletOpen(outlet) ? 'Open Now' : 'Closed';
	}
</script>

<div class="outlet-selection">
	<!-- Header -->
	<div class="header">
		<div class="location-info">
			<div class="location-icon">📍</div>
			<div>
				<h1>Choose Your Restaurant</h1>
				<p class="location-name">{tenantName || ''} - {storeName || 'Loading...'}</p>
			</div>
		</div>
		
		{#if cartSummary.items > 0}
			<button class="cart-btn" on:click={viewCart}>
				<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
						d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
				</svg>
				<div class="cart-badge">
					<span class="cart-count">{cartSummary.items}</span>
					<span class="cart-total">{formatCurrency(cartSummary.total)}</span>
				</div>
			</button>
		{/if}
	</div>
	
	<!-- Outlets Grid -->
	<div class="outlets-container">
		{#if loading}
			<div class="loading-state">
				<div class="spinner-large"></div>
				<p>Loading restaurants...</p>
			</div>
		{:else if error}
			<div class="error-state">
				<svg class="icon-large" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
						d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				<p>{error}</p>
				<button class="btn-retry" on:click={loadOutlets}>Try Again</button>
			</div>
		{:else if outlets.length === 0}
			<div class="empty-state">
				<svg class="icon-large" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
						d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
				</svg>
				<p>No restaurants available</p>
			</div>
		{:else}
			<div class="outlets-grid">
				{#each outlets as outlet (outlet.id)}
					<button 
						class="outlet-card"
						class:closed={!isOutletOpen(outlet)}
						on:click={() => selectOutlet(outlet)}
						disabled={!isOutletOpen(outlet)}
					>
						<!-- Tenant Color Bar -->
						<div 
							class="color-bar" 
							style="background-color: {outlet.tenant.primary_color}"
						></div>
						
						<!-- Logo/Icon -->
						<div class="outlet-logo">
							{#if outlet.tenant.logo}
								<img src={outlet.tenant.logo} alt={outlet.tenant.name} />
							{:else}
								<div 
									class="logo-placeholder"
									style="background: {outlet.tenant.primary_color}"
								>
									{outlet.tenant.name.charAt(0)}
								</div>
							{/if}
						</div>
						
						<!-- Info -->
						<div class="outlet-info">
							<h3>{outlet.brand_name}</h3>
							<p class="outlet-name">{outlet.tenant.name}</p>
							
							<div class="outlet-status">
								<span 
									class="status-badge"
									class:open={isOutletOpen(outlet)}
									class:closed={!isOutletOpen(outlet)}
								>
									{getOutletStatus(outlet)}
								</span>
								
								{#if outlet.opening_time && outlet.closing_time}
									<span class="hours">
										{outlet.opening_time} - {outlet.closing_time}
									</span>
								{/if}
							</div>
							
							<!-- Cart indicator if has items from this outlet -->
							{#if $multiCart.carts[outlet.id]}
								<div class="has-items-indicator">
									<svg class="icon-xs" fill="currentColor" viewBox="0 0 20 20">
										<path d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" />
									</svg>
									{$multiCart.carts[outlet.id].items.length} items
								</div>
							{/if}
						</div>
					</button>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.outlet-selection {
		min-height: 100vh;
		background: #f7fafc;
	}
	
	.header {
		background: white;
		padding: 2rem;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 2rem;
	}
	
	.location-info {
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	
	.location-icon {
		font-size: 3rem;
	}
	
	h1 {
		font-size: 2rem;
		font-weight: bold;
		color: #1a202c;
		margin: 0;
	}
	
	.location-name {
		color: #718096;
		margin: 0.25rem 0 0;
		font-size: 1.1rem;
	}
	
	.cart-btn {
		background: #667eea;
		color: white;
		border: none;
		padding: 1rem 1.5rem;
		border-radius: 1rem;
		display: flex;
		align-items: center;
		gap: 1rem;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.cart-btn:hover {
		background: #5568d3;
		transform: translateY(-2px);
		box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
	}
	
	.cart-badge {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 0.25rem;
	}
	
	.cart-count {
		font-weight: bold;
		font-size: 0.875rem;
	}
	
	.cart-total {
		font-size: 1.1rem;
		font-weight: 600;
	}
	
	.outlets-container {
		padding: 2rem;
		max-width: 1400px;
		margin: 0 auto;
	}
	
	.outlets-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 2rem;
	}
	
	.outlet-card {
		background: white;
		border: 2px solid #e2e8f0;
		border-radius: 1.5rem;
		padding: 0;
		cursor: pointer;
		transition: all 0.3s;
		text-align: left;
		position: relative;
		overflow: hidden;
	}
	
	.outlet-card:hover:not(:disabled) {
		transform: translateY(-8px);
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
		border-color: #667eea;
	}
	
	.outlet-card.closed {
		opacity: 0.6;
		cursor: not-allowed;
	}
	
	.color-bar {
		height: 8px;
		width: 100%;
	}
	
	.outlet-logo {
		padding: 1.5rem 1.5rem 1rem;
		display: flex;
		justify-content: center;
	}
	
	.outlet-logo img {
		width: 120px;
		height: 120px;
		object-fit: contain;
	}
	
	.logo-placeholder {
		width: 120px;
		height: 120px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		font-size: 3rem;
		font-weight: bold;
	}
	
	.outlet-info {
		padding: 1rem 1.5rem 1.5rem;
	}
	
	h3 {
		font-size: 1.5rem;
		font-weight: bold;
		color: #1a202c;
		margin: 0 0 0.25rem;
	}
	
	.outlet-name {
		color: #718096;
		font-size: 1rem;
		margin: 0 0 1rem;
	}
	
	.outlet-status {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex-wrap: wrap;
	}
	
	.status-badge {
		padding: 0.375rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.875rem;
		font-weight: 600;
	}
	
	.status-badge.open {
		background: #c6f6d5;
		color: #22543d;
	}
	
	.status-badge.closed {
		background: #fed7d7;
		color: #742a2a;
	}
	
	.hours {
		color: #718096;
		font-size: 0.875rem;
	}
	
	.has-items-indicator {
		margin-top: 1rem;
		padding: 0.5rem 0.75rem;
		background: #667eea;
		color: white;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}
	
	.loading-state,
	.error-state,
	.empty-state {
		text-align: center;
		padding: 4rem 2rem;
		color: #718096;
	}
	
	.icon {
		width: 24px;
		height: 24px;
	}
	
	.icon-xs {
		width: 16px;
		height: 16px;
	}
	
	.icon-large {
		width: 80px;
		height: 80px;
		color: #cbd5e0;
		margin-bottom: 1rem;
	}
	
	.spinner-large {
		width: 60px;
		height: 60px;
		border: 4px solid #e2e8f0;
		border-top-color: #667eea;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
		margin: 0 auto 1rem;
	}
	
	.btn-retry {
		margin-top: 1rem;
		padding: 0.75rem 1.5rem;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-weight: 600;
		cursor: pointer;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
