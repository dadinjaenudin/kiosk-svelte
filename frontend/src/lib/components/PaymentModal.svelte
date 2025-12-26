<script>
	import { createEventDispatcher } from 'svelte';
	
	export let groupedCartItems = [];
	export let grandTotal = 0;
	
	const dispatch = createEventDispatcher();
	
	// Payment methods
	const paymentMethods = [
		{ id: 'cash', name: 'Cash', icon: '💵', color: '#10B981' },
		{ id: 'qris', name: 'QRIS', icon: '📱', color: '#8B5CF6' },
		{ id: 'gopay', name: 'GoPay', icon: '🟢', color: '#00AA5B' },
		{ id: 'ovo', name: 'OVO', icon: '🟣', color: '#4F3BE8' },
		{ id: 'shopeepay', name: 'ShopeePay', icon: '🟠', color: '#EE4D2D' },
		{ id: 'dana', name: 'DANA', icon: '🔵', color: '#118EEA' },
		{ id: 'debit_card', name: 'Debit Card', icon: '💳', color: '#6B7280' },
		{ id: 'credit_card', name: 'Credit Card', icon: '💳', color: '#3B82F6' }
	];
	
	let selectedPaymentMethod = 'cash';
	let customerName = '';
	let customerPhone = '';
	let tableNumber = '';
	let notes = '';
	let processing = false;
	let error = '';
	
	function selectPaymentMethod(methodId) {
		selectedPaymentMethod = methodId;
		error = '';
	}
	
	function formatCurrency(amount) {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
	
	async function handleCheckout() {
		if (!selectedPaymentMethod) {
			error = 'Please select a payment method';
			return;
		}
		
		processing = true;
		error = '';
		
		dispatch('checkout', {
			paymentMethod: selectedPaymentMethod,
			customerName,
			customerPhone,
			tableNumber,
			notes
		});
	}
	
	function handleCancel() {
		dispatch('cancel');
	}
</script>

<div class="payment-modal-overlay" on:click={handleCancel}>
	<div class="payment-modal" on:click|stopPropagation>
		<!-- Header -->
		<div class="modal-header">
			<h2>💳 Pembayaran</h2>
			<button class="close-btn" on:click={handleCancel}>✕</button>
		</div>
		
		<!-- Order Summary -->
		<div class="order-summary">
			<h3>📋 Ringkasan Pesanan</h3>
			
			{#each groupedCartItems as group}
				<div class="tenant-group">
					<div class="tenant-header" style="border-left: 4px solid {group.tenant_color}">
						<span class="tenant-name">{group.tenant_name}</span>
						<span class="tenant-total">{formatCurrency(group.total)}</span>
					</div>
					<div class="items-list">
						{#each group.items as item}
							<div class="item-row">
								<span class="item-name">{item.product_name} × {item.quantity}</span>
								<span class="item-price">{formatCurrency(item.product_price * item.quantity)}</span>
							</div>
						{/each}
					</div>
				</div>
			{/each}
			
			<div class="total-row">
				<span class="total-label">Grand Total</span>
				<span class="total-amount">{formatCurrency(grandTotal)}</span>
			</div>
		</div>
		
		<!-- Payment Methods -->
		<div class="payment-methods">
			<h3>💳 Pilih Metode Pembayaran</h3>
			<div class="methods-grid">
				{#each paymentMethods as method}
					<button
						class="method-btn"
						class:selected={selectedPaymentMethod === method.id}
						style="border-color: {selectedPaymentMethod === method.id ? method.color : '#E5E7EB'}"
						on:click={() => selectPaymentMethod(method.id)}
					>
						<span class="method-icon">{method.icon}</span>
						<span class="method-name">{method.name}</span>
						{#if selectedPaymentMethod === method.id}
							<span class="check-icon">✓</span>
						{/if}
					</button>
				{/each}
			</div>
		</div>
		
		<!-- Customer Info (Optional) -->
		<div class="customer-info">
			<h3>👤 Info Pelanggan (Opsional)</h3>
			<div class="form-grid">
				<input
					type="text"
					placeholder="Nama"
					bind:value={customerName}
					class="form-input"
				/>
				<input
					type="tel"
					placeholder="No. HP"
					bind:value={customerPhone}
					class="form-input"
				/>
				<input
					type="text"
					placeholder="No. Meja"
					bind:value={tableNumber}
					class="form-input"
				/>
				<textarea
					placeholder="Catatan"
					bind:value={notes}
					class="form-textarea"
					rows="2"
				/>
			</div>
		</div>
		
		<!-- Error Message -->
		{#if error}
			<div class="error-message">
				⚠️ {error}
			</div>
		{/if}
		
		<!-- Action Buttons -->
		<div class="modal-actions">
			<button class="btn-cancel" on:click={handleCancel} disabled={processing}>
				Batal
			</button>
			<button
				class="btn-confirm"
				on:click={handleCheckout}
				disabled={processing || !selectedPaymentMethod}
			>
				{#if processing}
					⏳ Memproses...
				{:else}
					✓ Bayar {formatCurrency(grandTotal)}
				{/if}
			</button>
		</div>
	</div>
</div>

<style>
	.payment-modal-overlay {
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
	}
	
	.payment-modal {
		background: white;
		border-radius: 16px;
		max-width: 800px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
	}
	
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 24px;
		border-bottom: 2px solid #E5E7EB;
	}
	
	.modal-header h2 {
		font-size: 24px;
		font-weight: 700;
		color: #1F2937;
		margin: 0;
	}
	
	.close-btn {
		background: #F3F4F6;
		border: none;
		width: 40px;
		height: 40px;
		border-radius: 50%;
		font-size: 24px;
		color: #6B7280;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.close-btn:hover {
		background: #E5E7EB;
		color: #1F2937;
	}
	
	.order-summary {
		padding: 24px;
		background: #F9FAFB;
		border-bottom: 2px solid #E5E7EB;
	}
	
	.order-summary h3 {
		font-size: 16px;
		font-weight: 600;
		color: #374151;
		margin: 0 0 16px 0;
	}
	
	.tenant-group {
		margin-bottom: 16px;
		background: white;
		border-radius: 8px;
		overflow: hidden;
	}
	
	.tenant-header {
		padding: 12px 16px;
		background: #F9FAFB;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	
	.tenant-name {
		font-weight: 600;
		color: #1F2937;
	}
	
	.tenant-total {
		font-weight: 700;
		color: #059669;
	}
	
	.items-list {
		padding: 12px 16px;
	}
	
	.item-row {
		display: flex;
		justify-content: space-between;
		padding: 8px 0;
		font-size: 14px;
		color: #6B7280;
	}
	
	.total-row {
		display: flex;
		justify-content: space-between;
		padding: 16px;
		background: white;
		border-radius: 8px;
		margin-top: 16px;
	}
	
	.total-label {
		font-size: 18px;
		font-weight: 700;
		color: #1F2937;
	}
	
	.total-amount {
		font-size: 24px;
		font-weight: 800;
		color: #059669;
	}
	
	.payment-methods {
		padding: 24px;
	}
	
	.payment-methods h3 {
		font-size: 16px;
		font-weight: 600;
		color: #374151;
		margin: 0 0 16px 0;
	}
	
	.methods-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
		gap: 12px;
	}
	
	.method-btn {
		position: relative;
		background: white;
		border: 2px solid #E5E7EB;
		border-radius: 12px;
		padding: 16px;
		cursor: pointer;
		transition: all 0.2s;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
	}
	
	.method-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}
	
	.method-btn.selected {
		background: #F0FDF4;
		border-width: 3px;
	}
	
	.method-icon {
		font-size: 32px;
	}
	
	.method-name {
		font-size: 14px;
		font-weight: 600;
		color: #374151;
	}
	
	.check-icon {
		position: absolute;
		top: 8px;
		right: 8px;
		background: #10B981;
		color: white;
		width: 24px;
		height: 24px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 14px;
		font-weight: 700;
	}
	
	.customer-info {
		padding: 24px;
		background: #F9FAFB;
	}
	
	.customer-info h3 {
		font-size: 16px;
		font-weight: 600;
		color: #374151;
		margin: 0 0 16px 0;
	}
	
	.form-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 12px;
	}
	
	.form-input,
	.form-textarea {
		padding: 12px;
		border: 2px solid #E5E7EB;
		border-radius: 8px;
		font-size: 14px;
		transition: border-color 0.2s;
	}
	
	.form-input:focus,
	.form-textarea:focus {
		outline: none;
		border-color: #10B981;
	}
	
	.form-textarea {
		grid-column: 1 / -1;
		resize: vertical;
	}
	
	.error-message {
		margin: 0 24px;
		padding: 12px;
		background: #FEE2E2;
		color: #991B1B;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 500;
	}
	
	.modal-actions {
		padding: 24px;
		display: flex;
		gap: 12px;
		border-top: 2px solid #E5E7EB;
	}
	
	.btn-cancel,
	.btn-confirm {
		flex: 1;
		padding: 16px;
		border: none;
		border-radius: 12px;
		font-size: 16px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-cancel {
		background: #F3F4F6;
		color: #6B7280;
	}
	
	.btn-cancel:hover:not(:disabled) {
		background: #E5E7EB;
	}
	
	.btn-confirm {
		background: linear-gradient(135deg, #10B981 0%, #059669 100%);
		color: white;
	}
	
	.btn-confirm:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 8px 16px rgba(16, 185, 129, 0.3);
	}
	
	.btn-cancel:disabled,
	.btn-confirm:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
	
	@media (max-width: 640px) {
		.methods-grid {
			grid-template-columns: repeat(2, 1fr);
		}
		
		.form-grid {
			grid-template-columns: 1fr;
		}
		
		.modal-actions {
			flex-direction: column;
		}
	}
</style>
