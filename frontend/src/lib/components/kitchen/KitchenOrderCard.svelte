<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import type { KitchenOrder } from '$lib/stores/kitchenStore';
	
	export let order: KitchenOrder;
	export let column: 'pending' | 'preparing' | 'ready';
	
	const dispatch = createEventDispatcher();
	
	let currentTime = Date.now();
	let timer: any = null;
	
	// Update timer every minute
	onMount(() => {
		timer = setInterval(() => {
			currentTime = Date.now();
		}, 60000); // Update every minute
	});
	
	onDestroy(() => {
		if (timer) clearInterval(timer);
	});
	
	// Calculate wait time in minutes
	$: waitMinutes = order.wait_time || 0;
	$: isUrgent = order.is_urgent || waitMinutes > 15;
	
	function handleAction(action: 'start' | 'complete' | 'serve') {
		dispatch('action', { action });
	}
	
	function formatTime(isoString: string | null): string {
		if (!isoString) return '--:--';
		const date = new Date(isoString);
		return date.toLocaleTimeString('id-ID', { 
			hour: '2-digit', 
			minute: '2-digit',
			hour12: false
		});
	}
</script>

<div class="order-card {isUrgent ? 'urgent' : ''}" class:ready={column === 'ready'}>
	<!-- Order Header -->
	<div class="order-header">
		<div class="order-number-badge">
			<span class="order-number">{order.order_number}</span>
			{#if isUrgent}
				<span class="urgent-badge">🔥 URGENT</span>
			{/if}
		</div>
		<div class="order-time">
			<span class="time-label">Wait Time:</span>
			<span class="time-value {isUrgent ? 'urgent-time' : ''}">
				{waitMinutes} min
			</span>
		</div>
	</div>
	
	<!-- Customer Info -->
	{#if order.customer_name || order.customer_phone}
		<div class="customer-info">
			{#if order.customer_name}
				<div class="customer-name">
					👤 {order.customer_name}
				</div>
			{/if}
			{#if order.customer_phone}
				<div class="customer-phone">
					📞 {order.customer_phone}
				</div>
			{/if}
		</div>
	{/if}
	
	<!-- Order Type Badge -->
	<div class="order-meta">
		<span class="order-type {order.order_type}">
			{#if order.order_type === 'dinein'}
				🍽️ Dine In
			{:else if order.order_type === 'takeaway'}
				📦 Takeaway
			{:else if order.order_type === 'delivery'}
				🚚 Delivery
			{:else}
				{order.order_type}
			{/if}
		</span>
		<span class="order-created">
			⏰ {formatTime(order.created_at)}
		</span>
	</div>
	
	<!-- Order Items -->
	<div class="order-items">
		{#each order.items as item}
			<div class="order-item">
				<div class="item-quantity">{item.quantity}x</div>
				<div class="item-details">
					<div class="item-name">{item.product_name}</div>
					{#if item.modifiers_display && item.modifiers_display.length > 0}
						<div class="item-modifiers">
							{#each item.modifiers_display as modifier}
								<span class="modifier-tag">+ {modifier}</span>
							{/each}
						</div>
					{/if}
					{#if item.notes}
						<div class="item-notes">
							📝 {item.notes}
						</div>
					{/if}
				</div>
			</div>
		{/each}
	</div>
	
	<!-- Order Notes -->
	{#if order.notes}
		<div class="order-notes">
			<strong>Note:</strong> {order.notes}
		</div>
	{/if}
	
	<!-- Action Buttons -->
	<div class="order-actions">
		{#if column === 'pending'}
			<button 
				class="btn-action btn-start"
				on:click={() => handleAction('start')}
			>
				<span class="btn-icon">▶️</span>
				<span>Start Preparing</span>
			</button>
		{:else if column === 'preparing'}
			<button 
				class="btn-action btn-complete"
				on:click={() => handleAction('complete')}
			>
				<span class="btn-icon">✅</span>
				<span>Mark Ready</span>
			</button>
		{:else if column === 'ready'}
			<button 
				class="btn-action btn-serve"
				on:click={() => handleAction('serve')}
			>
				<span class="btn-icon">🍽️</span>
				<span>Serve Order</span>
			</button>
		{/if}
	</div>
</div>

<style>
	.order-card {
		background: white;
		border-radius: 12px;
		padding: 1.25rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		display: flex;
		flex-direction: column;
		gap: 1rem;
		transition: all 0.3s ease;
		border: 2px solid transparent;
	}
	
	.order-card:hover {
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
		transform: translateY(-2px);
	}
	
	.order-card.urgent {
		border-color: #dc2626;
		background: #fef2f2;
		animation: pulse-urgent 2s ease-in-out infinite;
	}
	
	@keyframes pulse-urgent {
		0%, 100% { 
			box-shadow: 0 2px 8px rgba(220, 38, 38, 0.2); 
		}
		50% { 
			box-shadow: 0 4px 20px rgba(220, 38, 38, 0.4); 
		}
	}
	
	.order-card.ready {
		border-color: #10b981;
		background: #f0fdf4;
	}
	
	/* Order Header */
	.order-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
	}
	
	.order-number-badge {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	
	.order-number {
		font-size: 1.25rem;
		font-weight: 700;
		color: #1f2937;
		font-family: 'Courier New', monospace;
	}
	
	.urgent-badge {
		background: #dc2626;
		color: white;
		padding: 0.25rem 0.5rem;
		border-radius: 6px;
		font-size: 0.75rem;
		font-weight: 700;
		letter-spacing: 0.05em;
		animation: blink 1s ease-in-out infinite;
	}
	
	@keyframes blink {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.7; }
	}
	
	.order-time {
		text-align: right;
	}
	
	.time-label {
		display: block;
		font-size: 0.75rem;
		color: #6b7280;
		text-transform: uppercase;
		font-weight: 600;
	}
	
	.time-value {
		display: block;
		font-size: 1.5rem;
		font-weight: 700;
		color: #3b82f6;
		margin-top: 0.25rem;
	}
	
	.time-value.urgent-time {
		color: #dc2626;
	}
	
	/* Customer Info */
	.customer-info {
		background: #f9fafb;
		padding: 0.75rem;
		border-radius: 8px;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
	
	.customer-name,
	.customer-phone {
		font-size: 0.875rem;
		color: #374151;
	}
	
	.customer-name {
		font-weight: 600;
	}
	
	/* Order Meta */
	.order-meta {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0;
		border-bottom: 1px solid #e5e7eb;
	}
	
	.order-type {
		background: #dbeafe;
		color: #1e40af;
		padding: 0.25rem 0.75rem;
		border-radius: 6px;
		font-size: 0.875rem;
		font-weight: 600;
	}
	
	.order-type.dinein {
		background: #dbeafe;
		color: #1e40af;
	}
	
	.order-type.takeaway {
		background: #fef3c7;
		color: #92400e;
	}
	
	.order-type.delivery {
		background: #fce7f3;
		color: #831843;
	}
	
	.order-created {
		font-size: 0.75rem;
		color: #6b7280;
	}
	
	/* Order Items */
	.order-items {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		max-height: 300px;
		overflow-y: auto;
	}
	
	.order-item {
		display: flex;
		gap: 0.75rem;
		padding: 0.75rem;
		background: #f9fafb;
		border-radius: 8px;
	}
	
	.item-quantity {
		font-size: 1.25rem;
		font-weight: 700;
		color: #3b82f6;
		min-width: 40px;
		text-align: center;
	}
	
	.item-details {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
	
	.item-name {
		font-weight: 600;
		color: #1f2937;
		font-size: 0.938rem;
	}
	
	.item-modifiers {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem;
	}
	
	.modifier-tag {
		background: #e0e7ff;
		color: #3730a3;
		padding: 0.125rem 0.5rem;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 500;
	}
	
	.item-notes {
		font-size: 0.813rem;
		color: #6b7280;
		font-style: italic;
		margin-top: 0.25rem;
	}
	
	/* Order Notes */
	.order-notes {
		background: #fef3c7;
		padding: 0.75rem;
		border-radius: 8px;
		font-size: 0.875rem;
		color: #78350f;
		border-left: 4px solid #f59e0b;
	}
	
	/* Action Buttons */
	.order-actions {
		display: flex;
		gap: 0.5rem;
		margin-top: 0.5rem;
	}
	
	.btn-action {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.875rem 1.5rem;
		border: none;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		color: white;
		min-height: 52px;
	}
	
	.btn-icon {
		font-size: 1.25rem;
	}
	
	.btn-start {
		background: #3b82f6;
	}
	
	.btn-start:hover {
		background: #2563eb;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
	}
	
	.btn-complete {
		background: #10b981;
	}
	
	.btn-complete:hover {
		background: #059669;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
	}
	
	.btn-serve {
		background: #8b5cf6;
	}
	
	.btn-serve:hover {
		background: #7c3aed;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
	}
	
	.btn-action:active {
		transform: translateY(0);
	}
	
	/* Scrollbar styling */
	.order-items::-webkit-scrollbar {
		width: 6px;
	}
	
	.order-items::-webkit-scrollbar-track {
		background: #f3f4f6;
		border-radius: 3px;
	}
	
	.order-items::-webkit-scrollbar-thumb {
		background: #d1d5db;
		border-radius: 3px;
	}
	
	.order-items::-webkit-scrollbar-thumb:hover {
		background: #9ca3af;
	}
</style>
