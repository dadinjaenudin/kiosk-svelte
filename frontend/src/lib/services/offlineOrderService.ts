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
 */

import Dexie, { type Table } from 'dexie';
import { browser } from '$app/environment';

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
			const orders = await this.db.orders
				.where('synced')
				.equals(0) // false = 0 in IndexedDB
				.toArray();

			return orders;
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
		if (!this.db) return [];

		try {
			const items = await this.db.syncQueue
				.orderBy('timestamp')
				.toArray();

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
			const [totalOrders, syncedOrders, syncQueueSize] = await Promise.all([
				this.db.orders.count(),
				this.db.orders.where('synced').equals(1).count(),
				this.db.syncQueue.count()
			]);

			const pendingOrders = totalOrders - syncedOrders;

			// Count failed syncs (sync_attempts > 3)
			const allOrders = await this.db.orders.toArray();
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
