/**
 * Network Detection Service
 * 
 * Monitors network connectivity and provides automatic online/offline detection
 * with health check to Central Server for intelligent failover.
 * 
 * Features:
 * - Browser online/offline detection (navigator.onLine)
 * - Ping/health check to Central Server (with timeout)
 * - Event listeners for network status changes
 * - Auto health check interval (30 seconds)
 * - Reactive Svelte store for UI updates
 */

import { writable, derived, type Writable } from 'svelte/store';
import { PUBLIC_API_URL } from '$env/static/public';
import { browser } from '$app/environment';

export type ConnectionMode = 'online' | 'offline' | 'checking' | 'error';

export interface NetworkStatus {
	mode: ConnectionMode;
	isOnline: boolean;
	lastCheckTime: Date | null;
	lastOnlineTime: Date | null;
	errorCount: number;
	latency: number | null;
}

class NetworkService {
	private status: Writable<NetworkStatus>;
	private healthCheckInterval: ReturnType<typeof setInterval> | null = null;
	private readonly HEALTH_CHECK_TIMEOUT = 2000; // 2 seconds
	private readonly HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
	private readonly HEALTH_ENDPOINT = '/api/health/';

	constructor() {
		this.status = writable<NetworkStatus>({
			mode: 'checking',
			isOnline: browser ? navigator.onLine : false,
			lastCheckTime: null,
			lastOnlineTime: null,
			errorCount: 0,
			latency: null
		});

		if (browser) {
			this.init();
		}
	}

	private init() {
		// Initial health check
		this.performHealthCheck();

		// Setup browser event listeners
		this.setupEventListeners();

		// Start auto health check
		this.startHealthCheckInterval();
	}

	private setupEventListeners() {
		// Browser online/offline events
		window.addEventListener('online', () => {
			console.log('🟢 Browser: Network online');
			this.performHealthCheck();
		});

		window.addEventListener('offline', () => {
			console.log('🔴 Browser: Network offline');
			this.updateStatus({
				mode: 'offline',
				isOnline: false,
				lastCheckTime: new Date()
			});
		});

		// Page visibility change (check when tab becomes visible)
		document.addEventListener('visibilitychange', () => {
			if (!document.hidden) {
				this.performHealthCheck();
			}
		});
	}

	private startHealthCheckInterval() {
		// Clear existing interval
		if (this.healthCheckInterval) {
			clearInterval(this.healthCheckInterval);
		}

		// Health check every 30 seconds
		this.healthCheckInterval = setInterval(() => {
			this.performHealthCheck();
		}, this.HEALTH_CHECK_INTERVAL);
	}

	private updateStatus(partial: Partial<NetworkStatus>) {
		this.status.update(current => ({
			...current,
			...partial
		}));
	}

	/**
	 * Perform health check to Central Server
	 * Tests if backend is reachable with timeout
	 */
	async performHealthCheck(): Promise<boolean> {
		// First check browser's navigator.onLine
		if (!navigator.onLine) {
			this.updateStatus({
				mode: 'offline',
				isOnline: false,
				lastCheckTime: new Date()
			});
			return false;
		}

		// Update to checking state
		this.updateStatus({
			mode: 'checking'
		});

		const startTime = Date.now();

		try {
			const controller = new AbortController();
			const timeoutId = setTimeout(() => controller.abort(), this.HEALTH_CHECK_TIMEOUT);

			const response = await fetch(`${PUBLIC_API_URL}${this.HEALTH_ENDPOINT}`, {
				method: 'GET',
				signal: controller.signal,
				cache: 'no-cache'
			});

			clearTimeout(timeoutId);

			const latency = Date.now() - startTime;

			if (response.ok) {
				console.log(`🟢 Central Server: Online (${latency}ms)`);
				
				this.updateStatus({
					mode: 'online',
					isOnline: true,
					lastCheckTime: new Date(),
					lastOnlineTime: new Date(),
					errorCount: 0,
					latency
				});

				return true;
			} else {
				throw new Error(`HTTP ${response.status}`);
			}

		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : 'Unknown error';
			console.warn(`🔴 Central Server: Unreachable (${errorMessage})`);

			this.status.update(current => ({
				...current,
				mode: 'offline',
				isOnline: false,
				lastCheckTime: new Date(),
				errorCount: current.errorCount + 1,
				latency: null
			}));

			return false;
		}
	}

	/**
	 * Check if currently online (with optional force check)
	 */
	async isOnline(forceCheck = false): Promise<boolean> {
		if (forceCheck) {
			return await this.performHealthCheck();
		}

		// Return cached status
		let currentStatus: NetworkStatus | null = null;
		this.status.subscribe(status => {
			currentStatus = status;
		})();

		return currentStatus?.isOnline ?? false;
	}

	/**
	 * Get current network status (Svelte store)
	 */
	getStatus() {
		return this.status;
	}

	/**
	 * Get derived connection mode only (for simple UI)
	 */
	getMode() {
		return derived(this.status, $status => $status.mode);
	}

	/**
	 * Manual retry connection
	 */
	async retry(): Promise<boolean> {
		console.log('🔄 Manual retry connection...');
		return await this.performHealthCheck();
	}

	/**
	 * Stop health check interval (cleanup)
	 */
	destroy() {
		if (this.healthCheckInterval) {
			clearInterval(this.healthCheckInterval);
			this.healthCheckInterval = null;
		}

		console.log('🛑 Network Service destroyed');
	}
}

// Singleton instance
export const networkService = new NetworkService();

// Export stores for reactive UI
export const networkStatus = networkService.getStatus();
export const connectionMode = networkService.getMode();

// Helper function to check online status
export async function checkOnline(forceCheck = false): Promise<boolean> {
	return await networkService.isOnline(forceCheck);
}

// Helper function to retry connection
export async function retryConnection(): Promise<boolean> {
	return await networkService.retry();
}
