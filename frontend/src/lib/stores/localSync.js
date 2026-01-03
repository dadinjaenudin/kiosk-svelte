/**
 * Local Sync Store - POS Side
 * Broadcasts orders to Kitchen Sync Server (local network WebSocket)
 * for real-time kitchen display updates when offline
 */

import { writable, get } from 'svelte/store';

// WebSocket connection state
export const syncServerConnected = writable(false);

// Outlet settings with WebSocket URL
export const outletSettings = writable(null);

// Pending messages queue (if disconnected)
const messageQueue = [];

let ws = null;
let reconnectTimer = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY = 3000; // 3 seconds

// Default fallback
const DEFAULT_SYNC_SERVER_URL = 'ws://localhost:3001';

/**
 * Get WebSocket URL from outlet settings or fallback
 */
function getWebSocketURL() {
	const settings = get(outletSettings);
	const wsUrl = settings?.websocket_url || DEFAULT_SYNC_SERVER_URL;
	console.log('[LocalSync] Using WebSocket URL:', wsUrl);
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
			console.log('[LocalSync] Outlet settings loaded:', {
				outlet: data.name,
				websocket_url: data.websocket_url
			});
			return data;
		}
	} catch (error) {
		console.error('[LocalSync] Failed to load outlet settings:', error);
	}
	return null;
}

/**
 * Connect to Kitchen Sync Server
 */
export function connectToSyncServer() {
	if (ws && ws.readyState === WebSocket.OPEN) {
		console.log('[LocalSync] Already connected');
		return;
	}

	const SYNC_SERVER_URL = getWebSocketURL();
	console.log(`[LocalSync] Connecting to ${SYNC_SERVER_URL}...`);

	try {
		ws = new WebSocket(SYNC_SERVER_URL);

		ws.onopen = () => {
			console.log('[LocalSync] ✅ Connected to Kitchen Sync Server');
			syncServerConnected.set(true);
			reconnectAttempts = 0;

			// Send queued messages
			if (messageQueue.length > 0) {
				console.log(`[LocalSync] Sending ${messageQueue.length} queued messages...`);
				while (messageQueue.length > 0) {
					const message = messageQueue.shift();
					ws.send(JSON.stringify(message));
				}
			}
		};

		ws.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);
				console.log('[LocalSync] Received:', data.type, data);

				// Handle acknowledgments
				if (data.type === 'ack') {
					console.log(`[LocalSync] ✅ Server acknowledged: ${data.messageType}`);
				}

				// Handle connection confirmation
				if (data.type === 'connected') {
					console.log('[LocalSync] ✅ Server welcome:', data.message);
				}
			} catch (error) {
				console.error('[LocalSync] Error parsing message:', error);
			}
		};

		ws.onerror = (error) => {
			console.error('[LocalSync] ❌ WebSocket error:', error);
			syncServerConnected.set(false);
		};

		ws.onclose = () => {
			console.log('[LocalSync] 📴 Disconnected from Kitchen Sync Server');
			syncServerConnected.set(false);
			ws = null;

			// Attempt to reconnect
			if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
				reconnectAttempts++;
				console.log(
					`[LocalSync] ⏳ Reconnecting in ${RECONNECT_DELAY / 1000}s (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`
				);
				reconnectTimer = setTimeout(connectToSyncServer, RECONNECT_DELAY);
			} else {
				console.log('[LocalSync] ⚠️ Max reconnect attempts reached. Please check server.');
			}
		};
	} catch (error) {
		console.error('[LocalSync] Error creating WebSocket:', error);
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
	console.log('[LocalSync] 👋 Disconnected');
}

/**
 * Broadcast new order to Kitchen Sync Server
 * @param {Object} order - Order data
 */
export function broadcastNewOrder(order) {
	const message = {
		type: 'new_order',
		timestamp: new Date().toISOString(),
		data: {
			order_number: order.order_number,
			tenant_id: order.tenant_id || order.tenant, // API returns 'tenant', not 'tenant_id'
			tenant_name: order.tenant_name,
			tenant_color: order.tenant_color,
			items: order.items,
			total: order.total,
			status: order.status || 'pending',
			payment_status: order.payment_status || 'paid',
			payment_method: order.payment_method,
			customer_name: order.customer_name,
			customer_phone: order.customer_phone,
			table_number: order.table_number,
			notes: order.notes,
			created_at: order.created_at || new Date().toISOString()
		}
	};

	sendMessage(message);
	console.log('[LocalSync] 📤 Broadcasted new order:', order.order_number, 'for tenant:', message.data.tenant_id);
}

/**
 * Broadcast order status update to Kitchen Sync Server
 * @param {string} orderNumber - Order number
 * @param {string} status - New status (pending, preparing, ready, completed)
 */
export function broadcastOrderStatus(orderNumber, status) {
	const message = {
		type: 'order_status',
		timestamp: new Date().toISOString(),
		data: {
			order_number: orderNumber,
			status: status,
			updated_at: new Date().toISOString()
		}
	};

	sendMessage(message);
	console.log('[LocalSync] 📤 Broadcasted status update:', orderNumber, '→', status);
}

/**
 * Send message to Kitchen Sync Server
 * @param {Object} message - Message object
 */
function sendMessage(message) {
	if (ws && ws.readyState === WebSocket.OPEN) {
		ws.send(JSON.stringify(message));
	} else {
		console.warn('[LocalSync] ⚠️ Not connected, queueing message...');
		messageQueue.push(message);

		// Try to reconnect
		if (!ws || ws.readyState === WebSocket.CLOSED) {
			connectToSyncServer();
		}
	}
}

/**
 * Get connection status
 */
export function getSyncServerStatus() {
	return {
		connected: ws && ws.readyState === WebSocket.OPEN,
		readyState: ws ? ws.readyState : null,
		queuedMessages: messageQueue.length,
		reconnectAttempts: reconnectAttempts
	};
}

// Auto-connect on module load (optional - can be disabled)
if (typeof window !== 'undefined') {
	// Only connect in browser (not during SSR)
	connectToSyncServer();
}
