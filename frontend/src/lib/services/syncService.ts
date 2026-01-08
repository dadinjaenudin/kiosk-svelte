/**
 * Background Sync Service
 * 
 * Automatically syncs pending orders from IndexedDB to Central Server
 * when internet connection is restored.
 * 
 * Features:
 * - Auto-sync on network restore (every 30 seconds when online)
 * - Priority queue processing (critical orders first)
 * - Retry with exponential backoff
 * - Progress tracking
 * - Error handling and logging
 */

import { writable, derived, type Writable } from 'svelte/store';
import { PUBLIC_API_URL } from '$env/static/public';
import { offlineOrderService, type SyncQueueItem } from './offlineOrderService';
import { networkStatus } from './networkService';

export interface SyncProgress {
	isRunning: boolean;
	totalItems: number;
	processedItems: number;
	successCount: number;
	failureCount: number;
	currentItem: string | null;
	lastSyncTime: Date | null;
	errors: SyncError[];
}

export interface SyncError {
	orderNumber: string;
	errorMessage: string;
	timestamp: Date;
	retryCount: number;
}

class SyncService {
	private progress: Writable<SyncProgress>;
	private syncInterval: ReturnType<typeof setInterval> | null = null;
	private readonly SYNC_INTERVAL = 30000; // 30 seconds
	private readonly MAX_CONCURRENT_SYNCS = 3;
	private isSyncing = false;

	constructor() {
		this.progress = writable<SyncProgress>({
			isRunning: false,
			totalItems: 0,
			processedItems: 0,
			successCount: 0,
			failureCount: 0,
			currentItem: null,
			lastSyncTime: null,
			errors: []
		});

		// Listen to network status changes
		this.setupNetworkListener();
	}

	/**
	 * Setup network status listener to trigger sync when online
	 */
	private setupNetworkListener() {
		networkStatus.subscribe(status => {
			if (status.isOnline && !this.isSyncing) {
				// Network restored, trigger sync
				console.log('🟢 Network online, checking for pending orders...');
				this.triggerSync();
			}
		});
	}

	/**
	 * Start auto-sync interval
	 */
	startAutoSync() {
		if (this.syncInterval) {
			console.warn('⚠️ Auto-sync already running');
			return;
		}

		console.log('🔄 Starting auto-sync service (every 30s)');

		// Initial sync
		this.triggerSync();

		// Set interval
		this.syncInterval = setInterval(() => {
			this.triggerSync();
		}, this.SYNC_INTERVAL);
	}

	/**
	 * Stop auto-sync interval
	 */
	stopAutoSync() {
		if (this.syncInterval) {
			clearInterval(this.syncInterval);
			this.syncInterval = null;
			console.log('🛑 Auto-sync service stopped');
		}
	}

	/**
	 * Trigger sync manually or via auto-sync
	 */
	async triggerSync(): Promise<void> {
		// Check if already syncing
		if (this.isSyncing) {
			console.log('⏳ Sync already in progress, skipping...');
			return;
		}

		// Check network status
		const currentNetworkStatus = await this.getNetworkStatus();
		if (!currentNetworkStatus?.isOnline) {
			console.log('🔴 Network offline, skipping sync');
			return;
		}

		// Get sync queue
		const queue = await offlineOrderService.getSyncQueue();
		if (queue.length === 0) {
			console.log('✅ No pending orders to sync');
			return;
		}

		console.log(`📤 Starting sync: ${queue.length} items in queue`);

		// Start sync process
		await this.syncPendingOrders();
	}

	/**
	 * Get current network status (helper)
	 */
	private async getNetworkStatus(): Promise<any> {
		return new Promise(resolve => {
			networkStatus.subscribe(status => {
				resolve(status);
			})();
		});
	}

	/**
	 * Sync all pending orders from queue
	 */
	async syncPendingOrders(): Promise<void> {
		this.isSyncing = true;

		// Reset progress
		this.progress.set({
			isRunning: true,
			totalItems: 0,
			processedItems: 0,
			successCount: 0,
			failureCount: 0,
			currentItem: null,
			lastSyncTime: null,
			errors: []
		});

		try {
			// Get all pending items from queue
			const queue = await offlineOrderService.getSyncQueue();

			if (queue.length === 0) {
				console.log('✅ No items in sync queue');
				this.isSyncing = false;
				return;
			}

			console.log(`📦 Syncing ${queue.length} items...`);

			this.progress.update(p => ({
				...p,
				totalItems: queue.length
			}));

			// Process queue items
			for (const item of queue) {
				await this.syncQueueItem(item);

				this.progress.update(p => ({
					...p,
					processedItems: p.processedItems + 1
				}));

				// Small delay between syncs
				await this.delay(500);
			}

			// Sync completed
			this.progress.update(p => ({
				...p,
				isRunning: false,
				lastSyncTime: new Date()
			}));

			const finalProgress = await this.getProgress();
			console.log(`✅ Sync completed: ${finalProgress.successCount} success, ${finalProgress.failureCount} failed`);

		} catch (error) {
			console.error('❌ Sync error:', error);
			this.progress.update(p => ({
				...p,
				isRunning: false
			}));
		} finally {
			this.isSyncing = false;
		}
	}

	/**
	 * Sync single queue item
	 */
	private async syncQueueItem(item: SyncQueueItem): Promise<void> {
		this.progress.update(p => ({
			...p,
			currentItem: item.order_number
		}));

		console.log(`📤 Syncing order: ${item.order_number} (${item.type})`);

		try {
			// Determine sync method based on type
			let success = false;

			switch (item.type) {
				case 'ORDER_CREATE':
					success = await this.syncOrderCreate(item);
					break;
				case 'ORDER_UPDATE':
					success = await this.syncOrderUpdate(item);
					break;
				case 'STATUS_CHANGE':
					success = await this.syncStatusChange(item);
					break;
				default:
					console.warn('⚠️ Unknown sync type:', item.type);
					success = false;
			}

			if (success) {
				// Remove from queue
				if (item.id) {
					await offlineOrderService.removeSyncQueueItem(item.id);
				}

				// Mark order as synced
				await offlineOrderService.markOrderSynced(item.order_number);

				this.progress.update(p => ({
					...p,
					successCount: p.successCount + 1
				}));

				console.log(`✅ Synced: ${item.order_number}`);
			} else {
				throw new Error('Sync failed');
			}

		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : 'Unknown error';
			console.error(`❌ Failed to sync ${item.order_number}:`, errorMessage);

			// Update retry count
			if (item.id) {
				await offlineOrderService.incrementSyncQueueRetry(item.id, errorMessage);
			}

			await offlineOrderService.incrementSyncAttempt(item.order_number, errorMessage);

			this.progress.update(p => ({
				...p,
				failureCount: p.failureCount + 1,
				errors: [
					...p.errors,
					{
						orderNumber: item.order_number,
						errorMessage,
						timestamp: new Date(),
						retryCount: item.retries || 0
					}
				]
			}));
		}
	}

	/**
	 * Sync ORDER_CREATE type
	 */
	private async syncOrderCreate(item: SyncQueueItem): Promise<boolean> {
		try {
			const orderData = item.data;

			// POST to order group API
			const response = await fetch(`${PUBLIC_API_URL}/orders/groups/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Tenant-ID': String(orderData.tenant_id)
				},
				body: JSON.stringify({
					location: orderData.store_id,
					customer_name: orderData.customer_name,
					customer_phone: orderData.customer_phone || '',
					customer_email: orderData.customer_email || '',
					payment_method: orderData.payment_method,
					orders: [
						{
							outlet: orderData.outlet_id,
							items: orderData.items.map((item: any) => ({
								product: item.product_id,
								quantity: item.quantity,
								modifiers: item.modifiers?.map((m: any) => m.modifier_id) || [],
								special_instructions: item.special_instructions || ''
							}))
						}
					]
				})
			});

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				throw new Error(`HTTP ${response.status}: ${JSON.stringify(errorData)}`);
			}

			return true;
		} catch (error) {
			console.error('❌ syncOrderCreate failed:', error);
			return false;
		}
	}

	/**
	 * Sync ORDER_UPDATE type
	 */
	private async syncOrderUpdate(item: SyncQueueItem): Promise<boolean> {
		try {
			const updateData = item.data;

			const response = await fetch(`${PUBLIC_API_URL}/orders/${updateData.order_id}/`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(updateData)
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}`);
			}

			return true;
		} catch (error) {
			console.error('❌ syncOrderUpdate failed:', error);
			return false;
		}
	}

	/**
	 * Sync STATUS_CHANGE type
	 */
	private async syncStatusChange(item: SyncQueueItem): Promise<boolean> {
		try {
			const statusData = item.data;

			const response = await fetch(`${PUBLIC_API_URL}/kitchen/orders/${statusData.order_id}/${statusData.action}/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					notes: statusData.notes || ''
				})
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}`);
			}

			return true;
		} catch (error) {
			console.error('❌ syncStatusChange failed:', error);
			return false;
		}
	}

	/**
	 * Get current progress
	 */
	private async getProgress(): Promise<SyncProgress> {
		return new Promise(resolve => {
			this.progress.subscribe(progress => {
				resolve(progress);
			})();
		});
	}

	/**
	 * Get progress store (for UI reactivity)
	 */
	getProgressStore() {
		return this.progress;
	}

	/**
	 * Get sync percentage (derived store)
	 */
	getSyncPercentage() {
		return derived(this.progress, $progress => {
			if ($progress.totalItems === 0) return 0;
			return Math.round(($progress.processedItems / $progress.totalItems) * 100);
		});
	}

	/**
	 * Delay helper
	 */
	private delay(ms: number): Promise<void> {
		return new Promise(resolve => setTimeout(resolve, ms));
	}

	/**
	 * Manual sync trigger (for UI button)
	 */
	async manualSync(): Promise<void> {
		console.log('🔄 Manual sync triggered by user');
		await this.syncPendingOrders();
	}

	/**
	 * Cleanup
	 */
	destroy() {
		this.stopAutoSync();
		console.log('🛑 Sync Service destroyed');
	}
}

// Singleton instance
export const syncService = new SyncService();

// Export progress stores
export const syncProgress = syncService.getProgressStore();
export const syncPercentage = syncService.getSyncPercentage();
