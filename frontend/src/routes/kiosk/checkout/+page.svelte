<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import { multiCart, kioskConfig } from '$lib/stores/kioskStore';
	import * as kioskStore from '$lib/stores/kioskStore';
	import { offlineOrderService, validateOrderSnapshot } from '$lib/services/offlineOrderService';
	import { syncService, syncProgress } from '$lib/services/syncService';
	import { networkStatus } from '$lib/services/networkService';
	import { socketService } from '$lib/services/socketService';
	import { ulid } from 'ulid';
	import SyncButton from '$lib/components/SyncButton.svelte';
	
	const API_BASE = 'http://localhost:8001/api';
	
	let customerName = '';
	let customerPhone = '';
	let customerEmail = '';
	let paymentMethod = 'cash';
	let cashAmount = 0;
	let loading = false;
	let error = '';
	let showOfflineSuccess = false;
	let offlineOrderData: any = null;
	
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
		
		// Start auto-sync service
		syncService.startAutoSync();
		console.log('🔄 Sync service started');
	});
	
	async function handleCheckout() {
		console.log('🎯 handleCheckout called');
		console.log('✅ canCheckout:', canCheckout);
		
		if (!canCheckout) {
			console.warn('⚠️ Checkout blocked - canCheckout is false');
			return;
		}
		
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
			
			// Check network status with multiple sources
			// 1. Check browser navigator.onLine (instant, but not 100% reliable)
			// 2. Check networkService status (health check based)
			const navigatorOnline = typeof navigator !== 'undefined' ? navigator.onLine : true;
			const serviceOnline = $networkStatus.isOnline;
			
			// If EITHER says offline, treat as offline (safer approach)
			let isOnline = navigatorOnline && serviceOnline;
			
			console.log(`📡 Network status check:`, {
				navigator: navigatorOnline ? 'Online' : 'Offline',
				service: serviceOnline ? 'Online' : 'Offline',
				final: isOnline ? 'Online' : 'Offline'
			});
			
			if (!isOnline) {
				// OFFLINE MODE: Save to IndexedDB
				console.log('📴 Offline mode detected: Saving order to local storage...');
				
				try {
					// Save the complete checkout data as one offline order
					// Generate ULID (sortable, unique, 128-bit, no collision)
					const orderId = ulid();
					const offlineOrder = {
						order_number: `OFFLINE-${orderId}`,
						checkout_data: checkoutData, // Save complete checkout data for sync
						store_id: checkoutData.store_id,
						customer_name: checkoutData.customer_name,
						customer_phone: checkoutData.customer_phone || '',
						customer_email: checkoutData.customer_email || null,
						payment_method: paymentMethod,
						total_amount: totalAmount,
						subtotal: totalAmount * 0.8, // Rough estimate if not provided
						tenant_id: $kioskConfig.tenantId,
						status: 'pending',
						created_at: new Date().toISOString(),
						synced: false,
						sync_attempts: 0,
						// Extract items for validation (flatten from carts)
						items: checkoutData.carts.flatMap((cart: any) => 
							cart.items.map((item: any) => ({
								product_id: item.product_id,
								product_name: item.product_name,
								price: item.price,
								quantity: item.quantity,
								modifiers: item.modifiers,
								modifiers_price: item.modifiers_price,
								subtotal: item.subtotal
							}))
						)
					};
					
					// ✅ VALIDATE SNAPSHOT INTEGRITY
					const validation = validateOrderSnapshot(offlineOrder);
					if (!validation.valid) {
						console.error('❌ Snapshot validation failed:', validation.errors);
						error = `Order validation failed: ${validation.errors.join(', ')}`;
						return;
					}
					console.log('✅ Snapshot validation passed');
					
					console.log('💾 Saving offline order:', offlineOrder.order_number);
					await offlineOrderService.saveOrder(offlineOrder);
					console.log(`✅ Offline order saved: ${offlineOrder.order_number}`);

					// Broadcast to Local Sync Server for kitchen display
					try {
						socketService.emitToLocal('order:created:offline', {
							order_number: offlineOrder.order_number,
							store_id: offlineOrder.store_id,
							customer_name: offlineOrder.customer_name,
							total_amount: offlineOrder.total_amount,
							payment_method: offlineOrder.payment_method,
							created_at: offlineOrder.created_at,
							status: 'pending'
						});
						console.log('📡 Broadcasted offline order to Local Sync Server');
					} catch (socketError) {
						console.warn('⚠️ Failed to broadcast to Local Sync Server:', socketError);
					}

					// Clear all carts after successful offline order
					multiCart.clearAll();
					console.log('🗑️ Carts cleared after offline order');

					// Show inline success message instead of navigation
					offlineOrderData = {
						orderNumber: offlineOrder.order_number,
						payment: paymentMethod,
						total: totalAmount,
						cashGiven: cashAmount,
						change: changeAmount,
						customerName: customerName,
						customerPhone: customerPhone
					};
					showOfflineSuccess = true;
					
					console.log('✅ Showing inline success message');
					return;
				} catch (offlineError) {
					console.error('❌ Offline order error:', offlineError);
					console.error('❌ Error stack:', offlineError.stack);
					error = `Failed to save offline order: ${offlineError.message}`;
					return;
				}
			}
			
			// ONLINE MODE: Try to send to backend
			console.log('🌐 Online mode: Sending order to backend...');
			
			try {
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
			
			} catch (networkError) {
				// FALLBACK: If online POST fails, save to offline queue
				console.warn('⚠️ Backend request failed, falling back to offline mode');
				console.error('Network error:', networkError);
				
				// Save as offline order
				try {
					const orderId = ulid();
					const offlineOrder = {
						order_number: `OFFLINE-${orderId}`,
						checkout_data: checkoutData,
						store_id: checkoutData.store_id,
						customer_name: checkoutData.customer_name,
						customer_phone: checkoutData.customer_phone || '',
						customer_email: checkoutData.customer_email || null,
						payment_method: paymentMethod,
						total_amount: totalAmount,
						subtotal: totalAmount * 0.8,
						tenant_id: $kioskConfig.tenantId,
						status: 'pending',
						created_at: new Date().toISOString(),
						synced: false,
						sync_attempts: 0,
						items: checkoutData.carts.flatMap((cart: any) => 
							cart.items.map((item: any) => ({
								product_id: item.product_id,
								product_name: item.product_name,
								price: item.price,
								quantity: item.quantity,
								modifiers: item.modifiers,
								modifiers_price: item.modifiers_price,
								subtotal: item.subtotal
							}))
						)
					};
					
					const validation = validateOrderSnapshot(offlineOrder);
					if (!validation.valid) {
						throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
					}
					
					await offlineOrderService.saveOrder(offlineOrder);
					console.log(`✅ Saved as offline order: ${offlineOrder.order_number}`);
					
					// Broadcast to local sync
					socketService.emitToLocal('order:created:offline', {
						order_number: offlineOrder.order_number,
						store_id: offlineOrder.store_id,
						customer_name: offlineOrder.customer_name,
						total_amount: offlineOrder.total_amount,
						payment_method: offlineOrder.payment_method,
						created_at: offlineOrder.created_at,
						status: 'pending'
					});
					
					multiCart.clearAll();
					
					// Show offline success
					offlineOrderData = {
						orderNumber: offlineOrder.order_number,
						payment: paymentMethod,
						total: totalAmount,
						cashGiven: cashAmount,
						change: changeAmount,
						customerName: customerName,
						customerPhone: customerPhone
					};
					showOfflineSuccess = true;
					return;
					
				} catch (offlineSaveError) {
					console.error('❌ Failed to save offline order:', offlineSaveError);
					throw new Error(`Network failed and offline save failed: ${offlineSaveError.message}`);
				}
			}
			
		} catch (err) {
			console.error('❌ Checkout error:', err);
			console.error('❌ Error stack:', err.stack);
			error = err.message || 'Failed to process order';
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

{#if browser}
<div class="checkout-page">
	{#if showOfflineSuccess && offlineOrderData}
		<!-- Offline Success Message -->
		<div class="min-h-screen bg-gradient-to-br from-amber-500 via-orange-500 to-yellow-500 flex items-center justify-center p-4">
			<div class="bg-white rounded-3xl shadow-2xl p-8 max-w-2xl w-full text-center border-4 border-amber-400">
				<!-- Offline Icon (DIFFERENT from online) -->
				<div class="mb-6">
					<div class="w-32 h-32 mx-auto bg-gradient-to-br from-amber-100 to-orange-200 rounded-full flex items-center justify-center animate-pulse">
						<svg class="w-20 h-20 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<!-- Save/Download icon instead of checkmark -->
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
						</svg>
					</div>
				</div>
				
				<!-- WARNING BADGE -->
				<div class="mb-4 inline-block px-6 py-3 bg-amber-100 border-2 border-amber-400 rounded-full">
					<p class="text-xl font-bold text-amber-800">📴 OFFLINE MODE</p>
				</div>
				
				<h1 class="text-4xl font-bold text-amber-700 mb-2">Order Saved Locally! 💾</h1>
				<p class="text-lg text-orange-600 font-semibold mb-6">⏳ Will sync to kitchen when internet returns</p>
				
				<!-- Order Number with Offline Prefix -->
				<div class="bg-amber-50 border-4 border-amber-300 rounded-xl p-4 mb-6">
					<p class="text-sm text-amber-600 font-bold mb-1">📋 LOCAL ORDER NUMBER</p>
					<p class="text-3xl font-bold text-amber-700 font-mono tracking-wider">{offlineOrderData.orderNumber}</p>
					<p class="text-xs text-amber-600 mt-2">🔄 Not synced yet</p>
				</div>
				
				<!-- Customer Info -->
				<div class="bg-blue-50 border-2 border-blue-200 rounded-xl p-4 mb-6 text-left">
					<h3 class="font-bold text-blue-800 text-lg mb-3">Customer</h3>
					<div class="space-y-2">
						<div class="flex justify-between">
							<span class="text-gray-600">Name:</span>
							<span class="font-semibold text-gray-800">{offlineOrderData.customerName}</span>
						</div>
						<div class="flex justify-between">
							<span class="text-gray-600">Phone:</span>
							<span class="font-semibold text-gray-800">{offlineOrderData.customerPhone}</span>
						</div>
					</div>
				</div>
				
				<!-- Payment Details -->
				<div class="bg-amber-50 border-2 border-amber-300 rounded-xl p-6 mb-6">
					<h3 class="font-bold text-amber-800 text-lg mb-4">💳 Payment Details</h3>
					<div class="space-y-3 text-left">
						<div class="flex justify-between items-center py-3 bg-amber-100 rounded-lg px-4">
							<span class="text-amber-700 font-semibold text-lg">Total:</span>
							<span class="font-bold text-amber-700 text-2xl">{formatCurrency(offlineOrderData.total)}</span>
						</div>
						{#if offlineOrderData.payment === 'cash' && offlineOrderData.cashGiven > 0}
							<div class="flex justify-between items-center py-2">
								<span class="text-gray-600">Cash Given:</span>
								<span class="font-semibold text-gray-800 text-lg">{formatCurrency(offlineOrderData.cashGiven)}</span>
							</div>
							<div class="flex justify-between items-center py-3 bg-orange-100 rounded-lg px-4">
								<span class="text-orange-700 font-semibold text-lg">Change:</span>
								<span class="font-bold text-orange-700 text-2xl">{formatCurrency(offlineOrderData.change)}</span>
							</div>
						{/if}
					</div>
				</div>
				
				<!-- Info -->
				<div class="bg-orange-50 border-2 border-orange-400 rounded-xl p-6 mb-6 text-left">
					<div class="flex items-center mb-3">
						<span class="text-2xl mr-2">⚠️</span>
						<h3 class="font-bold text-orange-800 text-lg">IMPORTANT: This order is NOT synced yet!</h3>
					</div>
					<ul class="space-y-3 text-gray-700">
						<li class="flex items-start">
							<span class="text-orange-600 mr-2 text-lg flex-shrink-0">💾</span>
							<span><strong>Order saved to this device only</strong> (not in kitchen yet)</span>
						</li>
						<li class="flex items-start">
							<span class="text-orange-600 mr-2 text-lg flex-shrink-0">🔄</span>
							<span><strong>Will auto-sync to kitchen</strong> when internet connection returns</span>
						</li>
						<li class="flex items-start">
							<span class="text-orange-600 mr-2 text-lg flex-shrink-0">🔔</span>
							<span><strong>You'll get notification</strong> when order successfully sent to kitchen</span>
						</li>
						<li class="flex items-start">
							<span class="text-orange-600 mr-2 text-lg flex-shrink-0">⏳</span>
							<span><strong>Kitchen will start preparing</strong> only after sync completes</span>
						</li>
					</ul>
				</div>
				
				<!-- Action Button -->
				<button
					on:click={() => goto('/kiosk/products')}
					class="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-bold py-5 px-8 rounded-xl text-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
				>
					🏠 Back to Menu
				</button>
				
				<!-- Bottom Warning -->
				<div class="mt-6 bg-yellow-50 border-2 border-yellow-400 rounded-lg p-4">
					<p class="text-sm text-yellow-800 font-semibold">
						⚡ Please keep internet connection stable for automatic sync!
					</p>
				</div>
			</div>
		</div>
	{:else}
	<div class="checkout-container">
		<!-- Header -->
		<div class="checkout-header">
			<button class="btn-back" on:click={backToCart}>
				<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
				</svg>
			</button>
			<h1>Checkout</h1>
			<div class="sync-button-container">
				<SyncButton size="md" variant="outline" />
			</div>
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
	{/if}
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
{:else}
<div class="checkout-page" style="display: flex; justify-content: center; align-items: center; min-height: 100vh;">
	<div class="spinner-small"></div>
</div>
{/if}
