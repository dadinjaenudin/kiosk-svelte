/**
 * Socket.IO Client Service
 * 
 * Manages WebSocket connections to both Central Server and Local Sync Server
 * with automatic failover and room-based broadcasting support.
 * 
 * Features:
 * - Dual connection support (Central + Local)
 * - Auto-reconnect with exponential backoff
 * - Room-based broadcasting per outlet
 * - Event handlers for orders (created, updated, completed, cancelled)
 * - Connection status tracking
 * - Type-safe event emitters
 */

import { writable, type Writable } from 'svelte/store';
import { io, type Socket } from 'socket.io-client';
import { PUBLIC_API_URL } from '$env/static/public';
import { browser } from '$app/environment';
import type { KitchenOrder } from '$lib/stores/kitchenStore';

export type SocketMode = 'central' | 'local' | 'dual' | 'polling' | 'none';

export interface SocketStatus {
	centralConnected: boolean;
	localConnected: boolean;
	mode: SocketMode;
	lastConnectTime: Date | null;
	reconnectAttempts: number;
	isPolling: boolean;
}

export interface OrderEventData {
	id: number;
	order_number: string;
	outlet_id: number;
	tenant_id?: number;
	status: string;
	items: any[];
	total_amount: string;
	customer?: {
		name: string;
		phone?: string;
	};
	created_at: string;
}

export interface StatusUpdateData {
	id: number;
	order_number: string;
	status: string;
	outlet_id: number;
	tenant_id?: number;
	updated_at: string;
}

export type OrderEventHandler = (order: KitchenOrder) => void;
export type StatusUpdateHandler = (update: StatusUpdateData) => void;

class SocketService {
	private centralSocket: Socket | null = null;
	private localSocket: Socket | null = null;
	private status: Writable<SocketStatus>;
	private eventHandlers: Map<string, Set<Function>> = new Map();
	
	// Configuration
	private readonly CENTRAL_URL: string;
	private readonly LOCAL_URL = 'http://localhost:3001'; // Local Sync Server
	private readonly RECONNECT_ATTEMPTS = 5;
	private readonly RECONNECT_DELAY = 3000;
	
	// Polling mechanism (fallback when WebSocket unavailable)
	private pollingInterval: NodeJS.Timeout | null = null;
	private readonly POLLING_INTERVAL = 3000; // Poll every 3 seconds
	private lastPolledOrderId: number | null = null;

	constructor() {
		// Parse Central Server URL for Socket.IO
		this.CENTRAL_URL = PUBLIC_API_URL.replace('/api', '');

		this.status = writable<SocketStatus>({
			centralConnected: false,
			localConnected: false,
			mode: 'none',
			lastConnectTime: null,
			reconnectAttempts: 0,
			isPolling: false
		});
	}

	/**
	 * Connect to Central Server Socket.IO
	 * TEMPORARY: Disabled because Django Channels doesn't support Socket.IO protocol
	 * TODO: Either use Django Channels native WebSocket or install python-socketio
	 */
	connectCentral(): void {
		if (!browser) {
			console.warn('🔴 Cannot connect to Central Socket: Not in browser context');
			return;
		}

		// TEMPORARY DISABLED: Django Channels doesn't support Socket.IO
		console.log('ℹ️ Central Server WebSocket unavailable (using HTTP polling instead)');
		console.log('   Django Channels uses native WebSocket, not Socket.IO protocol');
		console.log('   Kitchen display will use HTTP polling for order updates');
		
		// Mark as unavailable and use polling mode
		this.updateStatus({
			centralConnected: false,
			mode: 'polling',
			isPolling: false // Will be set to true when polling starts
		});
		
		return;

		/* ORIGINAL CODE - Re-enable when Socket.IO is properly configured
		if (this.centralSocket?.connected) {
			console.log('🟢 Central Socket: Already connected');
			return;
		}

		console.log('🔄 Connecting to Central Socket.IO:', this.CENTRAL_URL);

		this.centralSocket = io(this.CENTRAL_URL, {
			transports: ['websocket', 'polling'],
			reconnection: true,
			reconnectionAttempts: this.RECONNECT_ATTEMPTS,
			reconnectionDelay: this.RECONNECT_DELAY,
			timeout: 10000
		});

		this.setupCentralHandlers();
		*/
	}

	/**
	 * Connect to Local Sync Server Socket.IO
	 * Returns a Promise that resolves when connected
	 */
	connectLocal(): Promise<void> {
		return new Promise((resolve, reject) => {
			if (!browser) {
				console.warn('🔴 Cannot connect to Local Socket: Not in browser context');
				reject(new Error('Not in browser context'));
				return;
			}

			if (this.localSocket?.connected) {
				console.log('🟢 Local Socket: Already connected');
				resolve();
				return;
			}

			console.log('🔄 Connecting to Local Socket.IO:', this.LOCAL_URL);
			console.log('🔍 Connection config:', {
				url: this.LOCAL_URL,
				transports: ['websocket', 'polling'],
				reconnection: true
			});

			this.localSocket = io(this.LOCAL_URL, {
				transports: ['websocket', 'polling'],
				reconnection: true,
				reconnectionAttempts: this.RECONNECT_ATTEMPTS,
				reconnectionDelay: this.RECONNECT_DELAY,
				timeout: 5000
			});

			// Setup handlers first
			this.setupLocalHandlers();

			// Wait for connection or timeout
			const timeout = setTimeout(() => {
				console.warn('⚠️ Local Socket: Connection timeout, resolving anyway (will retry in background)');
				console.warn('   Check if Local Sync Server is running on port 3001');
				resolve();
			}, 6000); // 6 seconds timeout

			// Resolve when connected
			this.localSocket.once('connect', () => {
				console.log('✅ Local Socket: Connected successfully!');
				clearTimeout(timeout);
				resolve();
			});

			// Reject on immediate error (but auto-reconnect will continue)
			this.localSocket.once('connect_error', (error) => {
				// Don't reject, just warn - socket.io will auto-retry
				console.warn('⚠️ Local Socket: Initial connection error, will auto-retry:', error.message);
				console.warn('   Make sure Local Sync Server is running: cd local-sync-server && npm run dev');
			});
		});
	}

	/**
	 * Setup Central Socket event handlers
	 */
	private setupCentralHandlers(): void {
		if (!this.centralSocket) return;

		// Connection events
		this.centralSocket.on('connect', () => {
			console.log('✅ Central Socket: Connected', this.centralSocket?.id);
			this.updateStatus({
				centralConnected: true,
				lastConnectTime: new Date(),
				reconnectAttempts: 0
			});
			this.updateMode();
		});

		this.centralSocket.on('disconnect', (reason) => {
			console.log('❌ Central Socket: Disconnected', reason);
			this.updateStatus({
				centralConnected: false
			});
			this.updateMode();
		});

		this.centralSocket.on('connect_error', (error) => {
			// Suppress repetitive WebSocket errors (expected when Django doesn't have Socket.IO)
			this.status.update(s => {
				const newAttempts = s.reconnectAttempts + 1;
				// Only log on first attempt and every 10th attempt to reduce noise
				if (newAttempts === 1 || newAttempts % 10 === 0) {
					console.info('ℹ️ Central Server WebSocket unavailable (using HTTP polling instead)');
				}
				return { ...s, reconnectAttempts: newAttempts };
			});
		});

		// Custom events
		this.centralSocket.on('connected', (data) => {
			console.log('🟢 Central Server welcome:', data);
		});

		// Order events
		this.centralSocket.on('order_created', (order: OrderEventData) => {
			console.log('📦 Central: New order', order.order_number);
			this.emit('order_created', order);
		});

		this.centralSocket.on('order_updated', (update: StatusUpdateData) => {
			console.log('🔄 Central: Order updated', update.order_number, update.status);
			this.emit('order_updated', update);
		});

		this.centralSocket.on('order_completed', (order: OrderEventData) => {
			console.log('✅ Central: Order completed', order.order_number);
			this.emit('order_completed', order);
		});

		this.centralSocket.on('order_cancelled', (order: OrderEventData) => {
			console.log('❌ Central: Order cancelled', order.order_number);
			this.emit('order_cancelled', order);
		});
	}

	/**
	 * Setup Local Socket event handlers
	 */
	private setupLocalHandlers(): void {
		if (!this.localSocket) return;

		// Connection events
		this.localSocket.on('connect', () => {
			console.log('✅ Local Socket: Connected', this.localSocket?.id);
			this.updateStatus({
				localConnected: true,
				lastConnectTime: new Date(),
				reconnectAttempts: 0
			});
			this.updateMode();
		});

		this.localSocket.on('disconnect', (reason) => {
			console.log('❌ Local Socket: Disconnected', reason);
			this.updateStatus({
				localConnected: false
			});
			this.updateMode();
		});

		this.localSocket.on('connect_error', (error) => {
			console.error('❌ Local Socket: Connection error', error.message);
			this.status.update(s => ({
				...s,
				reconnectAttempts: s.reconnectAttempts + 1
			}));
		});

		// Custom events
		this.localSocket.on('connected', (data) => {
			console.log('🟢 Local Server welcome:', data);
		});

		this.localSocket.on('subscribed', (data) => {
			console.log('📍 Subscribed to outlet:', data.outletId);
		});

		// Order events (from Local Server)
		this.localSocket.on('order_created', (order: OrderEventData) => {
			console.log('📦 Local: New order', order.order_number);
			this.emit('order_created', order);
		});

		this.localSocket.on('order_updated', (update: StatusUpdateData) => {
			console.log('🔄 Local: Order updated', update.order_number, update.status);
			this.emit('order_updated', update);
		});

		this.localSocket.on('order_completed', (order: OrderEventData) => {
			console.log('✅ Local: Order completed', order.order_number);
			this.emit('order_completed', order);
		});

		this.localSocket.on('order_cancelled', (order: OrderEventData) => {
			console.log('❌ Local: Order cancelled', order.order_number);
			this.emit('order_cancelled', order);
		});
	}

	/**
	 * Subscribe to outlet-specific room
	 */
	subscribeOutlet(outletId: number): void {
		console.log('📍 Subscribing to outlet:', outletId);

		// Subscribe on Central Socket
		if (this.centralSocket?.connected) {
			this.centralSocket.emit('subscribe_outlet', outletId);
		}

		// Subscribe on Local Socket
		if (this.localSocket?.connected) {
			this.localSocket.emit('subscribe_outlet', outletId);
		}
	}

	/**
	 * Identify client type (POS or Kitchen)
	 */
	identify(type: 'pos' | 'kitchen'): void {
		console.log('🏷️ Identifying as:', type);

		if (this.centralSocket?.connected) {
			this.centralSocket.emit('identify', { type });
		}

		if (this.localSocket?.connected) {
			this.localSocket.emit('identify', { type });
		}
	}

	/**
	 * Emit new order event
	 */
	emitNewOrder(order: OrderEventData): void {
		console.log('📤 Emitting new order:', order.order_number);

		// Emit to Central (if connected)
		if (this.centralSocket?.connected) {
			this.centralSocket.emit('new_order', order);
		}

		// Always emit to Local (for LAN Kitchen Display)
		if (this.localSocket?.connected) {
			this.localSocket.emit('new_order', order);
		} else {
			console.warn('⚠️ Local Socket not connected, order not broadcasted to Kitchen Display');
		}
	}

	/**
	 * Emit order status update
	 */
	emitStatusUpdate(update: StatusUpdateData): void {
		console.log('📤 Emitting status update:', update.order_number, update.status);

		if (this.centralSocket?.connected) {
			this.centralSocket.emit('update_status', update);
		}

		if (this.localSocket?.connected) {
			this.localSocket.emit('update_status', update);
		}
	}

	/**
	 * Update connection mode based on socket states
	 */
	private updateMode(): void {
		this.status.update(s => {
			let mode: SocketMode = 'none';

			if (s.centralConnected && s.localConnected) {
				mode = 'dual';
			} else if (s.centralConnected) {
				mode = 'central';
			} else if (s.localConnected) {
				mode = 'local';
			}

			return { ...s, mode };
		});
	}

	/**
	 * Update status store
	 */
	private updateStatus(partial: Partial<SocketStatus>): void {
		this.status.update(current => ({
			...current,
			...partial
		}));
	}

	/**
	 * Register event handler
	 */
	on(event: string, handler: Function): void {
		if (!this.eventHandlers.has(event)) {
			this.eventHandlers.set(event, new Set());
		}
		this.eventHandlers.get(event)!.add(handler);
	}

	/**
	 * Unregister event handler
	 */
	off(event: string, handler: Function): void {
		this.eventHandlers.get(event)?.delete(handler);
	}

	/**
	 * Emit event to all registered handlers
	 */
	private emit(event: string, data: any): void {
		this.eventHandlers.get(event)?.forEach(handler => {
			try {
				handler(data);
			} catch (error) {
				console.error(`Error in ${event} handler:`, error);
			}
		});
	}

	/**
	 * Get socket status store
	 */
	getStatus() {
		return this.status;
	}

	/**
	 * Emit event to Local Sync Server
	 */
	emitToLocal(event: string, data: any): void {
		if (!this.localSocket) {
			console.warn('⚠️ Cannot emit to Local Server: Socket not initialized');
			return;
		}
		
		if (!this.localSocket.connected) {
		console.warn('⚠️ Cannot emit to Local Server: Not connected');
			this.localSocket.connect();
			return;
		}

		// Emit to Local Sync Server
		console.log('📤 Emitting to Local Server:', event, data);
		this.localSocket.emit(event, data);
	}

	/**
	 * Emit event to Central Server
	 */
	emitToCentral(event: string, data: any): void {
		if (!this.centralSocket?.connected) {
			console.warn('⚠️ Cannot emit to Central Server: Not connected');
			return;
		}

		// Emit to Central Server
		this.centralSocket.emit(event, data);
	}

	/**
	 * Register event listener on Local Socket
	 */
	onLocal(event: string, handler: (data: any) => void): void {
		if (!this.localSocket) {
			console.warn(`⚠️ Cannot register listener for ${event}: Local Socket not initialized`);
			return;
		}

		this.localSocket.on(event, handler);
	}

	/**
	 * Register event listener on Central Socket
	 */
	onCentral(event: string, handler: (data: any) => void): void {
		if (!this.centralSocket) {
			console.warn(`⚠️ Cannot register listener for ${event}: Central Socket not initialized`);
			return;
		}

		this.centralSocket.on(event, handler);
	}

	/**
	 * Disconnect all sockets
	 */
	disconnect(): void {
		console.log('🛑 Disconnecting all sockets...');

		if (this.centralSocket) {
			this.centralSocket.disconnect();
			this.centralSocket = null;
		}

		if (this.localSocket) {
			this.localSocket.disconnect();
			this.localSocket = null;
		}

		this.stopPolling();

		this.updateStatus({
			centralConnected: false,
			localConnected: false,
			mode: 'none'
		});
	}

	/**
	 * Start polling to Local Server (fallback when WebSocket unavailable)
	 */
	startPolling(outletId: number): void {
		if (!browser) {
			console.warn('🔴 Cannot start polling: Not in browser context');
			return;
		}

		if (this.pollingInterval) {
			console.log('⚠️ Polling already active');
			return;
		}

		console.log(`🔄 Starting polling to Local Server (outlet ${outletId}) every ${this.POLLING_INTERVAL}ms`);

		this.status.update(s => ({ ...s, isPolling: true, mode: 'polling' }));

		// Initial poll
		this.pollLocalServer(outletId);

		// Start interval
		this.pollingInterval = setInterval(() => {
			this.pollLocalServer(outletId);
		}, this.POLLING_INTERVAL);
	}

	/**
	 * Stop polling
	 */
	stopPolling(): void {
		if (this.pollingInterval) {
			console.log('🛑 Stopping polling to Local Server');
			clearInterval(this.pollingInterval);
			this.pollingInterval = null;
			this.lastPolledOrderId = null;
			this.status.update(s => ({ ...s, isPolling: false }));
		}
	}

	/**
	 * Poll Local Server for new orders
	 */
	private async pollLocalServer(outletId: number): Promise<void> {
		try {
			// Construct URL with last order ID if available
			let url = `${this.LOCAL_URL}/api/orders?outlet_id=${outletId}`;
			if (this.lastPolledOrderId) {
				url += `&since_id=${this.lastPolledOrderId}`;
			}

			const response = await fetch(url, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				console.warn(`⚠️ Polling failed: ${response.statusText}`);
				return;
			}

			const orders: OrderEventData[] = await response.json();

			// Emit new orders to handlers
			if (orders.length > 0) {
				console.log(`📦 Polled ${orders.length} new orders from Local Server`);

				orders.forEach(order => {
					// Update last polled ID
					if (order.id > (this.lastPolledOrderId || 0)) {
						this.lastPolledOrderId = order.id;
					}

					// Emit to handlers (simulate 'new_order' event)
					this.emitToHandlers('new_order', order);
				});
			}

		} catch (error) {
			console.error('❌ Polling error:', error);
		}
	}

	/**
	 * Emit event to registered handlers
	 */
	private emitToHandlers(event: string, data: any): void {
		const handlers = this.eventHandlers.get(event);
		if (handlers) {
			handlers.forEach(handler => {
				try {
					handler(data);
				} catch (error) {
					console.error(`Error in handler for ${event}:`, error);
				}
			});
		}
	}

	/**
	 * Cleanup (for component unmount)
	 */
	destroy(): void {
		this.disconnect();
		this.eventHandlers.clear();
		console.log('🛑 Socket Service destroyed');
	}
}

// Singleton instance
export const socketService = new SocketService();

// Export status store
export const socketStatus = socketService.getStatus();
