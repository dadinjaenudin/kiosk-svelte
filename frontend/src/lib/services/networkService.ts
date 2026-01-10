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
	private readonly HEALTH_CHECK_TIMEOUT = 5000; // 5 seconds
	private readonly HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
	private readonly HEALTH_ENDPOINT = '/health/'; // PUBLIC_API_URL already includes /api
	private failedChecks = 0; // Track consecutive failures
	private readonly MAX_FAILED_CHECKS = 2; // Require 2 failures before marking offline

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
			console.log('🟢 Browser: Network online event');
			// Verify with actual health check instead of trusting browser
			this.performHealthCheck();
		});

		window.addEventListener('offline', () => {
			console.log('🔴 Browser: Network offline event (verifying with health check...)');
			// Don't immediately mark as offline, verify with health check first
			// Browser navigator.onLine is unreliable on Windows
			this.performHealthCheck();
		});

		// Page visibility change (check when tab becomes visible)
		// Debounce to avoid triggering on DevTools open/close
		let visibilityTimeout: ReturnType<typeof setTimeout> | null = null;
		document.addEventListener('visibilitychange', () => {
			if (!document.hidden) {
				// Clear existing timeout
				if (visibilityTimeout) {
					clearTimeout(visibilityTimeout);
				}
				// Wait 500ms before checking (avoid false positives from DevTools)
				visibilityTimeout = setTimeout(() => {
					this.performHealthCheck();
				}, 500);
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
		this.status.update(current => {
			const newStatus = { ...current, ...partial };
			console.log('📡 NetworkService status updated:', { mode: newStatus.mode, isOnline: newStatus.isOnline });
			return newStatus;
		});
	}

	/**
	 * Perform health check to Central Server
	 * Tests if backend is reachable with timeout
	 */
	async performHealthCheck(): Promise<boolean> {
		console.log('🔍 Starting health check...', {
			endpoint: `${PUBLIC_API_URL}${this.HEALTH_ENDPOINT}`
		});

		// Don't update to 'checking' state to avoid UI flicker
		// Just perform the check and update based on result

		const startTime = Date.now();

		try {
			const controller = new AbortController();
			// Use longer timeout if DevTools is open (detected via window.outerWidth/innerWidth difference)
			const isDevToolsOpen = window.outerWidth - window.innerWidth > 200;
			const timeout = isDevToolsOpen ? 15000 : this.HEALTH_CHECK_TIMEOUT;
			
			if (isDevToolsOpen) {
				console.log('🔧 DevTools detected, using extended timeout:', timeout + 'ms');
			}
			
			console.log('📡 Fetching health endpoint with timeout:', timeout + 'ms');
			
			const timeoutId = setTimeout(() => {
				console.log('⏱️ Health check timeout reached');
				controller.abort();
			}, timeout);

			const response = await fetch(`${PUBLIC_API_URL}${this.HEALTH_ENDPOINT}`, {
				method: 'GET',
				signal: controller.signal,
				cache: 'no-cache',
				credentials: 'include',
				mode: 'cors'
			});

			clearTimeout(timeoutId);

			const latency = Date.now() - startTime;
			
			console.log('✅ Health check response:', {
				status: response.status,
				ok: response.ok,
				latency: latency + 'ms'
			});

			if (response.ok) {
				console.log(`🟢 Central Server: Online (${latency}ms)`);
				
				// Reset failed checks counter on success
				this.failedChecks = 0;
				
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
			
			// Increment failed checks
			this.failedChecks++;
			
			// Only mark as offline after MAX_FAILED_CHECKS consecutive failures
			if (this.failedChecks >= this.MAX_FAILED_CHECKS) {
				// Only log actual network errors, not abort errors from timeout
				if (errorMessage !== 'The user aborted a request.' && errorMessage !== 'signal is aborted without reason') {
					console.warn(`🔴 Central Server: Unreachable after ${this.failedChecks} attempts (${errorMessage})`);
				}

				this.status.update(current => ({
					...current,
					mode: 'offline',
					isOnline: false,
					lastCheckTime: new Date(),
					errorCount: current.errorCount + 1,
					latency: null
				}));
			} else {
				// Still trying, keep current status
				console.log(`⚠️ Health check failed (${this.failedChecks}/${this.MAX_FAILED_CHECKS}), retrying...`);
				this.status.update(current => ({
					...current,
					lastCheckTime: new Date()
				}));
			}

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

// Helper function to manually check health
export async function checkHealth(): Promise<boolean> {
	return await networkService.performHealthCheck();
}
