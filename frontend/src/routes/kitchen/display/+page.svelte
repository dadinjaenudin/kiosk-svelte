<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { kitchenConfig, kitchenOrders, kitchenStats, isKitchenConfigured } from '$lib/stores/kitchenStore';
	import KitchenOrderCard from '$lib/components/kitchen/KitchenOrderCard.svelte';
	
	const API_BASE = 'http://localhost:8001/api';
	
	let polling: any = null;
	let soundEnabled = false;
	let lastPendingCount = 0;
	let audioContext: AudioContext | null = null;
	
	// Subscribe to config for sound setting
	$: soundEnabled = $kitchenConfig.soundEnabled;
	
	onMount(async () => {
		// Check if kitchen is configured
		if (!$isKitchenConfigured) {
			goto('/kitchen/login');
			return;
		}
		
		console.log('🍳 Kitchen Display initialized:', {
			store: $kitchenConfig.storeName,
			outlet: $kitchenConfig.outletName,
			deviceId: $kitchenConfig.deviceId
		});
		
		// Initialize audio context (will be activated on first user interaction)
		if (typeof window !== 'undefined' && window.AudioContext) {
			audioContext = new AudioContext();
		}
		
		// Initial load
		await fetchAllOrders();
		await fetchStats();
		
		// Start polling every 10 seconds
		polling = setInterval(async () => {
			await fetchAllOrders();
			await fetchStats();
		}, 10000);
	});
	
	onDestroy(() => {
		if (polling) {
			clearInterval(polling);
		}
		if (audioContext) {
			audioContext.close();
		}
	});
	
	async function fetchAllOrders() {
		try {
			const outletId = $kitchenConfig.outletId;
			
			// Fetch pending orders
			const pendingRes = await fetch(`${API_BASE}/kitchen/orders/pending/?outlet=${outletId}`);
			if (pendingRes.ok) {
				const pending = await pendingRes.json();
				
				// Play sound if new orders arrived
				if (soundEnabled && pending.length > lastPendingCount) {
					playNewOrderSound();
				}
				lastPendingCount = pending.length;
				
				kitchenOrders.setPending(pending);
			}
			
			// Fetch preparing orders
			const preparingRes = await fetch(`${API_BASE}/kitchen/orders/preparing/?outlet=${outletId}`);
			if (preparingRes.ok) {
				const preparing = await preparingRes.json();
				kitchenOrders.setPreparing(preparing);
			}
			
			// Fetch ready orders
			const readyRes = await fetch(`${API_BASE}/kitchen/orders/ready/?outlet=${outletId}`);
			if (readyRes.ok) {
				const ready = await readyRes.json();
				kitchenOrders.setReady(ready);
			}
			
		} catch (err) {
			console.error('Failed to fetch orders:', err);
			kitchenOrders.update(state => ({ ...state, error: 'Failed to load orders' }));
		}
	}
	
	async function fetchStats() {
		try {
			const outletId = $kitchenConfig.outletId;
			const response = await fetch(`${API_BASE}/kitchen/orders/stats/?outlet=${outletId}`);
			
			if (response.ok) {
				const stats = await response.json();
				kitchenStats.setStats(stats);
			}
		} catch (err) {
			console.error('Failed to fetch stats:', err);
		}
	}
	
	function playNewOrderSound() {
		if (!audioContext || !soundEnabled) return;
		
		try {
			// Resume audio context if suspended (Chrome autoplay policy)
			if (audioContext.state === 'suspended') {
				audioContext.resume();
			}
			
			// Generate beep sound (440Hz for 0.2s)
			const oscillator = audioContext.createOscillator();
			const gainNode = audioContext.createGain();
			
			oscillator.connect(gainNode);
			gainNode.connect(audioContext.destination);
			
			oscillator.frequency.value = 440; // A4 note
			oscillator.type = 'sine';
			
			gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
			gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
			
			oscillator.start(audioContext.currentTime);
			oscillator.stop(audioContext.currentTime + 0.2);
			
			console.log('🔔 New order sound played');
		} catch (err) {
			console.error('Failed to play sound:', err);
		}
	}
	
	function toggleSound() {
		kitchenConfig.toggleSound();
		
		// Resume audio context on user interaction
		if (audioContext && audioContext.state === 'suspended') {
			audioContext.resume();
		}
	}
	
	function handleLogout() {
		if (confirm('Are you sure you want to logout?')) {
			kitchenConfig.clear();
			kitchenOrders.clear();
			goto('/kitchen/login');
		}
	}
	
	async function handleOrderAction(orderId: number, action: 'start' | 'complete' | 'serve', column: 'pending' | 'preparing' | 'ready') {
		try {
			const response = await fetch(`${API_BASE}/kitchen/orders/${orderId}/${action}/`, {
				method: 'POST',
			});
			
			if (!response.ok) {
				throw new Error(`Failed to ${action} order`);
			}
			
			const data = await response.json();
			console.log(`✅ Order ${action}:`, data);
			
			// Optimistically move order to next column
			if (action === 'start' && column === 'pending') {
				kitchenOrders.moveOrder(orderId, 'pending', 'preparing');
			} else if (action === 'complete' && column === 'preparing') {
				kitchenOrders.moveOrder(orderId, 'preparing', 'ready');
			} else if (action === 'serve' && column === 'ready') {
				kitchenOrders.removeOrder(orderId, 'ready');
			}
			
			// Refresh data
			await fetchAllOrders();
			await fetchStats();
			
		} catch (err) {
			console.error(`Failed to ${action} order:`, err);
			alert(`Failed to ${action} order. Please try again.`);
		}
	}
</script>

<div class="kitchen-display">
	<!-- Header -->
	<header class="kitchen-header">
		<div class="header-left">
			<div class="logo">🍳</div>
			<div class="header-info">
				<h1>Kitchen Display</h1>
				<p class="outlet-name">{$kitchenConfig.outletName} - {$kitchenConfig.storeName}</p>
			</div>
		</div>
		
		<div class="header-stats">
			<div class="stat-card">
				<span class="stat-label">Pending</span>
				<span class="stat-value pending">{$kitchenStats.pending_count}</span>
			</div>
			<div class="stat-card">
				<span class="stat-label">Preparing</span>
				<span class="stat-value preparing">{$kitchenStats.preparing_count}</span>
			</div>
			<div class="stat-card">
				<span class="stat-label">Ready</span>
				<span class="stat-value ready">{$kitchenStats.ready_count}</span>
			</div>
			<div class="stat-card">
				<span class="stat-label">Avg Time</span>
				<span class="stat-value">{$kitchenStats.avg_prep_time || 0} min</span>
			</div>
		</div>
		
		<div class="header-actions">
			<button 
				class="btn-icon {soundEnabled ? 'active' : ''}"
				on:click={toggleSound}
				title={soundEnabled ? 'Mute sounds' : 'Enable sounds'}
			>
				{#if soundEnabled}
					🔔
				{:else}
					🔕
				{/if}
			</button>
			<button class="btn-logout" on:click={handleLogout}>
				Logout
			</button>
		</div>
	</header>
	
	<!-- Orders Kanban -->
	<div class="orders-container">
		{#if $kitchenOrders.error}
			<div class="error-message">
				<p>{$kitchenOrders.error}</p>
				<button on:click={fetchAllOrders}>Retry</button>
			</div>
		{:else}
			<!-- Pending Column -->
			<div class="order-column pending-column">
				<div class="column-header">
					<h2>🆕 Pending</h2>
					<span class="count-badge">{$kitchenOrders.pending.length}</span>
				</div>
				<div class="order-list">
					{#each $kitchenOrders.pending as order (order.id)}
						<KitchenOrderCard 
							{order}
							column="pending"
							on:action={(e) => handleOrderAction(order.id, e.detail.action, 'pending')}
						/>
					{:else}
						<div class="empty-state">
							<p>No pending orders</p>
							<span class="emoji">✅</span>
						</div>
					{/each}
				</div>
			</div>
			
			<!-- Preparing Column -->
			<div class="order-column preparing-column">
				<div class="column-header">
					<h2>👨‍🍳 Preparing</h2>
					<span class="count-badge">{$kitchenOrders.preparing.length}</span>
				</div>
				<div class="order-list">
					{#each $kitchenOrders.preparing as order (order.id)}
						<KitchenOrderCard 
							{order}
							column="preparing"
							on:action={(e) => handleOrderAction(order.id, e.detail.action, 'preparing')}
						/>
					{:else}
						<div class="empty-state">
							<p>No orders being prepared</p>
							<span class="emoji">⏳</span>
						</div>
					{/each}
				</div>
			</div>
			
			<!-- Ready Column -->
			<div class="order-column ready-column">
				<div class="column-header">
					<h2>✅ Ready</h2>
					<span class="count-badge">{$kitchenOrders.ready.length}</span>
				</div>
				<div class="order-list">
					{#each $kitchenOrders.ready as order (order.id)}
						<KitchenOrderCard 
							{order}
							column="ready"
							on:action={(e) => handleOrderAction(order.id, e.detail.action, 'ready')}
						/>
					{:else}
						<div class="empty-state">
							<p>No orders ready</p>
							<span class="emoji">🍽️</span>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.kitchen-display {
		min-height: 100vh;
		background: #f3f4f6;
		display: flex;
		flex-direction: column;
	}
	
	/* Header */
	.kitchen-header {
		background: white;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		padding: 1rem 2rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 2rem;
		flex-wrap: wrap;
	}
	
	.header-left {
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	
	.logo {
		font-size: 2.5rem;
	}
	
	.header-info h1 {
		font-size: 1.5rem;
		font-weight: 700;
		color: #1f2937;
		margin: 0;
	}
	
	.outlet-name {
		font-size: 0.875rem;
		color: #6b7280;
		margin: 0;
	}
	
	.header-stats {
		display: flex;
		gap: 1rem;
		flex: 1;
		justify-content: center;
	}
	
	.stat-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 0.75rem 1.25rem;
		background: #f9fafb;
		border-radius: 8px;
		min-width: 100px;
	}
	
	.stat-label {
		font-size: 0.75rem;
		color: #6b7280;
		text-transform: uppercase;
		font-weight: 600;
		letter-spacing: 0.05em;
	}
	
	.stat-value {
		font-size: 1.75rem;
		font-weight: 700;
		color: #1f2937;
		margin-top: 0.25rem;
	}
	
	.stat-value.pending { color: #f59e0b; }
	.stat-value.preparing { color: #3b82f6; }
	.stat-value.ready { color: #10b981; }
	
	.header-actions {
		display: flex;
		gap: 0.75rem;
		align-items: center;
	}
	
	.btn-icon {
		background: #f3f4f6;
		border: none;
		width: 44px;
		height: 44px;
		border-radius: 8px;
		font-size: 1.5rem;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.btn-icon:hover {
		background: #e5e7eb;
	}
	
	.btn-icon.active {
		background: #dbeafe;
	}
	
	.btn-logout {
		background: #dc2626;
		color: white;
		border: none;
		padding: 0.5rem 1.25rem;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
	}
	
	.btn-logout:hover {
		background: #b91c1c;
	}
	
	/* Orders Container */
	.orders-container {
		flex: 1;
		padding: 1.5rem;
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1.5rem;
		overflow-y: auto;
	}
	
	.order-column {
		background: #f9fafb;
		border-radius: 12px;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		min-height: 0;
	}
	
	.pending-column { border-top: 4px solid #f59e0b; }
	.preparing-column { border-top: 4px solid #3b82f6; }
	.ready-column { border-top: 4px solid #10b981; }
	
	.column-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
		padding-bottom: 0.75rem;
		border-bottom: 2px solid #e5e7eb;
	}
	
	.column-header h2 {
		font-size: 1.25rem;
		font-weight: 700;
		color: #1f2937;
		margin: 0;
	}
	
	.count-badge {
		background: #1f2937;
		color: white;
		width: 32px;
		height: 32px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.875rem;
		font-weight: 700;
	}
	
	.order-list {
		flex: 1;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	
	.empty-state {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		color: #9ca3af;
		text-align: center;
		padding: 2rem;
	}
	
	.empty-state .emoji {
		font-size: 3rem;
		opacity: 0.5;
	}
	
	.error-message {
		grid-column: 1 / -1;
		text-align: center;
		padding: 3rem;
		background: #fee2e2;
		border-radius: 12px;
		color: #991b1b;
	}
	
	.error-message button {
		margin-top: 1rem;
		padding: 0.5rem 1.5rem;
		background: #dc2626;
		color: white;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
	}
	
	/* Responsive */
	@media (max-width: 1280px) {
		.orders-container {
			grid-template-columns: repeat(2, 1fr);
		}
		
		.ready-column {
			grid-column: 1 / -1;
		}
	}
	
	@media (max-width: 768px) {
		.kitchen-header {
			padding: 1rem;
		}
		
		.header-stats {
			order: 3;
			width: 100%;
			justify-content: space-around;
		}
		
		.stat-card {
			min-width: 80px;
			padding: 0.5rem 0.75rem;
		}
		
		.orders-container {
			grid-template-columns: 1fr;
			gap: 1rem;
		}
		
		.ready-column {
			grid-column: auto;
		}
	}
</style>
