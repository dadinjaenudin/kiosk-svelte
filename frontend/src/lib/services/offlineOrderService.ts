/**
 * Offline Order Service
 * 
 * Manages order persistence using IndexedDB for offline mode support.
 * Handles order queue, sync tracking, and conflict resolution.
 * 
 * Features:
 * - IndexedDB storage with Dexie.js
 * - Offline order queue management
 * - Sync queue with priority
 * - FIFO order processing
 * - Conflict detection
 * - ULID for unique sortable IDs (offline-safe)
 * - Price snapshot validation (F&B requirement)
 */

import Dexie, { type Table } from 'dexie';
import { browser } from '$app/environment';
import { ulid } from 'ulid';

/**
 * Validate order snapshot integrity
 * Ensures all prices are frozen values, not references
 */
export function validateOrderSnapshot(order: any): { valid: boolean; errors: string[] } {
	const errors: string[] = [];

	// Validate total_amount exists and is a number
	if (typeof order.total_amount !== 'number' || isNaN(order.total_amount)) {
		errors.push('total_amount must be a valid number');
	}

	// Validate subtotal exists
	if (typeof order.subtotal !== 'number' || isNaN(order.subtotal)) {
		errors.push('subtotal must be a valid number');
	}

	// Validate items exist
	if (!order.items || !Array.isArray(order.items) || order.items.length === 0) {
		errors.push('items array is required and must not be empty');
	} else {
		// Validate each item
		order.items.forEach((item: any, index: number) => {
			// Price must be snapshot (number), not reference
			if (typeof item.price !== 'number' || isNaN(item.price)) {
				errors.push(`Item ${index}: price must be a frozen number (snapshot)`);
			}

			// Quantity validation
			if (typeof item.quantity !== 'number' || item.quantity <= 0) {
				errors.push(`Item ${index}: quantity must be a positive number`);
			}

			// Product name must be snapshot
			if (!item.product_name || typeof item.product_name !== 'string') {
				errors.push(`Item ${index}: product_name is required (snapshot)`);
			}

			// Subtotal validation (if exists)
			if (item.subtotal !== undefined) {
				if (typeof item.subtotal !== 'number' || isNaN(item.subtotal)) {
					errors.push(`Item ${index}: subtotal must be a number`);
				}
				// Verify subtotal calculation
				const expectedSubtotal = (item.price + (item.modifiers_price || 0)) * item.quantity;
				if (Math.abs(item.subtotal - expectedSubtotal) > 0.01) {
					errors.push(`Item ${index}: subtotal mismatch (expected ${expectedSubtotal}, got ${item.subtotal})`);
				}
			}

			// Validate modifiers snapshot
			if (item.modifiers && Array.isArray(item.modifiers)) {
				item.modifiers.forEach((mod: any, modIndex: number) => {
					if (typeof mod.price !== 'number') {
						errors.push(`Item ${index}, Modifier ${modIndex}: price must be a frozen number`);
					}
					if (!mod.name || typeof mod.name !== 'string') {
						errors.push(`Item ${index}, Modifier ${modIndex}: name is required`);
					}
				});
			}
		});
	}

	// Validate payment_method
	if (!order.payment_method || typeof order.payment_method !== 'string') {
		errors.push('payment_method is required');
	}

	// Validate created_at timestamp
	if (!order.created_at || typeof order.created_at !== 'string') {
		errors.push('created_at timestamp is required');
	}

	return {
		valid: errors.length === 0,
		errors
	};
}

export interface OfflineOrder {
	id?: number; // Auto-increment local ID
	order_number: string;
	group_number?: string;
	outlet_id: number;
	tenant_id: number;
	store_id: number;
	customer_name: string;
	customer_phone?: string;
	customer_email?: string;
	payment_method: string;
	status: string;
	items: OrderItem[];
	subtotal: number;
	tax: number;
	service_charge: number;
	total_amount: number;
	created_at: string;
	synced: boolean;
	sync_attempts: number;
	last_sync_attempt?: string;
	error_message?: string;
}

export interface OrderItem {
	product_id: number;
	product_name: string;
	quantity: number;
	price: number;
	modifiers?: OrderModifier[];
	special_instructions?: string;
	total: number;
}

export interface OrderModifier {
	modifier_id: number;
	modifier_name: string;
	price: number;
}

export interface SyncQueueItem {
	id?: number; // Auto-increment
	type: 'ORDER_CREATE' | 'ORDER_UPDATE' | 'STATUS_CHANGE';
	priority: 'critical' | 'high' | 'normal' | 'low';
	order_number: string;
	data: any;
	timestamp: number;
	retries: number;
	max_retries: number;
	last_error?: string;
}

/**
 * IndexedDB Database using Dexie
 */
class OfflineDatabase extends Dexie {
	orders!: Table<OfflineOrder, number>;
	syncQueue!: Table<SyncQueueItem, number>;

	constructor() {
		super('KioskOfflineDB');

		// Only initialize in browser
		if (browser) {
			// Define schema version 1
			this.version(1).stores({
				orders: '++id, order_number, outlet_id, tenant_id, store_id, created_at, synced',
				syncQueue: '++id, type, priority, order_number, timestamp, retries'
			});
		}
	}
}

// Singleton database instance (only created in browser)
const db = browser ? new OfflineDatabase() : null;

/**
 * Offline Order Service Class
 */
class OfflineOrderService {
	private db: OfflineDatabase | null;

	constructor() {
		this.db = db;
	}

	/**
	 * Save order to IndexedDB (offline mode)
	 */
	async saveOrder(order: Omit<OfflineOrder, 'id' | 'synced' | 'sync_attempts'>): Promise<number> {
		if (!this.db) {
			console.warn('💾 IndexedDB not available (SSR mode)');
			return -1;
		}

		try {
			const offlineOrder: OfflineOrder = {
				...order,
				synced: false,
				sync_attempts: 0,
				created_at: order.created_at || new Date().toISOString()
			};

			const id = await this.db.orders.add(offlineOrder);
			console.log('💾 Order saved offline:', order.order_number, 'ID:', id);

			// Broadcast to Local Sync Server for kitchen displays in LAN
			if (typeof window !== 'undefined') {
				try {
					const { socketService } = await import('./socketService');
					socketService.emitToLocal('order:created:offline', offlineOrder);
					console.log('📡 Broadcasted offline order to Local Sync Server:', order.order_number);
				} catch (err) {
					console.warn('⚠️ Failed to broadcast offline order:', err);
				}
			}

			// Add to sync queue
			await this.addToSyncQueue({
				type: 'ORDER_CREATE',
				priority: 'critical',
				order_number: order.order_number,
				data: offlineOrder,
				timestamp: Date.now(),
				retries: 0,
				max_retries: 5
			});

			return id;
		} catch (error) {
			console.error('❌ Failed to save order offline:', error);
			throw error;
		}
	}

	/**
	 * Get all offline orders (not synced)
	 */
	async getOfflineOrders(): Promise<OfflineOrder[]> {
		if (!this.db) return [];

		try {
			// Get all orders and filter for unsynced (handles 0, false, undefined, null)
			const allOrders = await this.db.orders.toArray();
			const unsyncedOrders = allOrders.filter(order => !order.synced);

			console.log(`📋 Found ${unsyncedOrders.length} unsynced orders (out of ${allOrders.length} total)`);
			
			return unsyncedOrders;
		} catch (error) {
			console.error('❌ Failed to get offline orders:', error);
			return [];
		}
	}

	/**
	 * Get order by order number
	 */
	async getOrderByNumber(orderNumber: string): Promise<OfflineOrder | undefined> {
		if (!this.db) return undefined;

		try {
			return await this.db.orders
				.where('order_number')
				.equals(orderNumber)
				.first();
		} catch (error) {
			console.error('❌ Failed to get order:', error);
			return undefined;
		}
	}

	/**
	 * Mark order as synced
	 */
	async markOrderSynced(orderNumber: string): Promise<void> {
		if (!this.db) return;

		try {
			await this.db.orders
				.where('order_number')
				.equals(orderNumber)
				.modify({
					synced: true,
					last_sync_attempt: new Date().toISOString()
				});

			console.log('✅ Order marked as synced:', orderNumber);
		} catch (error) {
			console.error('❌ Failed to mark order as synced:', error);
		}
	}

	/**
	 * Update sync attempt count
	 */
	async incrementSyncAttempt(orderNumber: string, errorMessage?: string): Promise<void> {
		if (!this.db) return;

		try {
			const order = await this.getOrderByNumber(orderNumber);
			if (!order) return;

			await this.db.orders
				.where('order_number')
				.equals(orderNumber)
				.modify({
					sync_attempts: (order.sync_attempts || 0) + 1,
					last_sync_attempt: new Date().toISOString(),
					error_message: errorMessage
				});

			console.log(`🔄 Sync attempt #${(order.sync_attempts || 0) + 1} for order:`, orderNumber);
		} catch (error) {
			console.error('❌ Failed to increment sync attempt:', error);
		}
	}

	/**
	 * Add item to sync queue
	 */
	async addToSyncQueue(item: Omit<SyncQueueItem, 'id'>): Promise<number> {
		if (!this.db) return -1;

		try {
			const id = await this.db.syncQueue.add(item as SyncQueueItem);
			console.log('📥 Added to sync queue:', item.type, item.order_number);
			return id;
		} catch (error) {
			console.error('❌ Failed to add to sync queue:', error);
			throw error;
		}
	}

	/**
	 * Get pending sync queue items (FIFO order, by priority)
	 */
	async getSyncQueue(): Promise<SyncQueueItem[]> {
		if (!this.db) {
			console.log('❌ Database not initialized');
			return [];
		}

		try {
			// console.log('🔍 Checking sync queue...');
			const items = await this.db.syncQueue
				.orderBy('timestamp')
				.toArray();

			// console.log(`📊 Found ${items.length} items in sync queue:`, items);

			// Sort by priority: critical > high > normal > low
			const priorityOrder = { critical: 1, high: 2, normal: 3, low: 4 };
			return items.sort((a, b) => {
				return priorityOrder[a.priority] - priorityOrder[b.priority];
			});
		} catch (error) {
			console.error('❌ Failed to get sync queue:', error);
			return [];
		}
	}

	/**
	 * Remove item from sync queue (after successful sync)
	 */
	async removeSyncQueueItem(id: number): Promise<void> {
		if (!this.db) return;

		try {
			await this.db.syncQueue.delete(id);
			console.log('✅ Removed from sync queue, ID:', id);
		} catch (error) {
			console.error('❌ Failed to remove sync queue item:', error);
		}
	}

	/**
	 * Update sync queue item retry count
	 */
	async incrementSyncQueueRetry(id: number, errorMessage: string): Promise<void> {
		if (!this.db) return;

		try {
			const item = await this.db.syncQueue.get(id);
			if (!item) return;

			const newRetries = (item.retries || 0) + 1;

			if (newRetries >= item.max_retries) {
				// Max retries reached, remove from queue
				console.warn('⚠️ Max retries reached for sync item:', item.order_number);
				await this.removeSyncQueueItem(id);
			} else {
				// Increment retry count
				await this.db.syncQueue.update(id, {
					retries: newRetries,
					last_error: errorMessage
				});
				console.log(`🔄 Retry #${newRetries} for sync item:`, item.order_number);
			}
		} catch (error) {
			console.error('❌ Failed to update sync queue retry:', error);
		}
	}

	/**
	 * Get statistics
	 */
	async getStats(): Promise<{
		totalOrders: number;
		syncedOrders: number;
		pendingOrders: number;
		syncQueueSize: number;
		failedSyncs: number;
	}> {
		try {
			// Get all orders and count synced/unsynced properly
			const allOrders = await this.db.orders.toArray();
			const totalOrders = allOrders.length;
			const syncedOrders = allOrders.filter(o => o.synced).length;
			const pendingOrders = allOrders.filter(o => !o.synced).length;
			const syncQueueSize = await this.db.syncQueue.count();

			// Stats displayed in ConnectionStatus widget
			// console.log('📊 IndexedDB Stats:', {
			// 	totalOrders,
			// 	syncedOrders,
			// 	pendingOrders,
			// 	syncQueueSize
			// });

			// Count failed syncs (sync_attempts > 3)
			const failedSyncs = allOrders.filter(o => !o.synced && (o.sync_attempts || 0) > 3).length;

			return {
				totalOrders,
				syncedOrders,
				pendingOrders,
				syncQueueSize,
				failedSyncs
			};
		} catch (error) {
			console.error('❌ Failed to get stats:', error);
			return {
				totalOrders: 0,
				syncedOrders: 0,
				pendingOrders: 0,
				syncQueueSize: 0,
				failedSyncs: 0
			};
		}
	}

	/**
	 * Clear all synced orders (cleanup old data)
	 */
	async clearSyncedOrders(olderThanDays = 7): Promise<number> {
		if (!this.db) return 0;

		try {
			const cutoffDate = new Date();
			cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);

			const deleted = await this.db.orders
				.where('synced')
				.equals(1)
				.and(order => new Date(order.created_at) < cutoffDate)
				.delete();

			console.log(`🗑️ Cleared ${deleted} synced orders older than ${olderThanDays} days`);
			return deleted;
		} catch (error) {
			console.error('❌ Failed to clear synced orders:', error);
			return 0;
		}
	}

	/**
	 * Rebuild sync queue from unsynced orders
	 * Use this to recover from sync queue being cleared
	 */
	async rebuildSyncQueue(): Promise<number> {
		if (!this.db) return 0;

		try {
			console.log('🔧 Rebuilding sync queue from unsynced orders...');

			// Get all unsynced orders
			const unsyncedOrders = await this.getOfflineOrders();
			
			if (unsyncedOrders.length === 0) {
				console.log('✅ No unsynced orders to rebuild');
				return 0;
			}

			console.log(`📦 Found ${unsyncedOrders.length} unsynced orders`);

			// Clear existing queue first
			await this.db.syncQueue.clear();

			// Add each order to sync queue
			let added = 0;
			for (const order of unsyncedOrders) {
				await this.addToSyncQueue({
					type: 'ORDER_CREATE',
					order_number: order.order_number,
					priority: 'high',
					timestamp: new Date(order.created_at).getTime(),
					retryCount: order.sync_attempts || 0
				});
				added++;
			}

			console.log(`✅ Rebuilt sync queue: ${added} items added`);
			return added;
		} catch (error) {
			console.error('❌ Failed to rebuild sync queue:', error);
			return 0;
		}
	}

	/**
	 * Clear entire database (for testing)
	 */
	async clearAll(): Promise<void> {
		if (!this.db) return;

		try {
			await this.db.orders.clear();
			await this.db.syncQueue.clear();
			console.log('🗑️ All offline data cleared');
		} catch (error) {
			console.error('❌ Failed to clear database:', error);
		}
	}

	/**
	 * Get database instance (for advanced queries)
	 */
	getDatabase(): OfflineDatabase | null {
		return this.db;
	}
}

// Singleton instance
export const offlineOrderService = new OfflineOrderService();

// Export database for direct access if needed
export { db as offlineDB };
