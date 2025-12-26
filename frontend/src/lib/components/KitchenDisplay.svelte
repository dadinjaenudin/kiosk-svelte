<script>
	import { onMount, onDestroy } from 'svelte';
	import { writable } from 'svelte/store';
	
	export let tenantId;
	export let tenantName;
	export let tenantColor;
	
	const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:8001/api';
	
	let orders = [];
	let loading = true;
	let error = '';
	let refreshInterval;
	
	const statusColors = {
		'confirmed': { bg: '#DBEAFE', text: '#1E40AF', icon: '✓' },
		'preparing': { bg: '#FEF3C7', text: '#92400E', icon: '🍳' },
		'ready': { bg: '#D1FAE5', text: '#065F46', icon: '✓' }
	};
	
	onMount(async () => {
		await loadOrders();
		
		// Refresh every 5 seconds
		refreshInterval = setInterval(loadOrders, 5000);
	});
	
	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});
	
	async function loadOrders() {
		try {
			console.log(`📋 Loading orders for tenant: ${tenantId} (${tenantName})`);
			
			const response = await fetch(`${apiUrl}/orders/kitchen_display/`, {
				headers: {
					'X-Tenant-ID': tenantId.toString()
				}
			});
			
			console.log(`📡 Response status: ${response.status}`);
			
			if (!response.ok) {
				const errorData = await response.json();
				console.error('❌ API Error:', errorData);
				throw new Error(errorData.error || 'Failed to load orders');
			}
			
			orders = await response.json();
			loading = false;
			error = '';
			
			console.log(`✅ Orders loaded:`, {
				tenantName,
				tenantId,
				orderCount: orders.length,
				orders: orders.map(o => ({
					order_number: o.order_number,
					status: o.status,
					created_at: o.created_at,
					items_count: o.items?.length || 0
				}))
			});
		} catch (err) {
			console.error('❌ Error loading orders:', err);
			error = err.message;
			loading = false;
		}
	}
	
	async function updateOrderStatus(orderId, newStatus) {
		try {
			const response = await fetch(`${apiUrl}/orders/${orderId}/update_status/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Tenant-ID': tenantId.toString()
				},
				body: JSON.stringify({ status: newStatus })
			});
			
			if (!response.ok) {
				throw new Error('Failed to update status');
			}
			
			// Reload orders
			await loadOrders();
			playSound();
		} catch (err) {
			console.error('Error updating status:', err);
			alert(`Gagal update status: ${err.message}`);
		}
	}
	
	function playSound() {
		// Play a simple beep sound
		const audioContext = new (window.AudioContext || window.webkitAudioContext)();
		const oscillator = audioContext.createOscillator();
		const gainNode = audioContext.createGain();
		
		oscillator.connect(gainNode);
		gainNode.connect(audioContext.destination);
		
		oscillator.frequency.value = 800;
		oscillator.type = 'sine';
		
		gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
		gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
		
		oscillator.start(audioContext.currentTime);
		oscillator.stop(audioContext.currentTime + 0.1);
	}
	
	function formatCurrency(amount) {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
	
	function formatTime(dateString) {
		const date = new Date(dateString);
		return new Intl.DateTimeFormat('id-ID', {
			hour: '2-digit',
			minute: '2-digit'
		}).format(date);
	}
	
	function getTimeSince(dateString) {
		const now = new Date();
		const created = new Date(dateString);
		const diffMs = now - created;
		const diffMins = Math.floor(diffMs / 60000);
		
		if (diffMins < 1) return 'Baru saja';
		if (diffMins < 60) return `${diffMins} menit lalu`;
		const diffHours = Math.floor(diffMins / 60);
		return `${diffHours} jam lalu`;
	}
</script>

<div class="kitchen-display" style="border-top: 6px solid {tenantColor}">
	<!-- Header -->
	<div class="kitchen-header" style="background: {tenantColor}">
		<div class="tenant-info">
			<h1>{tenantName}</h1>
			<p>Kitchen Display System</p>
		</div>
		<div class="order-count">
			<span class="count">{orders.length}</span>
			<span class="label">Pesanan Aktif</span>
		</div>
	</div>
	
	<!-- Loading State -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Memuat pesanan...</p>
		</div>
	{/if}
	
	<!-- Error State -->
	{#if error}
		<div class="error-state">
			<p>⚠️ {error}</p>
			<button on:click={loadOrders}>Coba Lagi</button>
		</div>
	{/if}
	
	<!-- Orders Grid -->
	{#if !loading && !error}
		{#if orders.length === 0}
			<div class="empty-state">
				<div class="empty-icon">✨</div>
				<h3>Tidak Ada Pesanan</h3>
				<p>Semua pesanan sudah selesai!</p>
			</div>
		{:else}
			<div class="orders-grid">
				{#each orders as order}
					<div class="order-card" class:urgent={getTimeSince(order.created_at).includes('jam')}>
						<!-- Order Header -->
						<div class="order-header">
							<div class="order-info">
								<span class="order-number">#{order.order_number}</span>
								<span class="order-time">{formatTime(order.created_at)}</span>
							</div>
							<div class="time-badge" class:old={getTimeSince(order.created_at).includes('jam')}>
								⏱️ {getTimeSince(order.created_at)}
							</div>
						</div>
						
						<!-- Order Items -->
						<div class="order-items">
							{#each order.items as item}
								<div class="order-item">
									<div class="item-quantity">{item.quantity}x</div>
									<div class="item-details">
										<div class="item-name">{item.product_name}</div>
										{#if item.modifiers && item.modifiers.length > 0}
											<div class="item-modifiers">
												{#each item.modifiers as mod}
													<span class="modifier-tag">+ {mod.name}</span>
												{/each}
											</div>
										{/if}
										{#if item.notes}
											<div class="item-notes">📝 {item.notes}</div>
										{/if}
									</div>
								</div>
							{/each}
						</div>
						
						<!-- Customer Info -->
						{#if order.customer_name || order.table_number}
							<div class="customer-info">
								{#if order.table_number}
									<span class="info-badge">🪑 Meja {order.table_number}</span>
								{/if}
								{#if order.customer_name}
									<span class="info-badge">👤 {order.customer_name}</span>
								{/if}
							</div>
						{/if}
						
						<!-- Order Actions -->
						<div class="order-actions">
							{#if order.status === 'confirmed'}
								<button
									class="btn-action btn-start"
									on:click={() => updateOrderStatus(order.id, 'preparing')}
								>
									🍳 Mulai Masak
								</button>
							{:else if order.status === 'preparing'}
								<button
									class="btn-action btn-ready"
									on:click={() => updateOrderStatus(order.id, 'ready')}
								>
									✓ Siap Disajikan
								</button>
							{:else if order.status === 'ready'}
								<button
									class="btn-action btn-served"
									on:click={() => updateOrderStatus(order.id, 'served')}
								>
									✓ Sudah Disajikan
								</button>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	{/if}
</div>

<style>
	.kitchen-display {
		height: 100vh;
		background: #F3F4F6;
		overflow-y: auto;
	}
	
	.kitchen-header {
		padding: 24px 32px;
		color: white;
		display: flex;
		justify-content: space-between;
		align-items: center;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}
	
	.tenant-info h1 {
		font-size: 32px;
		font-weight: 800;
		margin: 0 0 4px 0;
	}
	
	.tenant-info p {
		font-size: 16px;
		opacity: 0.9;
		margin: 0;
	}
	
	.order-count {
		text-align: right;
	}
	
	.order-count .count {
		display: block;
		font-size: 48px;
		font-weight: 800;
		line-height: 1;
	}
	
	.order-count .label {
		font-size: 14px;
		opacity: 0.9;
	}
	
	.loading-state,
	.error-state,
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 60vh;
		padding: 48px;
		text-align: center;
	}
	
	.spinner {
		width: 64px;
		height: 64px;
		border: 6px solid #E5E7EB;
		border-top-color: #10B981;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
	
	.empty-icon {
		font-size: 96px;
		margin-bottom: 16px;
	}
	
	.empty-state h3 {
		font-size: 28px;
		font-weight: 700;
		color: #1F2937;
		margin: 0 0 8px 0;
	}
	
	.empty-state p {
		font-size: 18px;
		color: #6B7280;
		margin: 0;
	}
	
	.orders-grid {
		padding: 32px;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
		gap: 24px;
	}
	
	.order-card {
		background: white;
		border-radius: 16px;
		padding: 24px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
		transition: all 0.3s;
		border: 2px solid transparent;
	}
	
	.order-card:hover {
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
		transform: translateY(-4px);
	}
	
	.order-card.urgent {
		border-color: #EF4444;
		animation: pulse 2s infinite;
	}
	
	@keyframes pulse {
		0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
		50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
	}
	
	.order-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 20px;
		padding-bottom: 16px;
		border-bottom: 2px solid #E5E7EB;
	}
	
	.order-info {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	
	.order-number {
		font-size: 20px;
		font-weight: 800;
		color: #1F2937;
		font-family: 'Courier New', monospace;
	}
	
	.order-time {
		font-size: 14px;
		color: #6B7280;
	}
	
	.time-badge {
		padding: 6px 12px;
		background: #DBEAFE;
		color: #1E40AF;
		border-radius: 20px;
		font-size: 14px;
		font-weight: 600;
	}
	
	.time-badge.old {
		background: #FEE2E2;
		color: #991B1B;
	}
	
	.order-items {
		margin-bottom: 16px;
	}
	
	.order-item {
		display: flex;
		gap: 12px;
		padding: 12px 0;
		border-bottom: 1px solid #F3F4F6;
	}
	
	.order-item:last-child {
		border-bottom: none;
	}
	
	.item-quantity {
		flex-shrink: 0;
		width: 48px;
		height: 48px;
		background: #10B981;
		color: white;
		border-radius: 12px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 20px;
		font-weight: 800;
	}
	
	.item-details {
		flex: 1;
	}
	
	.item-name {
		font-size: 16px;
		font-weight: 700;
		color: #1F2937;
		margin-bottom: 4px;
	}
	
	.item-modifiers {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-bottom: 4px;
	}
	
	.modifier-tag {
		padding: 2px 8px;
		background: #FEF3C7;
		color: #92400E;
		border-radius: 4px;
		font-size: 12px;
		font-weight: 600;
	}
	
	.item-notes {
		font-size: 14px;
		color: #059669;
		font-style: italic;
		margin-top: 4px;
	}
	
	.customer-info {
		display: flex;
		gap: 8px;
		margin-bottom: 16px;
		flex-wrap: wrap;
	}
	
	.info-badge {
		padding: 6px 12px;
		background: #F3F4F6;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 600;
		color: #374151;
	}
	
	.order-actions {
		display: flex;
		gap: 12px;
	}
	
	.btn-action {
		flex: 1;
		padding: 16px;
		border: none;
		border-radius: 12px;
		font-size: 16px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.btn-action:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
	}
	
	.btn-start {
		background: #FCD34D;
		color: #78350F;
	}
	
	.btn-ready {
		background: #10B981;
		color: white;
	}
	
	.btn-served {
		background: #3B82F6;
		color: white;
	}
</style>
