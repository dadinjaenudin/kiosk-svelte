/**
 * Local Sync Store - POS Side
 * Broadcasts orders to Kitchen Sync Server (local network Socket.IO)
 * for real-time kitchen display updates when offline
 */

import { writable, get } from 'svelte/store';
import { io } from 'socket.io-client';

// WebSocket connection state
export const syncServerConnected = writable(false);

// Outlet settings with WebSocket URL
export const outletSettings = writable(null);

// Pending messages queue (if disconnected)
const messageQueue = [];

let socket = null;
let reconnectTimer = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY = 3000; // 3 seconds

// Default fallback - Socket.IO uses HTTP URL
const DEFAULT_SYNC_SERVER_URL = 'http://localhost:3001';

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
 * Connect to Kitchen Sync Server using Socket.IO
 */
export function connectToSyncServer() {
	if (socket && socket.connected) {
		console.log('[LocalSync] Already connected');
		return;
	}

	let SYNC_SERVER_URL = getWebSocketURL();
	
	// Convert ws:// to http:// for Socket.IO
	if (SYNC_SERVER_URL.startsWith('ws://')) {
		SYNC_SERVER_URL = SYNC_SERVER_URL.replace('ws://', 'http://');
	}
	
	console.log(`[LocalSync] Connecting to ${SYNC_SERVER_URL}...`);

	try {
		socket = io(SYNC_SERVER_URL, {
			transports: ['websocket', 'polling'],
			reconnection: false // We handle reconnection manually
		});

		socket.on('connect', () => {
			console.log('[LocalSync] ✅ Connected to Kitchen Sync Server');
			syncServerConnected.set(true);
			reconnectAttempts = 0;

			// Send queued messages
			if (messageQueue.length > 0) {
				console.log(`[LocalSync] Sending ${messageQueue.length} queued messages...`);
				while (messageQueue.length > 0) {
					const message = messageQueue.shift();
					socket.emit(message.type, message);
				}
			}
		});

		socket.on('disconnect', () => {
			console.log('[LocalSync] 📴 Disconnected from Kitchen Sync Server');
			syncServerConnected.set(false);

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
		});

		socket.on('connect_error', (error) => {
			console.error('[LocalSync] ❌ Connection error:', error.message);
			syncServerConnected.set(false);
		});

		// Handle server acknowledgments
		socket.on('ack', (data) => {
			console.log(`[LocalSync] ✅ Server acknowledged:`, data);
		});

		// Handle connection confirmation
		socket.on('connected', (data) => {
			console.log('[LocalSync] ✅ Server welcome:', data.message);
		});
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

	if (socket) {
		socket.disconnect();
		socket = null;
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
	if (socket && socket.connected) {
		socket.emit(message.type, message);
	} else {
		console.warn('[LocalSync] ⚠️ Not connected, queueing message...');
		messageQueue.push(message);

		// Try to reconnect
		if (!socket || !socket.connected) {
			connectToSyncServer();
		}
	}
}

/**
 * Get connection status
 */
export function getSyncServerStatus() {
	return {
		connected: socket && socket.connected,
		socketId: socket?.id || null,
		queuedMessages: messageQueue.length,
		reconnectAttempts: reconnectAttempts
	};
}

// Auto-connect on module load (optional - can be disabled)
if (typeof window !== 'undefined') {
	// Only connect in browser (not during SSR)
	connectToSyncServer();
}
