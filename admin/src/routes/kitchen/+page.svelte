<script>
	import { onMount, onDestroy } from 'svelte';
	import { io } from 'socket.io-client';
	import { isAuthenticated, user, selectedTenant } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { formatCurrency, formatDateTime } from '$lib/api/orders';
	import { getAllOutlets } from '$lib/api/outlets';
	
	let socket = null;
	let orders = [];
	let connected = false;
	let outletId = null;
	let outlets = [];
	let selectedOutletId = null;
	
	// Group orders by status
	$: pendingOrders = orders.filter(o => o.status === 'pending' || o.status === 'confirmed');
	$: preparingOrders = orders.filter(o => o.status === 'preparing');
	$: readyOrders = orders.filter(o => o.status === 'ready');
	
	// Connect to Kitchen Sync Server
	function connectToKitchenSync(useOutletId = null) {
		// Get outlet ID from parameter, selected, user settings, or default to 1
		outletId = useOutletId || selectedOutletId || $user?.outlet || $selectedTenant || 1;
		
		const SYNC_SERVER_URL = 'http://localhost:3001';
		console.log('[Kitchen Display] Connecting to', SYNC_SERVER_URL);
		
		socket = io(SYNC_SERVER_URL, {
			transports: ['websocket', 'polling']
		});
		
		socket.on('connect', () => {
			console.log('[Kitchen Display] ✅ Connected');
			connected = true;
			
			// Identify as kitchen display
			socket.emit('identify', { type: 'kitchen' });
			
			// Subscribe to outlet
			socket.emit('subscribe_outlet', outletId);
			console.log('[Kitchen Display] 📍 Subscribed to outlet:', outletId);
		});
		
		socket.on('disconnect', () => {
			console.log('[Kitchen Display] 📴 Disconnected');
			connected = false;
		// Clear orders when disconnected to prevent showing stale data
		orders = [];
			console.log('[Kitchen Display] ✅ Subscribed:', data);
		});
		
		// Listen for new orders
		socket.on('order_created', (data) => {
			console.log('[Kitchen Display] 🆕 New order received:', data);
			
			const order = data.data || data;
			
			// Add to orders list if not exists
			if (!orders.find(o => o.order_number === order.order_number)) {
				orders = [order, ...orders];
				
				// Play sound notification
				playNotification();
			}
		});
		
		// Listen for status updates
		socket.on('order_status_updated', (data) => {
			console.log('[Kitchen Display] 🔄 Status updated:', data);
			
			const index = orders.findIndex(o => o.order_number === data.order_number);
			if (index !== -1) {
				orders[index].status = data.status;
				orders = [...orders];
			}
		});
	}
	
	function disconnectFromKitchenSync() {
		if (socket) {
			socket.disconnect();
			socket = null;
		}
	}
	
	function playNotification() {
		// Simple beep (can be replaced with actual sound file)
		const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZizcIGmi775+fTRAMT6fj8LZjHAY4kdfyy3ksBSR3x/DdkEAKFF606eumVRQKRp/g8r5sIQUrgs/y2Yk3CBloue+fn00QDE+o4/C2YxwGOJHX8sp5LAUkd8fw3ZBAC');
		audio.play().catch(e => console.log('Audio play failed:', e));
	}
	
	function updateOrderStatus(orderNumber, newStatus) {
		// Emit status update to server
		if (socket && socket.connected) {
			socket.emit('update_status', {
				order_number: orderNumber,
				status: newStatus
			});
		}
		
		// Update local state
		const index = orders.findIndex(o => o.order_number === orderNumber);
		if (index !== -1) {
			orders[index].status = newStatus;
			orders = [...orders];
		}
	}
	
	function completeOrder(orderNumber) {
		updateOrderStatus(orderNumber, 'completed');
		
		// Remove from display after 2 seconds
		setTimeout(() => {
			orders = orders.filter(o => o.order_number !== orderNumber);
		}, 2000);
	}
	
	function changeOutlet(newOutletId) {
		selectedOutletId = parseInt(newOutletId);
		// Disconnect current connection
		disconnectFromKitchenSync();
		// Clear orders
		orders = [];
		// Reconnect to new outlet
		connectToKitchenSync(selectedOutletId);
	}
	
	async function loadOutlets() {
		try {
			const response = await getAllOutlets();
			outlets = response.results || [];
			// Set initial selected outlet
			if (outlets.length > 0 && !selectedOutletId) {
				selectedOutletId = $user?.outlet || $selectedTenant || outlets[0].id;
			}
		} catch (error) {
			console.error('[Kitchen Display] Failed to load outlets:', error);
		}
	}
	
	onMount(async () => {
		if (!$isAuthenticated) {
			goto('/login');
			return;
		}
		
		// Check if user has kitchen role
		if ($user?.role !== 'kitchen' && $user?.role !== 'admin' && $user?.role !== 'super_admin') {
			goto('/unauthorized');
			return;
		}
		
		// Load outlets first
		await loadOutlets();
		
		// Then connect
		connectToKitchenSync();
	});
	
	onDestroy(() => {
		disconnectFromKitchenSync();
	});
</script>

<div class="min-h-screen bg-gray-100 p-4">
	<!-- Header -->
	<div class="mb-6">
		<div class="flex items-center justify-between mb-2">
			<h1 class="text-3xl font-bold text-gray-900">🍳 Kitchen Display</h1>
			<div class="text-right">
				<div class="text-sm text-gray-600">Total Active Orders</div>
				<div class="text-3xl font-bold text-gray-900">{orders.length}</div>
			</div>
		</div>
		<div class="flex items-center gap-4 flex-wrap">
			<p class="text-gray-600">
				Real-time order display via WebSocket
			</p>
			
			<!-- Outlet Selector -->
			{#if outlets.length > 0}
				<select 
					bind:value={selectedOutletId}
					on:change={(e) => changeOutlet(e.target.value)}
					class="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
				>
					{#each outlets as outlet (outlet.id)}
						<option value={outlet.id}>{outlet.name}</option>
					{/each}
				</select>
			{/if}
			
			{#if connected}
				<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
					● Connected to Outlet #{outletId}
				</span>
			{:else}
				<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
					● Disconnected
				</span>
			{/if}
		</div>
	</div>

	{#if !connected}
		<div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
			<div class="flex">
				<div class="flex-shrink-0">
					<svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
					</svg>
				</div>
				<div class="ml-3">
					<p class="text-sm text-yellow-700">
						⚠️ <strong>Not connected to Kitchen Sync Server</strong>
						<br>
						Make sure the server is running at <code class="bg-yellow-100 px-1 rounded">http://localhost:3001</code>
					</p>
				</div>
			</div>
		</div>
	{/if}

	{#if orders.length === 0}
		<div class="text-center py-12">
			<svg class="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
			</svg>
			<h3 class="mt-2 text-lg font-medium text-gray-900">No active orders</h3>
			<p class="mt-1 text-sm text-gray-500">
				{#if connected}
					Waiting for new orders from POS...
				{:else}
					Connect to Kitchen Sync Server to receive orders
				{/if}
			</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<!-- Pending Orders -->
			<div>
				<h2 class="text-lg font-semibold mb-4 text-gray-700 flex items-center">
					<span class="w-3 h-3 bg-yellow-400 rounded-full mr-2"></span>
					Pending ({pendingOrders.length})
				</h2>
				<div class="space-y-4">
					{#each pendingOrders as order (order.order_number)}
						<div class="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-400">
							<div class="flex justify-between items-start mb-3">
								<div>
									<div class="text-xl font-bold text-gray-900">#{order.order_number}</div>
									<div class="text-sm text-gray-600">{formatDateTime(order.created_at)}</div>
								</div>
								<div class="text-right">
									<div class="text-sm font-medium px-2 py-1 rounded" style="background-color: {order.tenant_color}20; color: {order.tenant_color}">
										{order.tenant_name}
									</div>
								</div>
							</div>
							
							<div class="space-y-2 mb-4">
								{#each order.items || [] as item}
									<div class="flex justify-between text-sm">
										<span>{item.quantity}x {item.product_name || item.name}</span>
										<span class="text-gray-600">{formatCurrency(item.price * item.quantity)}</span>
									</div>
								{/each}
							</div>
							
							{#if order.notes}
								<div class="text-sm bg-yellow-50 p-2 rounded mb-4">
									<strong>Notes:</strong> {order.notes}
								</div>
							{/if}
							
							<button
								on:click={() => updateOrderStatus(order.order_number, 'preparing')}
								class="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
							>
								Start Preparing
							</button>
						</div>
					{/each}
				</div>
			</div>

			<!-- Preparing Orders -->
			<div>
				<h2 class="text-lg font-semibold mb-4 text-gray-700 flex items-center">
					<span class="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
					Preparing ({preparingOrders.length})
				</h2>
				<div class="space-y-4">
					{#each preparingOrders as order (order.order_number)}
						<div class="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
							<div class="flex justify-between items-start mb-3">
								<div>
									<div class="text-xl font-bold text-gray-900">#{order.order_number}</div>
									<div class="text-sm text-gray-600">{formatDateTime(order.created_at)}</div>
								</div>
								<div class="text-right">
									<div class="text-sm font-medium px-2 py-1 rounded" style="background-color: {order.tenant_color}20; color: {order.tenant_color}">
										{order.tenant_name}
									</div>
								</div>
							</div>
							
							<div class="space-y-2 mb-4">
								{#each order.items || [] as item}
									<div class="flex justify-between text-sm">
										<span>{item.quantity}x {item.product_name || item.name}</span>
										<span class="text-gray-600">{formatCurrency(item.price * item.quantity)}</span>
									</div>
								{/each}
							</div>
							
							<button
								on:click={() => updateOrderStatus(order.order_number, 'ready')}
								class="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
							>
								Mark as Ready
							</button>
						</div>
					{/each}
				</div>
			</div>

			<!-- Ready Orders -->
			<div>
				<h2 class="text-lg font-semibold mb-4 text-gray-700 flex items-center">
					<span class="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
					Ready ({readyOrders.length})
				</h2>
				<div class="space-y-4">
					{#each readyOrders as order (order.order_number)}
						<div class="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
							<div class="flex justify-between items-start mb-3">
								<div>
									<div class="text-xl font-bold text-gray-900">#{order.order_number}</div>
									<div class="text-sm text-gray-600">{formatDateTime(order.created_at)}</div>
								</div>
								<div class="text-right">
									<div class="text-sm font-medium px-2 py-1 rounded" style="background-color: {order.tenant_color}20; color: {order.tenant_color}">
										{order.tenant_name}
									</div>
								</div>
							</div>
							
							<div class="space-y-2 mb-4">
								{#each order.items || [] as item}
									<div class="flex justify-between text-sm">
										<span>{item.quantity}x {item.product_name || item.name}</span>
										<span class="text-gray-600">{formatCurrency(item.price * item.quantity)}</span>
									</div>
								{/each}
							</div>
							
							<button
								on:click={() => completeOrder(order.order_number)}
								class="w-full bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-900 transition"
							>
								Complete & Remove
							</button>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}
	
	.bg-green-500, .bg-blue-500, .bg-yellow-400 {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
</style>
