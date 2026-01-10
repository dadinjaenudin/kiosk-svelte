<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { get } from 'svelte/store';
	import { kitchenConfig, kitchenOrders, kitchenStats, isKitchenConfigured, setPendingOrders, setPreparingOrders, setReadyOrders } from '$lib/stores/kitchenStore';
	import KitchenOrderCard from '$lib/components/kitchen/KitchenOrderCard.svelte';
	import ConnectionStatus from '$lib/components/ConnectionStatus.svelte';
	import { networkService, networkStatus, checkHealth } from '$lib/services/networkService';
	import { socketService, socketStatus } from '$lib/services/socketService';
	
	const API_BASE = 'http://localhost:8001/api';
	
	// Offline mode detection
	let offlineMode = false;
	
	// Offline orders storage (from Local Sync Server)
	let offlineOrders: any[] = [];
	
	// WORKAROUND: Local copy for reactivity (since $store binding is broken)
	let localPendingOrders: any[] = [];
	let localPreparingOrders: any[] = [];
	let localReadyOrders: any[] = [];
	
	// Cache corruption detection
	let cacheCorruptionDetected = false;
	
	// Socket connection status (from socketService)
	let socketConnected = false;
	$: socketConnected = $socketStatus.localConnected;
	
	// Manual network status tracking (workaround for broken reactive binding)
	let networkOnline = true;
	let networkMode = 'checking';
	let networkLatency: number | null = null;
	let socketMode = 'none';
	
	// Status badge expand/collapse
	let statusExpanded = false;
	function toggleStatus() {
		statusExpanded = !statusExpanded;
	}
	
	// Polling function to force update from stores (ultimate workaround)
	function updateNetworkStatus() {
		const netStatus = get(networkStatus);
		const sockStatus = get(socketStatus);
		
		networkOnline = netStatus.isOnline;
		networkMode = netStatus.mode;
		networkLatency = netStatus.latency;
		socketMode = sockStatus.mode;
	}
	
	// Subscribe manually to network status
	let networkUnsubscribe: any;
	let socketUnsubscribe: any;
	let statusPollInterval: any;
	
	let polling: any = null;
	let soundEnabled = false;
	let lastPendingCount = 0;
	let audioContext: AudioContext | null = null;
	let unsubscribeOrders: (() => void) | undefined;
	
	// Subscribe to config for sound setting
	$: soundEnabled = $kitchenConfig.soundEnabled;
	
	// Setup socket event listeners
	function setupSocketListeners() {
		console.log('🔌 Setting up socket event listeners for kitchen display...');
		
		// Listen for new order events (from Central Server)
		socketService.onCentral('new_order', async (data) => {
			console.log('🔔 New order received via Central Server:', data.order_number);
			await fetchAllOrders();
			playNewOrderSound();
		});
		
		// Listen for order status updates (from Central Server)
		socketService.onCentral('order_updated', async (data) => {
			console.log('🔄 Order updated via Central Server:', data.order_number, '→', data.status);
			await fetchAllOrders();
		});
		
		// Listen for offline orders from kiosk (from Local Sync Server)
		socketService.onLocal('order:created:offline', async (data) => {
			console.log('🔔 Offline order received from kiosk:', data);
			
			// Transform offline order to match backend format
			const offlineOrder = {
				id: `offline-${Date.now()}`, // Temporary ID
				order_number: data.order_number || `OFFLINE-${Date.now()}`,
				order_group_id: null,
				status: 'pending',
				tenant: data.tenant_id,
				tenant_name: data.tenant_name || 'Unknown',
				outlet: data.checkout_data?.carts?.[0]?.outlet_id || null,
				outlet_name: 'Unknown Outlet',
				store: data.store_id,
				store_name: 'Unknown Store',
				customer_name: data.customer_name || 'Guest',
				customer_phone: data.customer_phone || '',
				table_number: '',
				notes: '',
				subtotal: (data.total_amount * 0.8).toFixed(2), // Rough estimate
				tax_amount: (data.total_amount * 0.1).toFixed(2),
				service_charge_amount: (data.total_amount * 0.1).toFixed(2),
				total_amount: data.total_amount?.toFixed(2) || '0.00',
				source: 'kiosk',
				device_id: data.device_id || 'Unknown',
				created_at: data.created_at || new Date().toISOString(),
				updated_at: data.created_at || new Date().toISOString(),
				completed_at: null,
				items: data.checkout_data?.carts?.[0]?.items?.map((item: any) => ({
					id: `item-${Date.now()}-${Math.random()}`,
					product: item.product_id,
					product_name: item.product_name || `Product ${item.product_id}`,
					product_image: null,
					quantity: item.quantity || 1,
					unit_price: '0.00',
					total_price: '0.00',
					notes: item.notes || '',
					modifiers: item.modifiers || [],
					modifiers_display: []
				})) || [],
				wait_time: 0,
				is_urgent: false,
				is_offline: true // Flag to indicate this is offline order
			};
			
			// Add to local pending orders for immediate display
			localPendingOrders = [offlineOrder, ...localPendingOrders];
			console.log('📱 Added offline order to kitchen display:', offlineOrder.order_number);
			
			// Play notification sound
			playNewOrderSound();
		});
		
		// Listen for when offline order is synced (from Local Sync Server)
		socketService.onLocal('order:synced', async (data) => {
			console.log('✅ Offline order synced:', data.order_number);
			
			// Remove from offline orders
			offlineOrders = offlineOrders.filter(o => o.order_number !== data.order_number);
			
			// Refresh orders from backend
			await fetchAllOrders();
		});
		
		console.log('✅ Socket event listeners registered');
	}


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
	console.log('🏭 Imported kitchenOrders store object:', kitchenOrders);
	
	// Manual subscription to network status (workaround for broken reactivity)
	networkUnsubscribe = networkStatus.subscribe(status => {
		networkOnline = status.isOnline;
		networkMode = status.mode;
		networkLatency = status.latency;
		console.log('🌐 Network Status Updated (manual subscription):', { mode: networkMode, isOnline: networkOnline, latency: networkLatency });
	});
	
	// Manual subscription to socket status
	socketUnsubscribe = socketStatus.subscribe(status => {
		socketMode = status.mode;
	});
	
	// NUCLEAR WORKAROUND: Poll status every 2 seconds using get()
	// Because even manual subscriptions are broken by HMR cache
	statusPollInterval = setInterval(() => {
		updateNetworkStatus();
	}, 2000);
	
	try {
		await socketService.connectLocal();
		console.log('✅ Connected to Local Sync Server, joining kitchen room...');
		
		// Join kitchen room on Local Sync Server (after connected)
		socketService.emitToLocal('join-kitchen', {
			outletId: $kitchenConfig.outletId,
			deviceId: $kitchenConfig.deviceId
		});
	} catch (error) {
		console.warn('⚠️ Failed to connect to Local Sync Server:', error);
	}
	
	try {
		await socketService.connectCentral();
		console.log('✅ Connected to Central Server, joining kitchen room...');
		
		// Join kitchen room on Central Server (after connected)
		socketService.emitToCentral('join-kitchen', {
			outletId: $kitchenConfig.outletId,
			deviceId: $kitchenConfig.deviceId
		});
	} catch (error) {
		console.warn('⚠️ Failed to connect to Central Server:', error);
	}
		
		// Setup socket event listeners
		setupSocketListeners();
		
		// Initial load
		await fetchAllOrders();
		
		
// Start HTTP polling (runs every 10s to ensure data is fresh)
	console.log('📡 Starting HTTP polling (10s interval)...');
	polling = setInterval(async () => {
		// Skip polling if offline to avoid error spam
		if (!networkOnline) {
			console.log('⏸️ Skipping poll - System offline');
			return;
		}
		console.log('🔄 Polling: Fetching orders...');
		await fetchAllOrders();
		}, 10000);
	});
	
	onDestroy(() => {
		if (polling) {
			clearInterval(polling);
		}
		if (statusPollInterval) {
			clearInterval(statusPollInterval);
		}
		// Unsubscribe from stores
		if (unsubscribeOrders) {
			unsubscribeOrders();
		}
		if (networkUnsubscribe) {
			networkUnsubscribe();
		}
		if (socketUnsubscribe) {
			socketUnsubscribe();
		}
		// socketService manages socket cleanup automatically
		if (audioContext) {
			audioContext.close();
		}
	});
	
	async function fetchAllOrders() {
		// Skip if offline
		if (offlineMode) {
			// Offline mode: Skip fetch (socket handles updates)
			return;
		}
		
		try {
			const outletId = $kitchenConfig.outletId;
			
			// Fetch with timeout (5 seconds max)
			const fetchWithTimeout = (url: string, timeout = 5000) => {
				return Promise.race([
					fetch(url),
					new Promise<Response>((_, reject) =>
						setTimeout(() => reject(new Error('Fetch timeout')), timeout)
					)
				]);
			};
			
			// Fetch pending orders
			const pendingRes = await fetchWithTimeout(`${API_BASE}/kitchen/orders/pending/?outlet=${outletId}`);
			if (pendingRes.ok) {
				const pending = await pendingRes.json();
				console.log('📥 Fetched pending orders:', pending.length, pending);
				console.log('📋 First order structure:', JSON.stringify(pending[0], null, 2));
				
				// Play sound if new orders arrived
				if (soundEnabled && pending.length > lastPendingCount) {
					playNewOrderSound();
				}
				lastPendingCount = pending.length;
				
			// WORKAROUND: Update local variable directly (bypasses store reactivity issue)
			localPendingOrders = [...pending];
			console.log('✅ Updated localPendingOrders:', localPendingOrders.length);
			
			// Still update store for consistency
			kitchenOrders.update(state => ({ ...state, pending }));
		}
		
		// Fetch preparing orders
		const preparingRes = await fetchWithTimeout(`${API_BASE}/kitchen/orders/preparing/?outlet=${outletId}`);
		if (preparingRes.ok) {
			const preparing = await preparingRes.json();
			console.log('📥 Fetched preparing orders:', preparing.length);
			localPreparingOrders = [...preparing];
			kitchenOrders.update(state => ({ ...state, preparing }));
		}
		
		// Fetch ready orders
		const readyRes = await fetchWithTimeout(`${API_BASE}/kitchen/orders/ready/?outlet=${outletId}`);
		if (readyRes.ok) {
			const ready = await readyRes.json();
			localReadyOrders = [...ready];
			kitchenOrders.update(state => ({ ...state, ready }));
		}
		
		// Check for cache corruption after fetching
		
	} catch (err) {
		// Silently handle fetch errors (offline mode handles this)
		// Only log once to avoid console spam
		if (networkOnline) {
			console.warn('⚠️ Failed to fetch orders:', err);
		}
		// Trigger network health check on fetch failure
		checkHealth();
	}
}

// Play sound when new orders arrive
function playNewOrderSound() {
	try {
		if (!audioContext) {
			audioContext = new AudioContext();
		}
		
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
			// Clear kitchen config
			kitchenConfig.clear();
			
			// Clear all intervals
			if (polling) clearInterval(polling);
			if (statusPollInterval) clearInterval(statusPollInterval);
			
			// Redirect to login
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
			
			// Optimistically update local arrays
			if (action === 'start' && column === 'pending') {
				const order = localPendingOrders.find(o => o.id === orderId);
				if (order) {
					localPendingOrders = localPendingOrders.filter(o => o.id !== orderId);
					localPreparingOrders = [...localPreparingOrders, { ...order, status: 'preparing' }];
				}
			} else if (action === 'complete' && column === 'preparing') {
				const order = localPreparingOrders.find(o => o.id === orderId);
				if (order) {
					localPreparingOrders = localPreparingOrders.filter(o => o.id !== orderId);
					localReadyOrders = [...localReadyOrders, { ...order, status: 'ready' }];
				}
			} else if (action === 'serve' && column === 'ready') {
				localReadyOrders = localReadyOrders.filter(o => o.id !== orderId);
			}
			
			// Refresh data from server
			await fetchAllOrders();
			
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
			<!-- Inline Connection Status (Collapsible) -->
			<div class="inline-connection-status">
				<button 
					class="status-badge clickable" 
					class:online={networkOnline} 
					class:offline={!networkOnline}
					class:expanded={statusExpanded}
					on:click={toggleStatus}
					title="Click to {statusExpanded ? 'hide' : 'show'} details"
				>
					<span class="status-dot"></span>
					<div class="status-info">
						<span class="status-label">{networkOnline ? 'Online' : 'Offline'}</span>
						{#if statusExpanded}
							<div class="status-details-inline">
								<span class="detail-item">Socket: {socketMode}</span>
								{#if networkLatency}
									<span class="detail-item">{networkLatency}ms</span>
								{/if}
							</div>
						{/if}
					</div>
					<span class="toggle-icon">{statusExpanded ? '▼' : '▶'}</span>
				</button>
			</div>
			
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
					<span class="count-badge">{$kitchenOrders.pending.length + offlineOrders.length}</span>
				</div>
				<div class="order-list">
					<!-- Offline Orders (not yet synced) -->
					{#each offlineOrders as order (order.order_number)}
						<div class="offline-order-card">
							<div class="offline-badge">📴 Pending Sync</div>
							<div class="order-info">
								<h3>{order.order_number}</h3>
								<p class="customer">{order.customer_name}</p>
								<p class="total">Rp {order.total_amount.toLocaleString()}</p>
								<p class="payment">{order.payment_method}</p>
							</div>
							<div class="offline-note">
								Waiting for sync to backend...
							</div>
						</div>
					{/each}
					
					<!-- Online/Synced Orders -->
					{#each localPendingOrders as order (order.id)}
						<KitchenOrderCard 
							{order}
							column="pending"
							on:action={(e) => handleOrderAction(order.id, e.detail.action, 'pending')}
						/>
					{:else}
						{#if offlineOrders.length === 0}
							<div class="empty-state">
								<p>No pending orders</p>
								<span class="emoji">✅</span>
							</div>
						{/if}
					{/each}
				</div>
			</div>
			
			<!-- Preparing Column -->
			<div class="order-column preparing-column">
				<div class="column-header">
					<h2>👨‍🍳 Preparing</h2>
				<span class="count-badge">{localPreparingOrders.length}</span>
			</div>
			<div class="order-list">
				{#each localPreparingOrders as order (order.id)}
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
				<span class="count-badge">{localReadyOrders.length}</span>
			</div>
			<div class="order-list">
				{#each localReadyOrders as order (order.id)}
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
	
	/* Cache Warning Banner */
	.cache-warning-banner {
		background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
		color: #78350f;
		padding: 1rem 1.5rem;
		display: flex;
		align-items: center;
		gap: 1rem;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		position: relative;
		z-index: 100;
		animation: slideDown 0.3s ease-out;
	}
	
	@keyframes slideDown {
		from {
			transform: translateY(-100%);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}
	
	.warning-icon {
		font-size: 2rem;
		flex-shrink: 0;
	}
	
	.warning-content {
		flex: 1;
	}
	
	.warning-content strong {
		display: block;
		font-size: 1rem;
		margin-bottom: 0.25rem;
	}
	
	.warning-content p {
		margin: 0;
		font-size: 0.875rem;
		opacity: 0.9;
	}
	
	.close-warning {
		background: rgba(0, 0, 0, 0.1);
		border: none;
		color: #78350f;
		width: 32px;
		height: 32px;
		border-radius: 50%;
		cursor: pointer;
		font-size: 1.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s;
		flex-shrink: 0;
	}
	
	.close-warning:hover {
		background: rgba(0, 0, 0, 0.2);
		transform: scale(1.1);
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
	
	/* Inline Connection Status */
	.inline-connection-status {
		margin-right: 0.5rem;
	}
	
	.status-badge {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		border-radius: 8px;
		background: #f3f4f6;
		transition: all 0.3s ease;
		border: 1px solid transparent;
	}
	
	.status-badge.clickable {
		cursor: pointer;
		border: none;
	}
	
	.status-badge.clickable:hover {
		transform: scale(1.02);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}
	
	.status-badge.expanded {
		padding: 0.5rem 1rem;
	}
	
	.status-badge.online {
		background: #d1fae5;
		border: 1px solid #10b981;
	}
	
	.status-badge.offline {
		background: #fee2e2;
		border: 1px solid #ef4444;
	}
	
	.status-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		flex-shrink: 0;
	}
	
	.status-badge.online .status-dot {
		background: #10b981;
		box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.3);
		animation: pulse 2s ease-in-out infinite;
	}
	
	.status-badge.offline .status-dot {
		background: #ef4444;
		box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.3);
	}
	
	.status-info {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
		min-width: 0;
	}
	
	.status-label {
		font-size: 0.875rem;
		font-weight: 600;
		color: #1f2937;
		white-space: nowrap;
	}
	
	.status-details-inline {
		display: flex;
		gap: 0.5rem;
		font-size: 0.75rem;
		color: #6b7280;
		margin-top: 0.25rem;
		animation: slideDown 0.2s ease-out;
	}
	
	.detail-item {
		white-space: nowrap;
	}
	
	.toggle-icon {
		font-size: 0.625rem;
		color: #6b7280;
		margin-left: 0.25rem;
		transition: transform 0.2s ease;
	}
	
	@keyframes pulse {
		0%, 100% { opacity: 1; transform: scale(1); }
		50% { opacity: 0.6; transform: scale(0.95); }
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
	
	/* Offline Order Card */
	.offline-order-card {
		background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
		border: 2px dashed #f59e0b;
		border-radius: 12px;
		padding: 1rem;
		margin-bottom: 1rem;
		box-shadow: 0 2px 8px rgba(245, 158, 11, 0.2);
	}
	
	.offline-badge {
		display: inline-block;
		background: #f59e0b;
		color: white;
		padding: 0.25rem 0.75rem;
		border-radius: 6px;
		font-size: 0.75rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
	}
	
	.offline-order-card .order-info {
		margin: 0.75rem 0;
	}
	
	.offline-order-card h3 {
		font-size: 1.125rem;
		font-weight: 700;
		color: #92400e;
		margin: 0 0 0.5rem 0;
	}
	
	.offline-order-card .customer {
		font-size: 0.875rem;
		color: #78350f;
		margin: 0.25rem 0;
	}
	
	.offline-order-card .total {
		font-size: 1rem;
		font-weight: 600;
		color: #92400e;
		margin: 0.25rem 0;
	}
	
	.offline-order-card .payment {
		font-size: 0.75rem;
		color: #78350f;
		margin: 0.25rem 0;
	}
	
	.offline-note {
		margin-top: 0.75rem;
		padding: 0.5rem;
		background: rgba(255, 255, 255, 0.6);
		border-radius: 6px;
		font-size: 0.75rem;
		color: #78350f;
		text-align: center;
		font-style: italic;
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
