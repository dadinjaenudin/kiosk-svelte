<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { navigationStore, showBackButton, sessionManager } from '$lib/stores/navigationStore';
	import { kioskConfig } from '$lib/stores/kioskStore';
	
	$: currentPath = $page.url.pathname;
	$: breadcrumbs = $navigationStore.breadcrumbs;
	$: canGoBack = $showBackButton;
	
	// Calculate total cart items from kioskConfig
	$: totalCartItems = Object.values($kioskConfig.carts || {}).reduce((sum, cart: any) => {
		return sum + (cart.items?.reduce((itemSum: number, item: any) => itemSum + (item.quantity || 0), 0) || 0);
	}, 0);
	
	// Update navigation store when path changes
	$: navigationStore.setCurrentPath(currentPath);
	$: navigationStore.setCartItemCount(totalCartItems);
	
	onMount(() => {
		// Initialize session tracking
		sessionManager.initialize();
		
		// Listen for clear session event
		const handleClearSession = () => {
			// Clear carts from kioskConfig
			kioskConfig.update(cfg => ({ ...cfg, carts: {} }));
			navigationStore.reset();
		};
		
		window.addEventListener('clear-session', handleClearSession);
		
		return () => {
			window.removeEventListener('clear-session', handleClearSession);
		};
	});
	
	function handleBack() {
		navigationStore.goBack(totalCartItems);
	}
	
	function goToCart() {
		goto('/kiosk/cart');
	}
	
	function navigateTo(path: string) {
		goto(path);
	}
	
	// Don't show header on idle screen
	$: showHeader = !currentPath.includes('/idle');
</script>

{#if showHeader}
	<header class="kiosk-header">
		<div class="header-container">
			<!-- Left: Back button & Breadcrumbs -->
			<div class="header-left">
				{#if canGoBack}
					<button class="back-button" on:click={handleBack} aria-label="Go back">
						<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M19 12H5M12 19l-7-7 7-7"/>
						</svg>
						<span class="back-text">Back</span>
					</button>
				{/if}
				
				<nav class="breadcrumbs" aria-label="Breadcrumb">
					{#each breadcrumbs as crumb, index}
						{#if index > 0}
							<span class="separator">/</span>
						{/if}
						<button
							class="breadcrumb-item"
							class:current={index === breadcrumbs.length - 1}
							on:click={() => navigateTo(crumb.path)}
							disabled={index === breadcrumbs.length - 1}
						>
							{crumb.label}
						</button>
					{/each}
				</nav>
			</div>
			
			<!-- Center: Store Info -->
			<div class="header-center">
				<h1 class="store-name">{$kioskConfig.storeName || 'Kiosk'}</h1>
				{#if $kioskConfig.tenantName}
					<p class="tenant-name">{$kioskConfig.tenantName}</p>
				{/if}
			</div>
			
			<!-- Right: Cart Badge -->
			<div class="header-right">
				<button class="cart-button" on:click={goToCart} aria-label="View cart">
					<svg class="cart-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="9" cy="21" r="1"/>
						<circle cx="20" cy="21" r="1"/>
						<path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
					</svg>
					{#if totalCartItems > 0}
						<span class="cart-badge">{totalCartItems}</span>
					{/if}
				</button>
			</div>
		</div>
	</header>
{/if}

<style>
	.kiosk-header {
		position: sticky;
		top: 0;
		z-index: 50;
		background: white;
		border-bottom: 2px solid #e5e7eb;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	}
	
	.header-container {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		align-items: center;
		gap: 1rem;
		max-width: 1400px;
		margin: 0 auto;
		padding: 1rem 1.5rem;
	}
	
	/* Left Section */
	.header-left {
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	
	.back-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: #f3f4f6;
		border: none;
		border-radius: 0.5rem;
		font-size: 1rem;
		font-weight: 500;
		color: #374151;
		cursor: pointer;
		transition: all 0.2s ease;
		min-height: 44px; /* Touch-friendly */
	}
	
	.back-button:hover {
		background: #e5e7eb;
	}
	
	.back-button:active {
		transform: scale(0.98);
	}
	
	.back-button .icon {
		width: 20px;
		height: 20px;
	}
	
	.breadcrumbs {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	
	.separator {
		color: #9ca3af;
		font-size: 0.875rem;
	}
	
	.breadcrumb-item {
		padding: 0.25rem 0.5rem;
		background: none;
		border: none;
		font-size: 0.875rem;
		color: #6b7280;
		cursor: pointer;
		transition: color 0.2s ease;
		border-radius: 0.25rem;
	}
	
	.breadcrumb-item:not(.current):hover {
		color: #374151;
		background: #f3f4f6;
	}
	
	.breadcrumb-item.current {
		color: #1f2937;
		font-weight: 600;
		cursor: default;
	}
	
	/* Center Section */
	.header-center {
		text-align: center;
	}
	
	.store-name {
		font-size: 1.5rem;
		font-weight: 700;
		color: #1f2937;
		margin: 0;
		line-height: 1.2;
	}
	
	.tenant-name {
		font-size: 0.875rem;
		color: #6b7280;
		margin: 0.25rem 0 0 0;
	}
	
	/* Right Section */
	.header-right {
		display: flex;
		justify-content: flex-end;
	}
	
	.cart-button {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 56px;
		height: 56px;
		background: #667eea;
		border: none;
		border-radius: 50%;
		cursor: pointer;
		transition: all 0.2s ease;
		box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
	}
	
	.cart-button:hover {
		background: #5a67d8;
		transform: scale(1.05);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
	}
	
	.cart-button:active {
		transform: scale(0.98);
	}
	
	.cart-icon {
		width: 28px;
		height: 28px;
		color: white;
	}
	
	.cart-badge {
		position: absolute;
		top: -4px;
		right: -4px;
		display: flex;
		align-items: center;
		justify-content: center;
		min-width: 24px;
		height: 24px;
		padding: 0 6px;
		background: #ef4444;
		color: white;
		font-size: 0.75rem;
		font-weight: 700;
		border-radius: 12px;
		border: 2px solid white;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
	}
	
	/* Responsive */
	@media (max-width: 768px) {
		.header-container {
			grid-template-columns: 1fr;
			gap: 0.75rem;
			padding: 0.75rem 1rem;
		}
		
		.header-left {
			order: 2;
			justify-content: flex-start;
		}
		
		.header-center {
			order: 1;
		}
		
		.header-right {
			position: fixed;
			bottom: 1rem;
			right: 1rem;
			z-index: 100;
		}
		
		.cart-button {
			width: 64px;
			height: 64px;
			box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
		}
		
		.cart-icon {
			width: 32px;
			height: 32px;
		}
		
		.back-text {
			display: none;
		}
		
		.breadcrumbs {
			display: none; /* Hide breadcrumbs on mobile, show only back button */
		}
		
		.store-name {
			font-size: 1.25rem;
		}
		
		.tenant-name {
			font-size: 0.75rem;
		}
	}
	
	@media (max-width: 480px) {
		.header-container {
			padding: 0.5rem 0.75rem;
		}
		
		.store-name {
			font-size: 1.125rem;
		}
	}
</style>
