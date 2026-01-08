<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { kioskConfig } from '$lib/stores/kioskStore';
	
	const API_BASE = 'http://localhost:8001/api';
	
	let groupNumber: string;
	let orderGroup: any = null;
	let loading = true;
	let error = '';
	let countdown = 10;
	
	$: groupNumber = $page.params.groupNumber;
	
	onMount(async () => {
		await loadReceipt();
		startCountdown();
	});
	
	async function loadReceipt() {
		try {
			const tenantId = $kioskConfig.tenantId?.toString() || '';
			console.log('🏪 Loading receipt with tenant ID:', tenantId);
			console.log('📋 Kiosk config:', $kioskConfig);
			
			const response = await fetch(
				`${API_BASE}/order-groups/${groupNumber}/receipt/`,
				{
					headers: {
						'X-Tenant-ID': tenantId
					}
				}
			);
			
			if (response.ok) {
				orderGroup = await response.json();
				console.log('📄 Receipt loaded:', orderGroup);			console.log('📍 Location:', orderGroup.location);
			console.log('👤 Customer:', orderGroup.customer);
			console.log('💳 Payment:', orderGroup.payment);
			console.log('📦 Orders:', orderGroup.orders);			} else {
				const errorText = await response.text();
				console.error('❌ Receipt error:', response.status, errorText);
				error = 'Failed to load receipt';
			}
		} catch (err) {
			error = 'Connection error';
			console.error('Load receipt error:', err);
		} finally {
			loading = false;
		}
	}
	
	function startCountdown() {
		const interval = setInterval(() => {
			countdown--;
			if (countdown <= 0) {
				clearInterval(interval);
				startNewOrder();
			}
		}, 1000);
	}
	
	function startNewOrder() {
		goto('/kiosk');
	}
	
	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
	
	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleString('id-ID', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
	
	function printReceipt() {
		window.print();
	}
</script>

<div class="success-page">
	<div class="success-container">
		{#if loading}
			<div class="loading">
				<div class="spinner"></div>
				<p>Loading receipt...</p>
			</div>
		{:else if error}
			<div class="error">
				<p>⚠️ {error}</p>
				<button class="btn-primary" on:click={startNewOrder}>
					Start New Order
				</button>
			</div>
		{:else if orderGroup}
			<!-- Success Animation -->
			<div class="success-icon">
				<svg class="checkmark" viewBox="0 0 52 52">
					<circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
					<path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
				</svg>
			</div>
			
			<h1>Order Successful!</h1>
			<p class="subtitle">Your order has been placed and sent to the kitchen.</p>
			
			<!-- Receipt -->
			<div class="receipt">
				<div class="receipt-header">
					<h2>Order Receipt</h2>
					<p class="group-number">{orderGroup.group_number}</p>
				<p class="location-name">{orderGroup.location?.name || 'N/A'}</p>
				<p class="date">{formatDate(orderGroup.created_at)}</p>
			</div>
			
			<div class="receipt-customer">
				<h3>Customer Information</h3>
				<p><strong>Name:</strong> {orderGroup.customer?.name || 'N/A'}</p>
				<p><strong>Phone:</strong> {orderGroup.customer?.phone || 'N/A'}</p>
				{#if orderGroup.customer?.email}
					<p><strong>Email:</strong> {orderGroup.customer.email}</p>
				{/if}
			</div>			
			<!-- Orders by Outlet -->
			<div class="receipt-orders">
				{#each orderGroup.orders as order}
					<div class="order-section">							<div class="order-header">
								<div>
								<h3>{order.tenant || 'N/A'}</h3>
								<p class="outlet-name">{order.outlet || 'N/A'}</p>
								<p class="order-number">{order.order_number}</p>
							</div>
							</div>
							
							<div class="order-items">
								{#each order.items as item}
									<div class="receipt-item">
										<div class="item-info">
											<span class="item-qty">{item.quantity}x</span>
											<div>
												<p class="item-name">{item.name}</p>
												{#if item.modifiers && item.modifiers.length > 0}
													<div class="item-modifiers">
														{#each item.modifiers as mod}
															<span>+ {mod.name}</span>
														{/each}
													</div>
												{/if}
												{#if item.notes}
													<p class="item-notes">📝 {item.notes}</p>
												{/if}
											</div>
										</div>
										<span class="item-price">
											{formatCurrency(item.total)}
										</span>
									</div>
								{/each}
							</div>
							
							<div class="order-summary">
								<div class="summary-row">
									<span>Subtotal</span>
									<span>{formatCurrency(order.subtotal)}</span>
								</div>
								{#if order.tax > 0}
									<div class="summary-row">
										<span>Tax</span>
										<span>{formatCurrency(order.tax)}</span>
									</div>
								{/if}
								{#if order.service_charge > 0}
									<div class="summary-row">
										<span>Service</span>
										<span>{formatCurrency(order.service_charge)}</span>
									</div>
								{/if}
								<div class="summary-total">
									<span>Total</span>
									<span>{formatCurrency(order.total)}</span>
								</div>
							</div>
						</div>
					{/each}

				<!-- Grand Total -->
				<div class="grand-total">
					<p><strong>Grand Total:</strong> <span class="total-amount">{formatCurrency(orderGroup.payment?.total || 0)}</span></p>
				</div>

				<!-- Payment Info -->
				<div class="payment-info">
					<p><strong>Payment Method:</strong> {orderGroup.payment?.method?.toUpperCase() || 'N/A'}</p>
					<p><strong>Status:</strong> <span class="status-paid">{orderGroup.payment?.status?.toUpperCase() || 'PAID'}</span></p>
				</div>
			</div> <!-- End receipt-orders -->
		</div> <!-- End receipt -->

		<!-- Action Buttons -->
			<div class="actions">
				<button class="btn-secondary" on:click={printReceipt}>
					🖨️ Print Receipt
				</button>
				<button class="btn-primary" on:click={startNewOrder}>
					Start New Order ({countdown}s)
				</button>
			</div>
			
			<p class="thank-you">Thank you for your order! 🎉</p>
		{/if}
	</div>
</div>

<style>
	.success-page {
		min-height: 100vh;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 20px;
	}
	
	.success-container {
		max-width: 600px;
		width: 100%;
		text-align: center;
	}
	
	.loading, .error {
		background: white;
		padding: 40px;
		border-radius: 16px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
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
	
	.success-icon {
		margin-bottom: 24px;
	}
	
	.checkmark {
		width: 100px;
		height: 100px;
		margin: 0 auto;
		display: block;
	}
	
	.checkmark-circle {
		stroke: #4caf50;
		stroke-width: 2;
		stroke-dasharray: 166;
		stroke-dashoffset: 166;
		animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
	}
	
	.checkmark-check {
		stroke: #4caf50;
		stroke-width: 3;
		stroke-linecap: round;
		stroke-dasharray: 48;
		stroke-dashoffset: 48;
		animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
	}
	
	@keyframes stroke {
		100% {
			stroke-dashoffset: 0;
		}
	}
	
	h1 {
		font-size: 32px;
		font-weight: 700;
		color: white;
		margin: 0 0 12px 0;
	}
	
	.subtitle {
		font-size: 18px;
		color: rgba(255, 255, 255, 0.9);
		margin: 0 0 32px 0;
	}
	
	.receipt {
		background: white;
		border-radius: 16px;
		padding: 24px;
		margin-bottom: 20px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
		text-align: left;
	}
	
	.receipt-header {
		text-align: center;
		padding-bottom: 20px;
		border-bottom: 2px dashed #e0e0e0;
		margin-bottom: 20px;
	}
	
	.receipt-header h2 {
		font-size: 24px;
		font-weight: 700;
		margin: 0 0 12px 0;
		color: #1a1a1a;
	}
	
	.group-number {
		font-size: 18px;
		font-weight: 600;
		color: #667eea;
		margin: 0 0 8px 0;
	}
	
	.location-name {
		font-size: 16px;
		color: #666;
		margin: 0 0 4px 0;
	}
	
	.date {
		font-size: 14px;
		color: #999;
		margin: 0;
	}
	
	.receipt-customer {
		padding: 16px;
		background: #f9f9f9;
		border-radius: 8px;
		margin-bottom: 20px;
	}
	
	.receipt-customer h3 {
		font-size: 16px;
		font-weight: 600;
		margin: 0 0 12px 0;
		color: #1a1a1a;
	}
	
	.receipt-customer p {
		font-size: 14px;
		color: #666;
		margin: 0 0 6px 0;
	}
	
	.receipt-orders {
		margin-bottom: 20px;
	}
	
	.order-section {
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 16px;
		margin-bottom: 16px;
		background: #fafafa;
	}
	
	.order-section:last-child {
		margin-bottom: 0;
	}
	
	.order-header {
		padding-bottom: 12px;
		border-bottom: 1px solid #e0e0e0;
		margin-bottom: 12px;
	}
	
	.order-header h3 {
		font-size: 18px;
		font-weight: 600;
		margin: 0 0 4px 0;
		color: #1a1a1a;
	}
	
	.outlet-name {
		font-size: 14px;
		color: #666;
		margin: 0 0 4px 0;
	}
	
	.order-number {
		font-size: 12px;
		color: #999;
		margin: 0;
	}
	
	.order-items {
		margin-bottom: 12px;
	}
	
	.receipt-item {
		display: flex;
		justify-content: space-between;
		padding: 10px 0;
		border-bottom: 1px solid #e8e8e8;
	}
	
	.receipt-item:last-child {
		border-bottom: none;
	}
	
	.item-info {
		display: flex;
		gap: 12px;
	}
	
	.item-qty {
		font-weight: 600;
		color: #667eea;
		min-width: 30px;
	}
	
	.item-name {
		font-size: 14px;
		font-weight: 500;
		color: #1a1a1a;
		margin: 0 0 4px 0;
	}
	
	.item-modifiers {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-bottom: 4px;
	}
	
	.item-modifiers span {
		font-size: 12px;
		color: #667eea;
		background: #f0f3ff;
		padding: 2px 8px;
		border-radius: 4px;
	}
	
	.item-notes {
		font-size: 12px;
		color: #666;
		font-style: italic;
		margin: 0;
	}
	
	.item-price {
		font-size: 14px;
		font-weight: 600;
		color: #1a1a1a;
		white-space: nowrap;
	}
	
	.order-summary {
		margin-top: 12px;
		padding-top: 12px;
		border-top: 1px solid #e0e0e0;
	}
	
	.summary-row, .summary-total {
		display: flex;
		justify-content: space-between;
		padding: 6px 0;
		font-size: 14px;
	}
	
	.summary-row {
		color: #666;
	}
	
	.summary-total {
		font-weight: 700;
		font-size: 16px;
		color: #1a1a1a;
		padding-top: 10px;
		border-top: 1px solid #e0e0e0;
		margin-top: 6px;
	}
	
	.grand-total {
		display: flex;
		justify-content: space-between;
		padding: 20px;
		background: #667eea;
		color: white;
		border-radius: 8px;
		font-size: 20px;
		font-weight: 700;
		margin-bottom: 16px;
	}
	
	.payment-info {
		text-align: center;
		padding: 16px;
		background: #f9f9f9;
		border-radius: 8px;
	}
	
	.payment-info p {
		font-size: 14px;
		color: #666;
		margin: 0 0 8px 0;
	}
	
	.payment-info p:last-child {
		margin-bottom: 0;
	}
	
	.status-paid {
		color: #4caf50;
		font-weight: 700;
	}
	
	.actions {
		display: flex;
		gap: 12px;
		margin-bottom: 16px;
	}
	
	.btn-primary, .btn-secondary {
		flex: 1;
		padding: 16px;
		border: none;
		border-radius: 12px;
		font-size: 16px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s;
	}
	
	.btn-primary {
		background: white;
		color: #667eea;
	}
	
	.btn-primary:hover {
		background: #f0f0f0;
		transform: translateY(-2px);
	}
	
	.btn-secondary {
		background: rgba(255, 255, 255, 0.2);
		color: white;
		border: 1px solid rgba(255, 255, 255, 0.3);
	}
	
	.btn-secondary:hover {
		background: rgba(255, 255, 255, 0.3);
		transform: translateY(-2px);
	}
	
	.thank-you {
		font-size: 18px;
		color: white;
		font-weight: 600;
		margin: 0;
	}
	
	@media print {
		.success-page {
			background: white;
			padding: 0;
		}
		
		.success-icon, .actions, .thank-you {
			display: none;
		}
		
		.receipt {
			box-shadow: none;
			padding: 20px;
		}
	}
</style>
