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
import type { KitchenOrder } from '$lib/stores/kitchenStore';

export type SocketMode = 'central' | 'local' | 'dual' | 'none';

export interface SocketStatus {
	centralConnected: boolean;
	localConnected: boolean;
	mode: SocketMode;
	lastConnectTime: Date | null;
	reconnectAttempts: number;
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

	constructor() {
		// Parse Central Server URL for Socket.IO
		this.CENTRAL_URL = PUBLIC_API_URL.replace('/api', '');

		this.status = writable<SocketStatus>({
			centralConnected: false,
			localConnected: false,
			mode: 'none',
			lastConnectTime: null,
			reconnectAttempts: 0
		});
	}

	/**
	 * Connect to Central Server Socket.IO
	 */
	connectCentral(): void {
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
	}

	/**
	 * Connect to Local Sync Server Socket.IO
	 */
	connectLocal(): void {
		if (this.localSocket?.connected) {
			console.log('🟢 Local Socket: Already connected');
			return;
		}

		console.log('🔄 Connecting to Local Socket.IO:', this.LOCAL_URL);

		this.localSocket = io(this.LOCAL_URL, {
			transports: ['websocket', 'polling'],
			reconnection: true,
			reconnectionAttempts: this.RECONNECT_ATTEMPTS,
			reconnectionDelay: this.RECONNECT_DELAY,
			timeout: 5000
		});

		this.setupLocalHandlers();
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
			console.error('❌ Central Socket: Connection error', error.message);
			this.status.update(s => ({
				...s,
				reconnectAttempts: s.reconnectAttempts + 1
			}));
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

		this.updateStatus({
			centralConnected: false,
			localConnected: false,
			mode: 'none'
		});
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
