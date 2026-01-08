<script lang="ts">
	import { multiCart, kioskConfig } from '$lib/stores/kioskStore';
	import { goto } from '$app/navigation';
	import { createEventDispatcher } from 'svelte';
	
	const dispatch = createEventDispatcher();
	
	$: carts = Object.values($multiCart.carts);
	$: totalAmount = $multiCart.totalAmount;
	$: itemsCount = $multiCart.itemsCount;
	
	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
	
	function updateQuantity(outletId: number, itemId: string, newQuantity: number) {
		multiCart.updateQuantity(outletId, itemId, newQuantity);
	}
	
	function removeItem(outletId: number, itemId: string) {
		multiCart.removeItem(outletId, itemId);
	}
	
	function clearOutlet(outletId: number) {
		if (confirm('Remove all items from this restaurant?')) {
			multiCart.clearOutlet(outletId);
		}
	}
	
	function backToOutlets() {
		goto('/kiosk/products');
	}
	
	function proceedToCheckout() {
		goto('/kiosk/checkout');
	}
</script>

<div class="multi-cart">
	<!-- Header -->
	<div class="cart-header">
		<button class="btn-back" on:click={backToOutlets}>
			<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			Back to Restaurants
		</button>
		
		<h1>Your Cart</h1>
		
		<div class="cart-summary-header">
			<span>{itemsCount} items</span>
			<span class="total-amount">{formatCurrency(totalAmount)}</span>
		</div>
	</div>
	
	<!-- Cart Content -->
	<div class="cart-content">
		{#if carts.length === 0}
			<div class="empty-cart">
				<svg class="icon-large" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
						d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
				</svg>
				<h2>Your cart is empty</h2>
				<p>Add items from restaurants to get started</p>
				<button class="btn-primary" on:click={backToOutlets}>
					Browse Restaurants
				</button>
			</div>
		{:else}
			<!-- Cart by Outlet -->
			<div class="outlet-carts">
				{#each carts as cart (cart.outletId)}
					<div class="outlet-cart-section">
						<!-- Outlet Header -->
						<div class="outlet-header" style="border-left-color: {cart.tenantColor}">
							<div class="outlet-title">
								<div 
									class="tenant-badge" 
									style="background-color: {cart.tenantColor}"
								></div>
								<div>
									<h3>{cart.tenantName}</h3>
									<p class="outlet-name">{cart.outletName}</p>
								</div>
							</div>
							
							<button 
								class="btn-clear-outlet"
								on:click={() => clearOutlet(cart.outletId)}
								title="Remove all items from this restaurant"
							>
								<svg class="icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
										d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
								</svg>
							</button>
						</div>
						
						<!-- Items -->
						<div class="cart-items">
							{#each cart.items as item (item.id)}
								<div class="cart-item">
									<div class="item-details">
										<h4>{item.productName}</h4>
										
										{#if item.modifiers && item.modifiers.length > 0}
											<div class="modifiers">
												{#each item.modifiers as mod}
													<span class="modifier-tag">
														+ {mod.name} ({formatCurrency(mod.price)})
													</span>
												{/each}
											</div>
										{/if}
										
										{#if item.notes}
											<p class="item-notes">📝 {item.notes}</p>
										{/if}
										
										<p class="item-price">
											{formatCurrency(item.price + item.modifiersPrice)} × {item.quantity}
										</p>
									</div>
									
									<!-- Quantity Controls -->
									<div class="quantity-controls">
										<button 
											class="btn-qty"
											on:click={() => updateQuantity(cart.outletId, item.id, item.quantity - 1)}
										>
											<svg class="icon-xs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
											</svg>
										</button>
										
										<span class="quantity">{item.quantity}</span>
										
										<button 
											class="btn-qty"
											on:click={() => updateQuantity(cart.outletId, item.id, item.quantity + 1)}
										>
											<svg class="icon-xs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
											</svg>
										</button>
									</div>
									
									<!-- Item Total -->
									<div class="item-total">
										{formatCurrency((item.price + item.modifiersPrice) * item.quantity)}
									</div>
									
									<!-- Remove Button -->
									<button 
										class="btn-remove"
										on:click={() => removeItem(cart.outletId, item.id)}
										title="Remove item"
									>
										<svg class="icon-xs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
										</svg>
									</button>
								</div>
							{/each}
						</div>
						
						<!-- Outlet Summary -->
						<div class="outlet-summary">
							<div class="summary-row">
								<span>Subtotal</span>
								<span>{formatCurrency(cart.subtotal)}</span>
							</div>
							<div class="summary-row">
								<span>Tax ({cart.taxRate}%)</span>
								<span>{formatCurrency(cart.tax)}</span>
							</div>
							<div class="summary-row">
								<span>Service ({cart.serviceChargeRate}%)</span>
								<span>{formatCurrency(cart.serviceCharge)}</span>
							</div>
							<div class="summary-row total">
								<span>Total</span>
								<span>{formatCurrency(cart.total)}</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
	
	<!-- Footer Checkout -->
	{#if carts.length > 0}
		<div class="cart-footer">
			<div class="footer-summary">
				<div class="summary-label">
					<span>{itemsCount} items from {carts.length} restaurant{carts.length > 1 ? 's' : ''}</span>
				</div>
				<div class="summary-total">
					<span class="total-label">Total Payment</span>
					<span class="total-value">{formatCurrency(totalAmount)}</span>
				</div>
			</div>
			
			<button class="btn-checkout" on:click={proceedToCheckout}>
				Proceed to Payment
				<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
				</svg>
			</button>
		</div>
	{/if}
</div>

<style>
	.multi-cart {
		min-height: 100vh;
		background: #f7fafc;
		display: flex;
		flex-direction: column;
	}
	
	.cart-header {
		background: white;
		padding: 1.5rem 2rem;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 2rem;
	}
	
	.btn-back {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		background: none;
		border: none;
		color: #667eea;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		transition: background 0.2s;
	}
	
	.btn-back:hover {
		background: #f7fafc;
	}
	
	h1 {
		font-size: 2rem;
		font-weight: bold;
		color: #1a202c;
		margin: 0;
		flex: 1;
	}
	
	.cart-summary-header {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 0.25rem;
	}
	
	.cart-summary-header span {
		color: #718096;
	}
	
	.total-amount {
		font-size: 1.5rem;
		font-weight: bold;
		color: #667eea !important;
	}
	
	.cart-content {
		flex: 1;
		padding: 2rem;
		max-width: 1200px;
		width: 100%;
		margin: 0 auto;
	}
	
	.empty-cart {
		text-align: center;
		padding: 4rem 2rem;
	}
	
	.empty-cart h2 {
		color: #2d3748;
		margin: 1rem 0 0.5rem;
	}
	
	.empty-cart p {
		color: #718096;
		margin: 0 0 2rem;
	}
	
	.outlet-carts {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}
	
	.outlet-cart-section {
		background: white;
		border-radius: 1rem;
		overflow: hidden;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
	}
	
	.outlet-header {
		padding: 1.5rem;
		border-left: 4px solid #667eea;
		background: #f7fafc;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	
	.outlet-title {
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	
	.tenant-badge {
		width: 50px;
		height: 50px;
		border-radius: 50%;
	}
	
	.outlet-title h3 {
		font-size: 1.25rem;
		font-weight: bold;
		color: #1a202c;
		margin: 0;
	}
	
	.outlet-name {
		color: #718096;
		margin: 0.25rem 0 0;
		font-size: 0.9rem;
	}
	
	.btn-clear-outlet {
		background: none;
		border: none;
		color: #e53e3e;
		cursor: pointer;
		padding: 0.5rem;
		border-radius: 0.5rem;
		transition: background 0.2s;
	}
	
	.btn-clear-outlet:hover {
		background: #fff5f5;
	}
	
	.cart-items {
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	
	.cart-item {
		display: grid;
		grid-template-columns: 1fr auto auto auto;
		gap: 1rem;
		align-items: center;
		padding: 1rem;
		background: #f7fafc;
		border-radius: 0.75rem;
	}
	
	.item-details h4 {
		font-size: 1.1rem;
		font-weight: 600;
		color: #1a202c;
		margin: 0 0 0.5rem;
	}
	
	.modifiers {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}
	
	.modifier-tag {
		font-size: 0.875rem;
		color: #718096;
		background: white;
		padding: 0.25rem 0.5rem;
		border-radius: 0.25rem;
	}
	
	.item-notes {
		color: #718096;
		font-size: 0.875rem;
		margin: 0.5rem 0 0;
	}
	
	.item-price {
		color: #a0aec0;
		font-size: 0.9rem;
		margin: 0.5rem 0 0;
	}
	
	.quantity-controls {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		background: white;
		padding: 0.5rem;
		border-radius: 0.5rem;
	}
	
	.btn-qty {
		width: 32px;
		height: 32px;
		border: 1px solid #e2e8f0;
		background: white;
		border-radius: 0.375rem;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-qty:hover {
		background: #f7fafc;
		border-color: #667eea;
	}
	
	.quantity {
		font-weight: 600;
		min-width: 30px;
		text-align: center;
	}
	
	.item-total {
		font-size: 1.1rem;
		font-weight: 600;
		color: #1a202c;
		min-width: 120px;
		text-align: right;
	}
	
	.btn-remove {
		width: 36px;
		height: 36px;
		border: none;
		background: #fff5f5;
		color: #e53e3e;
		border-radius: 0.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-remove:hover {
		background: #e53e3e;
		color: white;
	}
	
	.outlet-summary {
		padding: 1.5rem;
		border-top: 2px dashed #e2e8f0;
		background: #fafafa;
	}
	
	.summary-row {
		display: flex;
		justify-content: space-between;
		padding: 0.5rem 0;
		color: #4a5568;
	}
	
	.summary-row.total {
		border-top: 2px solid #e2e8f0;
		margin-top: 0.5rem;
		padding-top: 1rem;
		font-size: 1.25rem;
		font-weight: bold;
		color: #1a202c;
	}
	
	.cart-footer {
		background: white;
		padding: 1.5rem 2rem;
		box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 2rem;
	}
	
	.footer-summary {
		flex: 1;
	}
	
	.summary-label {
		color: #718096;
		font-size: 0.9rem;
		margin-bottom: 0.5rem;
	}
	
	.summary-total {
		display: flex;
		align-items: baseline;
		gap: 1rem;
	}
	
	.total-label {
		color: #4a5568;
		font-size: 0.9rem;
	}
	
	.total-value {
		font-size: 2rem;
		font-weight: bold;
		color: #667eea;
	}
	
	.btn-checkout {
		padding: 1.25rem 2.5rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 1rem;
		font-size: 1.25rem;
		font-weight: 600;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		transition: all 0.3s;
		box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
	}
	
	.btn-checkout:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
	}
	
	.btn-primary {
		padding: 1rem 2rem;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 0.75rem;
		font-size: 1.1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-primary:hover {
		background: #5568d3;
		transform: translateY(-2px);
	}
	
	.icon {
		width: 24px;
		height: 24px;
	}
	
	.icon-sm {
		width: 20px;
		height: 20px;
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
</style>
