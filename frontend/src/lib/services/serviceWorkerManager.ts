/**
 * Service Worker Registration & Management
 * 
 * Handles service worker lifecycle and provides utilities
 * for background sync and cache management
 */

import { browser } from '$app/environment';

export interface ServiceWorkerStatus {
	registered: boolean;
	active: boolean;
	waiting: boolean;
	installing: boolean;
	updateAvailable: boolean;
}

class ServiceWorkerManager {
	private registration: ServiceWorkerRegistration | null = null;
	private status: ServiceWorkerStatus = {
		registered: false,
		active: false,
		waiting: false,
		installing: false,
		updateAvailable: false
	};

	/**
	 * Register service worker
	 */
	async register(): Promise<boolean> {
		if (!browser) {
			console.warn('[SW] Not in browser context');
			return false;
		}

		if (!('serviceWorker' in navigator)) {
			console.warn('[SW] Service Worker not supported');
			return false;
		}

		try {
			console.log('[SW] Registering...');

			this.registration = await navigator.serviceWorker.register('/service-worker.js', {
				scope: '/',
				type: 'module'
			});

			console.log('[SW] Registered successfully');
			this.status.registered = true;

			// Listen for updates
			this.registration.addEventListener('updatefound', () => {
				console.log('[SW] Update found');
				this.handleUpdateFound();
			});

			// Check for active service worker
			if (this.registration.active) {
				console.log('[SW] Active service worker found');
				this.status.active = true;
			}

			// Handle waiting service worker
			if (this.registration.waiting) {
				console.log('[SW] Waiting service worker found');
				this.status.waiting = true;
				this.status.updateAvailable = true;
			}

			// Listen for controller change
			navigator.serviceWorker.addEventListener('controllerchange', () => {
				console.log('[SW] Controller changed - reloading page');
				window.location.reload();
			});

			return true;
		} catch (error) {
			console.error('[SW] Registration failed:', error);
			return false;
		}
	}

	/**
	 * Handle service worker update found
	 */
	private handleUpdateFound(): void {
		if (!this.registration) return;

		const newWorker = this.registration.installing;
		if (!newWorker) return;

		this.status.installing = true;

		newWorker.addEventListener('statechange', () => {
			if (newWorker.state === 'installed') {
				this.status.installing = false;

				if (navigator.serviceWorker.controller) {
					// New service worker available
					console.log('[SW] New version available');
					this.status.updateAvailable = true;
					this.status.waiting = true;

					// Notify user about update
					this.notifyUpdateAvailable();
				} else {
					// First install
					console.log('[SW] Service worker installed for first time');
					this.status.active = true;
				}
			}

			if (newWorker.state === 'activated') {
				console.log('[SW] Service worker activated');
				this.status.active = true;
				this.status.waiting = false;
			}
		});
	}

	/**
	 * Notify about service worker update
	 */
	private notifyUpdateAvailable(): void {
		// You can dispatch custom event here for UI notification
		console.log('[SW] 🔄 Update available - reload to get latest version');
		
		// Optional: Auto-update after delay
		// setTimeout(() => this.skipWaiting(), 5000);
	}

	/**
	 * Skip waiting and activate new service worker
	 */
	async skipWaiting(): Promise<void> {
		if (!this.registration || !this.registration.waiting) {
			console.warn('[SW] No waiting service worker');
			return;
		}

		console.log('[SW] Skipping waiting...');
		this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
	}

	/**
	 * Request background sync for pending orders
	 */
	async syncOrders(): Promise<boolean> {
		if (!this.registration || !this.registration.sync) {
			console.warn('[SW] Background Sync not supported');
			return false;
		}

		try {
			console.log('[SW] Requesting background sync...');
			await this.registration.sync.register('sync-orders');
			console.log('[SW] Background sync registered');
			return true;
		} catch (error) {
			console.error('[SW] Failed to register background sync:', error);
			return false;
		}
	}

	/**
	 * Manually trigger sync (for testing or immediate sync)
	 */
	async syncNow(): Promise<boolean> {
		if (!this.registration || !this.registration.active) {
			console.warn('[SW] No active service worker');
			return false;
		}

		return new Promise((resolve) => {
			const messageChannel = new MessageChannel();

			messageChannel.port1.onmessage = (event) => {
				if (event.data.success) {
					console.log('[SW] Manual sync completed');
					resolve(true);
				} else {
					console.error('[SW] Manual sync failed:', event.data.error);
					resolve(false);
				}
			};

			this.registration!.active!.postMessage(
				{ type: 'SYNC_NOW' },
				[messageChannel.port2]
			);
		});
	}

	/**
	 * Unregister service worker
	 */
	async unregister(): Promise<boolean> {
		if (!this.registration) {
			console.warn('[SW] No registration to unregister');
			return false;
		}

		try {
			const success = await this.registration.unregister();
			console.log('[SW] Unregistered:', success);
			this.status = {
				registered: false,
				active: false,
				waiting: false,
				installing: false,
				updateAvailable: false
			};
			return success;
		} catch (error) {
			console.error('[SW] Unregister failed:', error);
			return false;
		}
	}

	/**
	 * Get current status
	 */
	getStatus(): ServiceWorkerStatus {
		return { ...this.status };
	}

	/**
	 * Check if service worker is ready
	 */
	isReady(): boolean {
		return this.status.registered && this.status.active;
	}

	/**
	 * Clear all caches
	 */
	async clearCaches(): Promise<void> {
		if (!browser || !('caches' in window)) {
			console.warn('[SW] Cache API not available');
			return;
		}

		try {
			const cacheNames = await caches.keys();
			console.log('[SW] Clearing caches:', cacheNames);

			await Promise.all(
				cacheNames.map((cacheName) => caches.delete(cacheName))
			);

			console.log('[SW] All caches cleared');
		} catch (error) {
			console.error('[SW] Failed to clear caches:', error);
		}
	}

	/**
	 * Get cache storage usage
	 */
	async getCacheSize(): Promise<{ usage: number; quota: number; percentage: number }> {
		if (!browser || !('storage' in navigator) || !('estimate' in navigator.storage)) {
			return { usage: 0, quota: 0, percentage: 0 };
		}

		try {
			const estimate = await navigator.storage.estimate();
			const usage = estimate.usage || 0;
			const quota = estimate.quota || 0;
			const percentage = quota > 0 ? (usage / quota) * 100 : 0;

			return { usage, quota, percentage };
		} catch (error) {
			console.error('[SW] Failed to estimate storage:', error);
			return { usage: 0, quota: 0, percentage: 0 };
		}
	}
}

// Export singleton instance
export const serviceWorkerManager = new ServiceWorkerManager();
