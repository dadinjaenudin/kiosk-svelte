/**
 * Kitchen Sync Store - Kitchen Display Side
 * Listens for orders from Kitchen Sync Server (local network WebSocket)
 * for real-time order updates when offline
 */

import { writable, get } from 'svelte/store';

// WebSocket connection state
export const syncServerConnected = writable(false);

// New orders received from POS (via sync server)
export const newOrders = writable([]);

// Outlet settings with WebSocket URL
export const outletSettings = writable(null);

let ws = null;
let reconnectTimer = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY = 3000; // 3 seconds

// Default fallback
const DEFAULT_SYNC_SERVER_URL = 'ws://localhost:3001';

// Order notification callback
let onNewOrderCallback = null;
let onOrderStatusCallback = null;

/**
 * Get WebSocket URL from outlet settings or fallback
 */
function getWebSocketURL() {
	const settings = get(outletSettings);
	const wsUrl = settings?.websocket_url || DEFAULT_SYNC_SERVER_URL;
	console.log('[KitchenSync] Using WebSocket URL:', wsUrl);
	return wsUrl;
}

/**
 * Load outlet settings from API
 */
export async function loadOutletSettings(outletId) {
	try {
		const response = await fetch(`http://localhost:8000/api/tenants/outlets/${outletId}/`);
		if (response.ok) {
			const data = await response.json();
			outletSettings.set(data);
			console.log('[KitchenSync] Outlet settings loaded:', {
				outlet: data.name,
				websocket_url: data.websocket_url
			});
			return data;
		}
	} catch (error) {
		console.error('[KitchenSync] Failed to load outlet settings:', error);
	}
	return null;
}

/**
 * Connect to Kitchen Sync Server
 */
export function connectToSyncServer() {
	if (ws && ws.readyState === WebSocket.OPEN) {
		console.log('[KitchenSync] Already connected');
		return;
	}

	const SYNC_SERVER_URL = getWebSocketURL();
	console.log(`[KitchenSync] Connecting to ${SYNC_SERVER_URL}...`);

	try {
		ws = new WebSocket(SYNC_SERVER_URL);

		ws.onopen = () => {
			console.log('[KitchenSync] ✅ Connected to Kitchen Sync Server');
			syncServerConnected.set(true);
			reconnectAttempts = 0;

			// Send identification message
			ws.send(
				JSON.stringify({
					type: 'identify',
					role: 'kitchen_display',
					timestamp: new Date().toISOString()
				})
			);
		};

		ws.onmessage = async (event) => {
			try {
				// Handle Blob data from WebSocket
				let messageText = event.data;
				if (event.data instanceof Blob) {
					messageText = await event.data.text();
				}
				
				const data = JSON.parse(messageText);
				console.log('[KitchenSync] Received:', data.type, data);

				// Handle different message types
				switch (data.type) {
					case 'connected':
						console.log('[KitchenSync] ✅ Server welcome:', data.message);
						break;

					case 'new_order':
						console.log('[KitchenSync] 🔔 New order received:', data.data?.order_number);
						console.log('[KitchenSync] 📦 Order data:', data.data);
						handleNewOrder(data.data);
						break;

					case 'order_status':
						console.log(
							'[KitchenSync] 📝 Order status update:',
							data.data.order_number,
							'→',
							data.data.status
						);
						handleOrderStatusUpdate(data.data);
						break;

					case 'ack':
						console.log(`[KitchenSync] ✅ Server acknowledged: ${data.messageType}`);
						break;

					default:
						console.log('[KitchenSync] Unknown message type:', data.type);
				}
			} catch (error) {
				console.error('[KitchenSync] Error parsing message:', error);
			}
		};

		ws.onerror = (error) => {
			console.error('[KitchenSync] ❌ WebSocket error:', error);
			syncServerConnected.set(false);
		};

		ws.onclose = () => {
			console.log('[KitchenSync] 📴 Disconnected from Kitchen Sync Server');
			syncServerConnected.set(false);
			ws = null;

			// Attempt to reconnect
			if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
				reconnectAttempts++;
				console.log(
					`[KitchenSync] ⏳ Reconnecting in ${RECONNECT_DELAY / 1000}s (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`
				);
				reconnectTimer = setTimeout(connectToSyncServer, RECONNECT_DELAY);
			} else {
				console.log(
					'[KitchenSync] ⚠️ Max reconnect attempts reached. Please check server.'
				);
			}
		};
	} catch (error) {
		console.error('[KitchenSync] Error creating WebSocket:', error);
		syncServerConnected.set(false);
	}
}

/**
 * Disconnect from Kitchen Sync Server
 */
export function disconnectFromSyncServer() {
	if (reconnectTimer) {
		clearTimeout(reconnectTimer);
		reconnectTimer = null;
	}

	if (ws) {
		ws.close();
		ws = null;
	}

	syncServerConnected.set(false);
	console.log('[KitchenSync] 👋 Disconnected');
}

/**
 * Handle new order received from sync server
 * @param {Object} order - Order data
 */
function handleNewOrder(order) {
	console.log('[KitchenSync] 🔍 Processing order:', {
		order_number: order?.order_number,
		tenant_id: order?.tenant_id,
		items_count: order?.items?.length
	});
	
	if (!order || !order.order_number) {
		console.error('[KitchenSync] ❌ Invalid order data:', order);
		return;
	}
	
	// Add to newOrders store
	newOrders.update((orders) => {
		// Check if order already exists (avoid duplicates)
		const exists = orders.find((o) => o.order_number === order.order_number);
		if (exists) {
			console.warn('[KitchenSync] ⚠️ Order already exists:', order.order_number);
			return orders;
		}

		console.log('[KitchenSync] ✅ Adding order to store:', order.order_number);
		// Add new order to the beginning of the list
		return [order, ...orders];
	});

	// Play notification sound (if available)
	playNotificationSound();

	// Show notification (if enabled)
	showOrderNotification(order);

	// Call callback if registered
	if (onNewOrderCallback) {
		onNewOrderCallback(order);
	}
}

/**
 * Handle order status update received from sync server
 * @param {Object} statusUpdate - Status update data
 */
function handleOrderStatusUpdate(statusUpdate) {
	const { order_number, status, updated_at } = statusUpdate;

	// Update order in newOrders store
	newOrders.update((orders) => {
		return orders.map((order) => {
			if (order.order_number === order_number) {
				return {
					...order,
					status: status,
					updated_at: updated_at
				};
			}
			return order;
		});
	});

	// Call callback if registered
	if (onOrderStatusCallback) {
		onOrderStatusCallback(statusUpdate);
	}
}

/**
 * Play notification sound for new order
 * Enhanced with multiple beeps for better attention
 */
function playNotificationSound() {
	// Try Web Audio API first (more reliable and louder)
	try {
		const audioContext = new (window.AudioContext || window.webkitAudioContext)();
		
		// Play 3 beeps in sequence for better attention
		const beeps = [
			{ frequency: 800, startTime: 0, duration: 0.15 },
			{ frequency: 1000, startTime: 0.2, duration: 0.15 },
			{ frequency: 800, startTime: 0.4, duration: 0.15 },
			{ frequency: 1000, startTime: 0.6, duration: 0.15 },
			{ frequency: 1200, startTime: 0.8, duration: 0.3 }
		];
		
		beeps.forEach((beep) => {
			const oscillator = audioContext.createOscillator();
			const gainNode = audioContext.createGain();
			
			oscillator.connect(gainNode);
			gainNode.connect(audioContext.destination);
			
			oscillator.frequency.value = beep.frequency;
			oscillator.type = 'sine';
			
			// Envelope for smooth sound
			const now = audioContext.currentTime + beep.startTime;
			gainNode.gain.setValueAtTime(0, now);
			gainNode.gain.linearRampToValueAtTime(0.3, now + 0.01); // Attack
			gainNode.gain.exponentialRampToValueAtTime(0.01, now + beep.duration); // Decay
			
			oscillator.start(now);
			oscillator.stop(now + beep.duration);
		});
		
		console.log('[KitchenSync] 🔔 Playing alert sound (Web Audio API)');
		
	} catch (error) {
		console.log('[KitchenSync] Web Audio API failed, trying audio file...', error);
		
		// Fallback: Try to play audio file
		try {
			const audio = new Audio('/notification.mp3');
			audio.volume = 0.8; // Louder volume
			audio.play().catch((err) => {
				console.log('[KitchenSync] Audio file playback failed:', err);
			});
		} catch (err) {
			console.log('[KitchenSync] Notification sound not available:', err);
		}
	}
}

/**
 * Show browser notification for new order
 * @param {Object} order - Order data
 */
function showOrderNotification(order) {
	// Check if browser supports notifications
	if (!('Notification' in window)) {
		console.log('[KitchenSync] Browser does not support notifications');
		return;
	}

	// Check notification permission
	if (Notification.permission === 'granted') {
		const notification = new Notification('🍽️ Order Baru!', {
			body: `Order #${order.order_number}\n${order.items?.length || 0} items - ${order.tenant || 'Unknown tenant'}`,
			icon: '/logo.png',
			badge: '/logo.png',
			tag: order.order_number,
			requireInteraction: true // Keep notification until clicked
		});

		notification.onclick = () => {
			window.focus();
			notification.close();
		};
	} else if (Notification.permission !== 'denied') {
		// Request permission
		Notification.requestPermission().then((permission) => {
			if (permission === 'granted') {
				showOrderNotification(order); // Try again
			}
		});
	}
}

/**
 * Register callback for new orders
 * @param {Function} callback - Callback function(order)
 */
export function onNewOrder(callback) {
	onNewOrderCallback = callback;
}

/**
 * Register callback for order status updates
 * @param {Function} callback - Callback function(statusUpdate)
 */
export function onOrderStatus(callback) {
	onOrderStatusCallback = callback;
}

/**
 * Clear all orders from store
 */
export function clearNewOrders() {
	newOrders.set([]);
}

/**
 * Remove specific order from store
 * @param {string} orderNumber - Order number to remove
 */
export function removeOrder(orderNumber) {
	newOrders.update((orders) => {
		return orders.filter((order) => order.order_number !== orderNumber);
	});
}

/**
 * Get connection status
 */
export function getSyncServerStatus() {
	return {
		connected: ws && ws.readyState === WebSocket.OPEN,
		readyState: ws ? ws.readyState : null,
		reconnectAttempts: reconnectAttempts
	};
}

/**
 * Send acknowledgment to sync server
 * @param {string} orderNumber - Order number to acknowledge
 */
export function acknowledgeOrder(orderNumber) {
	if (ws && ws.readyState === WebSocket.OPEN) {
		ws.send(
			JSON.stringify({
				type: 'order_ack',
				timestamp: new Date().toISOString(),
				data: {
					order_number: orderNumber,
					acknowledged_by: 'kitchen_display',
					acknowledged_at: new Date().toISOString()
				}
			})
		);
		console.log('[KitchenSync] 📤 Sent acknowledgment for order:', orderNumber);
	}
}

// Auto-connect on module load (optional - can be disabled)
if (typeof window !== 'undefined') {
	// Only connect in browser (not during SSR)
	connectToSyncServer();

	// Request notification permission on load
	if ('Notification' in window && Notification.permission === 'default') {
		Notification.requestPermission().then((permission) => {
			console.log('[KitchenSync] Notification permission:', permission);
		});
	}
}
