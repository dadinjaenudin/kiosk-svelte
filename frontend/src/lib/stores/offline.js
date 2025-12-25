/**
 * Offline Store - Network status and sync management
 */
import { writable, derived } from 'svelte/store';
import { getPendingSyncItems, removeSyncItem, incrementSyncRetry, addToSyncQueue } from '$db';

// Online/offline status
export const isOnline = writable(typeof navigator !== 'undefined' ? navigator.onLine : true);

// Sync status
export const syncStatus = writable({
	isSyncing: false,
	lastSyncTime: null,
	pendingCount: 0,
	errors: []
});

// Initialize online/offline listeners
if (typeof window !== 'undefined') {
	window.addEventListener('online', () => {
		isOnline.set(true);
		startSync();
	});
	
	window.addEventListener('offline', () => {
		isOnline.set(false);
	});
}

/**
 * Start background sync
 */
export async function startSync() {
	syncStatus.update(s => ({ ...s, isSyncing: true, errors: [] }));
	
	try {
		const pendingItems = await getPendingSyncItems();
		syncStatus.update(s => ({ ...s, pendingCount: pendingItems.length }));
		
		for (const item of pendingItems) {
			try {
				await syncItem(item);
				await removeSyncItem(item.id);
				syncStatus.update(s => ({ ...s, pendingCount: s.pendingCount - 1 }));
			} catch (error) {
				console.error('Sync error for item:', item.id, error);
				await incrementSyncRetry(item.id);
				syncStatus.update(s => ({
					...s,
					errors: [...s.errors, { itemId: item.id, error: error.message }]
				}));
			}
		}
		
		syncStatus.update(s => ({
			...s,
			isSyncing: false,
			lastSyncTime: new Date().toISOString()
		}));
		
		return true;
	} catch (error) {
		console.error('Sync failed:', error);
		syncStatus.update(s => ({ ...s, isSyncing: false }));
		return false;
	}
}

/**
 * Sync individual item to server
 */
async function syncItem(item) {
	const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000/api';
	const data = JSON.parse(item.data);
	
	let endpoint = '';
	let method = 'POST';
	
	switch (item.entity_type) {
		case 'order':
			endpoint = '/orders/';
			method = item.action === 'update' ? 'PATCH' : 'POST';
			break;
		case 'payment':
			endpoint = '/payments/';
			break;
		default:
			throw new Error(`Unknown entity type: ${item.entity_type}`);
	}
	
	const response = await fetch(`${API_URL}${endpoint}`, {
		method: method,
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${localStorage.getItem('access_token')}`
		},
		body: JSON.stringify(data)
	});
	
	if (!response.ok) {
		throw new Error(`HTTP ${response.status}: ${await response.text()}`);
	}
	
	return await response.json();
}

/**
 * Force sync now
 */
export async function forceSyncNow() {
	if (navigator.onLine) {
		return await startSync();
	} else {
		throw new Error('Cannot sync while offline');
	}
}

/**
 * Get sync statistics
 */
export async function getSyncStats() {
	const pending = await getPendingSyncItems();
	return {
		pendingCount: pending.length,
		oldestPending: pending.length > 0 ? pending[0].created_at : null,
		retryingCount: pending.filter(i => i.retry_count > 0).length
	};
}
