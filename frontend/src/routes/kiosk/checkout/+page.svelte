<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { multiCart, kioskConfig } from '$lib/stores/kioskStore';
	
	const API_BASE = 'http://localhost:8001/api';
	
	let customerName = '';
	let customerPhone = '';
	let customerEmail = '';
	let paymentMethod = 'cash';
	let cashAmount = 0;
	let loading = false;
	let error = '';
	
	$: carts = Object.values($multiCart.carts);
	$: totalAmount = $multiCart.totalAmount;
	$: changeAmount = cashAmount - totalAmount;
	$: isCashPayment = paymentMethod === 'cash';
	$: cashValid = !isCashPayment || (isCashPayment && cashAmount >= totalAmount);
	$: canCheckout = customerName.trim().length > 0 && customerPhone.trim().length > 0 && carts.length > 0 && cashValid;
	
	// Debug
	$: console.log('Checkout validation:', {
		name: customerName,
		phone: customerPhone,
		carts: carts.length,
		paymentMethod,
		cashAmount,
		totalAmount,
		cashValid,
		canCheckout,
		tenantId: $kioskConfig.tenantId
	});
	
	onMount(() => {
		if (carts.length === 0) {
			goto('/kiosk');
		}
		
		// Check if tenantId is missing
		if (!$kioskConfig.tenantId) {
			console.warn('⚠️ Tenant ID is missing! Please reconfigure kiosk.');
			error = 'Kiosk configuration incomplete. Please setup again.';
		}
	});
	
	async function handleCheckout() {
		if (!canCheckout) return;
		
		// Validate tenantId exists
		if (!$kioskConfig.tenantId) {
			error = 'Kiosk not properly configured. Please go to setup and enter store code again.';
			console.error('❌ Tenant ID missing in config:', $kioskConfig);
			return;
		}
		
		loading = true;
		error = '';
		
		try {
			// Prepare checkout data
			const checkoutTemplate = multiCart.getCheckoutData();
			const checkoutData = {
				...checkoutTemplate,
				customer_name: customerName,
				customer_phone: customerPhone,
				customer_email: customerEmail || null
			};
			
			console.log('🛒 Checkout data:', JSON.stringify(checkoutData, null, 2));
			console.log('📍 Store ID:', checkoutData.store_id);
			console.log('🛒 Carts:', checkoutData.carts.length);
			
			// Validate required fields
			if (!checkoutData.store_id) {
				throw new Error('Store ID is missing. Please reconfigure kiosk.');
			}
			if (!checkoutData.carts || checkoutData.carts.length === 0) {
				throw new Error('Cart is empty');
			}
			
			// Create order group
			const response = await fetch(`${API_BASE}/order-groups/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Tenant-ID': $kioskConfig.tenantId?.toString() || ''
				},
				body: JSON.stringify(checkoutData)
			});
			
			if (!response.ok) {
				const errorData = await response.json();
				console.error('❌ Backend error:', errorData);
				throw new Error(errorData.message || errorData.detail || JSON.stringify(errorData));
			}
			
			const orderGroup = await response.json();
			console.log('✅ Order group created:', orderGroup.group_number);
			
			// Mark as paid
			const paymentResponse = await fetch(
				`${API_BASE}/order-groups/${orderGroup.group_number}/mark-paid/`,
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						'X-Tenant-ID': $kioskConfig.tenantId?.toString() || ''
					},
					body: JSON.stringify({ payment_method: paymentMethod })
				}
			);
			
			if (!paymentResponse.ok) {
				throw new Error('Failed to process payment');
			}
			
			const paymentResult = await paymentResponse.json();
			console.log('💰 Payment successful');
			
			// Clear cart
			multiCart.clearAll();
			
			// Navigate to success page
			goto(`/kiosk/success/${orderGroup.group_number}`);
			
		} catch (err) {
			error = err.message || 'Failed to process order';
			console.error('Checkout error:', err);
		} finally {
			loading = false;
		}
	}
	
	function generateSessionId(): string {
		return `SESS-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
	}
	
	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
	
	function backToCart() {
		goto('/kiosk/cart');
	}
	
	function forceSetup() {
		// Clear configuration to trigger setup form
		kioskConfig.reset();
		goto('/kiosk');
	}
</script>

<div class="checkout-page">
	<div class="checkout-container">
		<!-- Header -->
		<div class="checkout-header">
			<button class="btn-back" on:click={backToCart}>
				<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
				</svg>
			</button>
			<h1>Checkout</h1>
		</div>
		
		<!-- Customer Info Form -->
		<div class="form-section">
			<h2>Contact Information</h2>
			
			<div class="form-group">
				<label for="name">Name *</label>
				<input
					id="name"
					type="text"
					bind:value={customerName}
					placeholder="Enter your name"
					required
					disabled={loading}
				/>
			</div>
			
			<div class="form-group">
				<label for="phone">Phone Number *</label>
				<input
					id="phone"
					type="tel"
					bind:value={customerPhone}
					placeholder="08xxxxxxxxxx"
					required
					disabled={loading}
				/>
			</div>
			
			<div class="form-group">
				<label for="email">Email (optional)</label>
				<input
					id="email"
					type="email"
					bind:value={customerEmail}
					placeholder="your@email.com"
					disabled={loading}
				/>
			</div>
		</div>
		
		<!-- Payment Method -->
		<div class="form-section">
			<h2>Payment Method</h2>
			
			<div class="payment-methods">
				<label class="payment-method" class:selected={paymentMethod === 'cash'}>
					<input
						type="radio"
						name="payment"
						value="cash"
						bind:group={paymentMethod}
						disabled={loading}
					/>
					<div class="payment-method-content">
						<span class="payment-icon">💵</span>
						<span>Cash</span>
					</div>
				</label>
				
				<label class="payment-method" class:selected={paymentMethod === 'card'}>
					<input
						type="radio"
						name="payment"
						value="card"
						bind:group={paymentMethod}
						disabled={loading}
					/>
					<div class="payment-method-content">
						<span class="payment-icon">💳</span>
						<span>Card</span>
					</div>
				</label>
				
				<label class="payment-method" class:selected={paymentMethod === 'qris'}>
					<input
						type="radio"
						name="payment"
						value="qris"
						bind:group={paymentMethod}
						disabled={loading}
					/>
					<div class="payment-method-content">
						<span class="payment-icon">📱</span>
						<span>QRIS</span>
					</div>
				</label>
				
				<label class="payment-method" class:selected={paymentMethod === 'ewallet'}>
					<input
						type="radio"
						name="payment"
						value="ewallet"
						bind:group={paymentMethod}
						disabled={loading}
					/>
					<div class="payment-method-content">
						<span class="payment-icon">📲</span>
						<span>E-Wallet</span>
					</div>
				</label>
			</div>
			
			<!-- Cash Amount Input (only show if cash selected) -->
			{#if paymentMethod === 'cash'}
				<div class="cash-payment-section">
					<div class="form-group">
						<label for="cashAmount">Cash Amount *</label>
						<input
							id="cashAmount"
							type="number"
							bind:value={cashAmount}
							placeholder="Enter cash amount"
							min={totalAmount}
							step="1000"
							disabled={loading}
							class="cash-input"
						/>
					</div>
					
					<div class="total-display">
						<div class="total-row">
							<span>Total to Pay:</span>
							<span class="total-amount">{formatCurrency(totalAmount)}</span>
						</div>
						{#if cashAmount > 0}
							<div class="total-row">
								<span>Cash Given:</span>
								<span class="cash-given">{formatCurrency(cashAmount)}</span>
							</div>
							{#if changeAmount >= 0}
								<div class="total-row change-row">
									<span>Change:</span>
									<span class="change-amount">{formatCurrency(changeAmount)}</span>
								</div>
							{:else}
								<div class="total-row insufficient-row">
									<span>Insufficient:</span>
									<span class="insufficient-amount">{formatCurrency(Math.abs(changeAmount))}</span>
								</div>
							{/if}
						{/if}
					</div>
					
					<!-- Quick Amount Buttons -->
					<div class="quick-amounts">
						<button 
							type="button"
							class="btn-quick-amount" 
							on:click={() => cashAmount = totalAmount}
							disabled={loading}
						>
							Exact Amount
						</button>
						<button 
							type="button"
							class="btn-quick-amount" 
							on:click={() => cashAmount = Math.ceil(totalAmount / 50000) * 50000}
							disabled={loading}
						>
							{formatCurrency(Math.ceil(totalAmount / 50000) * 50000)}
						</button>
						<button 
							type="button"
							class="btn-quick-amount" 
							on:click={() => cashAmount = Math.ceil(totalAmount / 100000) * 100000}
							disabled={loading}
						>
							{formatCurrency(Math.ceil(totalAmount / 100000) * 100000)}
						</button>
					</div>
				</div>
			{/if}
		</div>
		
		<!-- Order Summary -->
		<div class="form-section">
			<h2>Order Summary</h2>
			
			<div class="order-summary">
				{#each carts as cart (cart.outletId)}
					<div class="summary-outlet">
						<div class="summary-outlet-header">
							<div 
								class="outlet-badge" 
								style="background-color: {cart.tenantColor}"
							></div>
							<div>
								<h4>{cart.tenantName}</h4>
								<p>{cart.outletName}</p>
							</div>
						</div>
						
						<div class="summary-items">
							{#each cart.items as item}
								<div class="summary-item">
									<span>{item.quantity}x {item.productName}</span>
									<span>{formatCurrency((item.price + item.modifiersPrice) * item.quantity)}</span>
								</div>
							{/each}
						</div>
						
						<div class="summary-subtotal">
							<span>Subtotal</span>
							<span>{formatCurrency(cart.subtotal)}</span>
						</div>
						
						{#if cart.tax > 0}
							<div class="summary-row">
								<span>Tax ({cart.taxRate * 100}%)</span>
								<span>{formatCurrency(cart.tax)}</span>
							</div>
						{/if}
						
						{#if cart.serviceCharge > 0}
							<div class="summary-row">
								<span>Service ({cart.serviceChargeRate * 100}%)</span>
								<span>{formatCurrency(cart.serviceCharge)}</span>
							</div>
						{/if}
						
						<div class="summary-total">
							<span>Total</span>
							<span>{formatCurrency(cart.total)}</span>
						</div>
					</div>
				{/each}
				
				<div class="grand-total">
					<span>Grand Total</span>
					<span>{formatCurrency(totalAmount)}</span>
				</div>
			</div>
		</div>
		
		{#if error}
			<div class="error-alert">
				⚠️ {error}
				{#if !$kioskConfig.tenantId}
					<button class="btn-setup" on:click={forceSetup}>
						Go to Setup
					</button>
				{/if}
			</div>
		{/if}
		
		<!-- Checkout Button -->
		<button
			class="btn-checkout"
			disabled={!canCheckout || loading}
			on:click={handleCheckout}
		>
			{#if loading}
				<span class="spinner-small"></span>
				Processing...
			{:else}
				Pay {formatCurrency(totalAmount)}
			{/if}
		</button>
	</div>
</div>

<style>
	.checkout-page {
		min-height: 100vh;
		background: #f5f5f5;
		padding: 20px;
	}
	
	.checkout-container {
		max-width: 800px;
		margin: 0 auto;
	}
	
	.checkout-header {
		background: white;
		padding: 16px 20px;
		border-radius: 12px;
		display: flex;
		align-items: center;
		gap: 16px;
		margin-bottom: 20px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
	
	.checkout-header h1 {
		font-size: 24px;
		font-weight: 700;
		margin: 0;
		color: #1a1a1a;
	}
	
	.form-section {
		background: white;
		padding: 24px;
		border-radius: 12px;
		margin-bottom: 20px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}
	
	.form-section h2 {
		font-size: 18px;
		font-weight: 600;
		margin: 0 0 20px 0;
		color: #1a1a1a;
	}
	
	.form-group {
		margin-bottom: 16px;
	}
	
	.form-group:last-child {
		margin-bottom: 0;
	}
	
	.form-group label {
		display: block;
		font-size: 14px;
		font-weight: 500;
		color: #333;
		margin-bottom: 8px;
	}
	
	.form-group input {
		width: 100%;
		padding: 12px 16px;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		font-size: 16px;
		color: #1a1a1a;
		transition: border-color 0.2s;
	}
	
	.form-group input:focus {
		outline: none;
		border-color: #667eea;
	}
	
	.form-group input:disabled {
		background: #f5f5f5;
		cursor: not-allowed;
	}
	
	.payment-methods {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 12px;
	}
	
	.payment-method {
		position: relative;
		display: block;
		cursor: pointer;
	}
	
	.payment-method input[type="radio"] {
		position: absolute;
		opacity: 0;
		width: 0;
		height: 0;
	}
	
	.payment-method-content {
		border: 2px solid #e0e0e0;
		border-radius: 12px;
		padding: 20px;
		text-align: center;
		transition: all 0.2s;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
	}
	
	.payment-method.selected .payment-method-content {
		border-color: #667eea;
		background: #f0f3ff;
	}
	
	.payment-method:hover .payment-method-content {
		border-color: #667eea;
	}
	
	.payment-icon {
		font-size: 32px;
	}
	
	/* Cash Payment Section */
	.cash-payment-section {
		margin-top: 24px;
		padding-top: 24px;
		border-top: 1px solid #e0e0e0;
	}
	
	.cash-input {
		font-size: 24px !important;
		font-weight: 600;
		text-align: right;
		padding: 16px !important;
	}
	
	.total-display {
		background: #f8f9ff;
		border: 2px solid #e0e7ff;
		border-radius: 12px;
		padding: 20px;
		margin-top: 16px;
	}
	
	.total-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 0;
		font-size: 16px;
	}
	
	.total-amount {
		font-size: 20px;
		font-weight: 700;
		color: #667eea;
	}
	
	.cash-given {
		font-size: 18px;
		font-weight: 600;
		color: #333;
	}
	
	.change-row {
		margin-top: 8px;
		padding-top: 12px;
		border-top: 2px solid #667eea;
	}
	
	.change-amount {
		font-size: 24px;
		font-weight: 700;
		color: #10b981;
	}
	
	.insufficient-row {
		margin-top: 8px;
		padding-top: 12px;
		border-top: 2px solid #ef4444;
	}
	
	.insufficient-amount {
		font-size: 20px;
		font-weight: 700;
		color: #ef4444;
	}
	
	.quick-amounts {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 12px;
		margin-top: 16px;
	}
	
	.btn-quick-amount {
		padding: 12px 16px;
		background: white;
		border: 2px solid #667eea;
		color: #667eea;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-quick-amount:hover:not(:disabled) {
		background: #667eea;
		color: white;
		transform: translateY(-2px);
	}
	
	.btn-quick-amount:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
	
	.order-summary {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}
	
	.summary-outlet {
		border: 1px solid #e0e0e0;
		border-radius: 12px;
		padding: 16px;
		background: #fafafa;
	}
	
	.summary-outlet-header {
		display: flex;
		align-items: center;
		gap: 12px;
		margin-bottom: 16px;
		padding-bottom: 12px;
		border-bottom: 1px solid #e0e0e0;
	}
	
	.outlet-badge {
		width: 8px;
		height: 40px;
		border-radius: 4px;
	}
	
	.summary-outlet-header h4 {
		font-size: 16px;
		font-weight: 600;
		margin: 0;
		color: #1a1a1a;
	}
	
	.summary-outlet-header p {
		font-size: 14px;
		color: #666;
		margin: 0;
	}
	
	.summary-items {
		margin-bottom: 12px;
	}
	
	.summary-item {
		display: flex;
		justify-content: space-between;
		padding: 6px 0;
		font-size: 14px;
		color: #666;
	}
	
	.summary-row, .summary-subtotal, .summary-total {
		display: flex;
		justify-content: space-between;
		padding: 8px 0;
		font-size: 14px;
	}
	
	.summary-subtotal {
		border-top: 1px solid #e0e0e0;
		padding-top: 12px;
		margin-top: 12px;
		font-weight: 600;
		color: #333;
	}
	
	.summary-row {
		color: #666;
	}
	
	.summary-total {
		border-top: 2px solid #e0e0e0;
		padding-top: 12px;
		margin-top: 8px;
		font-size: 16px;
		font-weight: 700;
		color: #1a1a1a;
	}
	
	.grand-total {
		display: flex;
		justify-content: space-between;
		padding: 20px;
		background: #667eea;
		color: white;
		border-radius: 12px;
		font-size: 20px;
		font-weight: 700;
	}
	
	.error-alert {
		background: #fee;
		color: #c00;
		padding: 16px;
		border-radius: 8px;
		margin-bottom: 20px;
		text-align: center;
		display: flex;
		flex-direction: column;
		gap: 12px;
		align-items: center;
	}
	
	.btn-setup {
		padding: 10px 20px;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-setup:hover {
		background: #5568d3;
	}
	
	.btn-checkout {
		width: 100%;
		padding: 18px;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 12px;
		font-size: 18px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.3s;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 12px;
	}
	
	.btn-checkout:hover:not(:disabled) {
		background: #5568d3;
		transform: translateY(-2px);
		box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
	}
	
	.btn-checkout:disabled {
		background: #ccc;
		cursor: not-allowed;
	}
	
	.spinner-small {
		width: 20px;
		height: 20px;
		border: 3px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
