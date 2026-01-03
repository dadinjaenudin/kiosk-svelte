<script>
	import { createEventDispatcher } from 'svelte';
	import { printReceipt, printAllReceipts, downloadReceipt } from '$lib/utils/print.js';
	
	export let orders = [];
	export let payments = [];
	export let totalAmount = 0;
	export let paymentMethod = '';
	export let offline = false; // New: track if order was saved offline
	
	const dispatch = createEventDispatcher();
	
	function formatCurrency(amount) {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
	
	function formatDateTime(dateString) {
		const date = new Date(dateString);
		return new Intl.DateTimeFormat('id-ID', {
			day: '2-digit',
			month: 'short',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		}).format(date);
	}
	
	function handlePrintReceipt(order) {
		printReceipt(order);
	}
	
	function handlePrintAll() {
		printAllReceipts({ orders });
	}
	
	function handleDownloadReceipt(order) {
		downloadReceipt(order);
	}
	
	function handleClose() {
		dispatch('close');
	}
</script>

<div class="success-modal-overlay">
	<div class="success-modal">
		<!-- Success Icon -->
		<div class="success-icon">
			<div class="checkmark">✓</div>
		</div>
		
		<!-- Header -->
		<div class="modal-header">
			{#if offline}
				<h2>📴 Pembayaran Disimpan (Offline)</h2>
				<p class="subtitle offline-notice">
					{orders.length} pesanan disimpan offline. Akan otomatis dikirim ke server saat online.
				</p>
			{:else}
				<h2>🎉 Pembayaran Berhasil!</h2>
				<p class="subtitle">{orders.length} pesanan telah dibuat</p>
			{/if}
		</div>
		
		<!-- Orders List -->
		<div class="orders-list">
			{#each orders as order, index}
				<div class="order-card" style="border-left: 4px solid {order.tenant_color}">
					<div class="order-header">
						<div class="order-info">
							<span class="order-number">#{order.order_number}</span>
							<span class="tenant-name">{order.tenant_name}</span>
						</div>
						<span class="order-amount">{formatCurrency(order.total_amount)}</span>
					</div>
					
					<div class="order-items">
						{#each order.items as item}
							<div class="item-row">
								<span>{item.product_name} × {item.quantity}</span>
								<span>{formatCurrency(item.total_price)}</span>
							</div>
						{/each}
					</div>
					
					<div class="order-footer">
						<button class="btn-print" on:click={() => handlePrintReceipt(order)}>
							🖨️ Print Struk
						</button>
						<button class="btn-download" on:click={() => handleDownloadReceipt(order)}>
							💾 Download
						</button>
						<span class="order-status">
							{#if order.status === 'confirmed'}
								<span class="status-badge confirmed">✓ Dikonfirmasi</span>
							{:else if order.status === 'preparing'}
								<span class="status-badge preparing">🍳 Dimasak</span>
							{:else}
								<span class="status-badge pending">⏳ Menunggu</span>
							{/if}
						</span>
					</div>
				</div>
			{/each}
		</div>
		
		<!-- Payment Summary -->
		<div class="payment-summary">
			<div class="summary-row">
				<span>Metode Pembayaran:</span>
				<strong>{paymentMethod.toUpperCase()}</strong>
			</div>
			<div class="summary-row total">
				<span>Total Pembayaran:</span>
				<strong>{formatCurrency(totalAmount)}</strong>
			</div>
		</div>
		
		<!-- Actions -->
		<div class="modal-actions">
			<button class="btn-print-all" on:click={handlePrintAll}>
				🖨️ Print Semua Struk
			</button>
			<button class="btn-done" on:click={handleClose}>
				✓ Selesai
			</button>
		</div>
		
		<div class="footer-note">
			<p>💡 Struk akan dikirim ke dapur masing-masing tenant</p>
		</div>
	</div>
</div>

<style>
	.success-modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 20px;
		animation: fadeIn 0.3s;
	}
	
	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}
	
	.success-modal {
		background: white;
		border-radius: 20px;
		max-width: 600px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: slideUp 0.3s;
	}
	
	@keyframes slideUp {
		from {
			transform: translateY(30px);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}
	
	.success-icon {
		padding: 40px 24px 20px;
		text-align: center;
	}
	
	.checkmark {
		width: 80px;
		height: 80px;
		margin: 0 auto;
		background: linear-gradient(135deg, #10B981 0%, #059669 100%);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 48px;
		color: white;
		font-weight: 700;
		animation: scaleIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
	}
	
	@keyframes scaleIn {
		from {
			transform: scale(0);
		}
		to {
			transform: scale(1);
		}
	}
	
	.modal-header {
		text-align: center;
		padding: 0 24px 24px;
	}
	
	.modal-header h2 {
		font-size: 28px;
		font-weight: 800;
		color: #1F2937;
		margin: 0 0 8px 0;
	}
	
	.subtitle {
		font-size: 16px;
		color: #6B7280;
		margin: 0;
	}
	
	.offline-notice {
		color: #F59E0B;
		background: #FEF3C7;
		padding: 8px 16px;
		border-radius: 8px;
		font-weight: 500;
		margin-top: 8px;
	}
	
	.orders-list {
		padding: 0 24px 16px;
		max-height: 400px;
		overflow-y: auto;
	}
	
	.order-card {
		background: #F9FAFB;
		border-radius: 12px;
		padding: 16px;
		margin-bottom: 12px;
		border-left: 4px solid #10B981;
	}
	
	.order-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 12px;
	}
	
	.order-info {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	
	.order-number {
		font-size: 14px;
		font-weight: 700;
		color: #059669;
		font-family: 'Courier New', monospace;
	}
	
	.tenant-name {
		font-size: 16px;
		font-weight: 600;
		color: #1F2937;
	}
	
	.order-amount {
		font-size: 18px;
		font-weight: 700;
		color: #059669;
	}
	
	.order-items {
		padding: 12px 0;
		border-top: 1px solid #E5E7EB;
		border-bottom: 1px solid #E5E7EB;
	}
	
	.item-row {
		display: flex;
		justify-content: space-between;
		padding: 6px 0;
		font-size: 14px;
		color: #6B7280;
	}
	
	.order-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-top: 12px;
		gap: 8px;
	}
	
	.btn-print,
	.btn-download {
		background: white;
		border: 2px solid #E5E7EB;
		padding: 8px 12px;
		border-radius: 8px;
		font-size: 13px;
		font-weight: 600;
		color: #374151;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-print:hover {
		background: #F3F4F6;
		border-color: #10B981;
		color: #059669;
	}
	
	.btn-download:hover {
		background: #F3F4F6;
		border-color: #3B82F6;
		color: #2563EB;
	}
	
	.order-status {
		flex: 1;
		text-align: right;
	}
	
	.status-badge {
		display: inline-block;
		padding: 6px 12px;
		border-radius: 20px;
		font-size: 12px;
		font-weight: 600;
	}
	
	.status-badge.confirmed {
		background: #D1FAE5;
		color: #065F46;
	}
	
	.status-badge.preparing {
		background: #FEF3C7;
		color: #92400E;
	}
	
	.status-badge.pending {
		background: #E0E7FF;
		color: #3730A3;
	}
	
	.payment-summary {
		padding: 16px 24px;
		background: #F9FAFB;
		border-top: 2px solid #E5E7EB;
		border-bottom: 2px solid #E5E7EB;
	}
	
	.summary-row {
		display: flex;
		justify-content: space-between;
		padding: 8px 0;
		font-size: 14px;
		color: #6B7280;
	}
	
	.summary-row.total {
		font-size: 18px;
		color: #1F2937;
		padding-top: 12px;
		border-top: 2px solid #E5E7EB;
		margin-top: 8px;
	}
	
	.summary-row strong {
		color: #059669;
	}
	
	.modal-actions {
		padding: 24px;
		display: flex;
		gap: 12px;
	}
	
	.btn-print-all,
	.btn-done {
		flex: 1;
		padding: 16px;
		border: none;
		border-radius: 12px;
		font-size: 16px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-print-all {
		background: white;
		color: #059669;
		border: 2px solid #10B981;
	}
	
	.btn-print-all:hover {
		background: #F0FDF4;
	}
	
	.btn-done {
		background: linear-gradient(135deg, #10B981 0%, #059669 100%);
		color: white;
	}
	
	.btn-done:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 16px rgba(16, 185, 129, 0.3);
	}
	
	.footer-note {
		padding: 0 24px 24px;
		text-align: center;
	}
	
	.footer-note p {
		font-size: 14px;
		color: #6B7280;
		margin: 0;
	}
	
	@media (max-width: 640px) {
		.modal-actions {
			flex-direction: column;
		}
	}
</style>
