<script lang="ts">
	/**
	 * Connection Status Component
	 * 
	 * Displays current network and socket connection status with visual indicators.
	 * Shows sync progress and allows manual retry.
	 * 
	 * Features:
	 * - Color-coded status badges (Green/Yellow/Red)
	 * - Connection mode display (Online/Offline/Dual)
	 * - Pending orders count
	 * - Last sync timestamp
	 * - Manual sync button
	 * - Responsive design
	 */

	import { onMount, onDestroy } from 'svelte';
	import { networkStatus, retryConnection, type ConnectionMode } from '$lib/services/networkService';
	import { socketStatus, type SocketMode } from '$lib/services/socketService';
	import { syncProgress, syncPercentage, syncService } from '$lib/services/syncService';
	import { offlineOrderService } from '$lib/services/offlineOrderService';

	// Props
	export let position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' = 'top-right';
	export let compact = false;

	// State
	let pendingCount = 0;
	let stats = {
		totalOrders: 0,
		syncedOrders: 0,
		pendingOrders: 0,
		syncQueueSize: 0,
		failedSyncs: 0
	};
	let isRetrying = false;
	let statsInterval: ReturnType<typeof setInterval> | null = null;

	// Reactive derived values
	$: connectionMode = $networkStatus.mode;
	$: isOnline = $networkStatus.isOnline;
	$: lastCheckTime = $networkStatus.lastCheckTime;
	$: latency = $networkStatus.latency;
	$: socketMode = $socketStatus.mode;
	$: isSyncing = $syncProgress.isRunning;
	$: syncPercent = $syncPercentage;
	$: pendingCount = $syncProgress.totalItems - $syncProgress.processedItems;

	// Status badge color
	$: badgeColor = getBadgeColor(connectionMode, socketMode);
	$: badgeIcon = getBadgeIcon(connectionMode, socketMode);
	$: statusText = getStatusText(connectionMode, socketMode);

	onMount(async () => {
		// Load initial stats
		await loadStats();

		// Update stats every 10 seconds
		statsInterval = setInterval(loadStats, 10000);
	});

	onDestroy(() => {
		if (statsInterval) {
			clearInterval(statsInterval);
		}
	});

	async function loadStats() {
		stats = await offlineOrderService.getStats();
	}

	function getBadgeColor(netMode: ConnectionMode, sockMode: SocketMode): string {
		if (netMode === 'online' && (sockMode === 'dual' || sockMode === 'central')) {
			return 'green'; // Fully online
		} else if (netMode === 'online' && sockMode === 'local') {
			return 'yellow'; // Online but only local socket
		} else if (netMode === 'offline' && sockMode === 'local') {
			return 'yellow'; // Offline but LAN works
		} else if (sockMode === 'none') {
			return 'red'; // No connection at all
		} else {
			return 'yellow'; // Other states
		}
	}

	function getBadgeIcon(netMode: ConnectionMode, sockMode: SocketMode): string {
		if (netMode === 'checking') return '⏳';
		if (netMode === 'error') return '⚠️';
		
		const color = getBadgeColor(netMode, sockMode);
		if (color === 'green') return '🟢';
		if (color === 'yellow') return '🟡';
		if (color === 'red') return '🔴';
		return '⚪';
	}

	function getStatusText(netMode: ConnectionMode, sockMode: SocketMode): string {
		if (netMode === 'checking') return 'Checking...';
		if (netMode === 'error') return 'Connection Error';
		
		if (netMode === 'online') {
			if (sockMode === 'dual') return 'Online (Central + Local)';
			if (sockMode === 'central') return 'Online (Central)';
			if (sockMode === 'local') return 'Online (Local Only)';
			return 'Online';
		} else if (netMode === 'offline') {
			if (sockMode === 'local') return 'Offline (LAN Mode)';
			return 'Offline';
		}

		return 'Unknown';
	}

	function formatTimestamp(date: Date | null): string {
		if (!date) return 'Never';
		
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffSec = Math.floor(diffMs / 1000);

		if (diffSec < 60) return `${diffSec}s ago`;
		if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
		if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
		return date.toLocaleTimeString();
	}

	async function handleRetry() {
		isRetrying = true;
		try {
			await retryConnection();
			await loadStats();
		} finally {
			isRetrying = false;
		}
	}

	async function handleManualSync() {
		await syncService.manualSync();
		await loadStats();
	}

	function getPositionClass(pos: string): string {
		const baseClasses = 'fixed z-50';
		switch (pos) {
			case 'top-left':
				return `${baseClasses} top-4 left-4`;
			case 'top-right':
				return `${baseClasses} top-4 right-4`;
			case 'bottom-left':
				return `${baseClasses} bottom-4 left-4`;
			case 'bottom-right':
				return `${baseClasses} bottom-4 right-4`;
			default:
				return `${baseClasses} top-4 right-4`;
		}
	}
</script>

<div class={`connection-status ${getPositionClass(position)} ${compact ? 'compact' : ''}`}>
	<div class="status-card">
		<!-- Header with badge -->
		<div class="status-header">
			<span class="badge badge-{badgeColor}">
				{badgeIcon} {statusText}
			</span>
		</div>

		{#if !compact}
			<!-- Details -->
			<div class="status-details">
				<!-- Connection Info -->
				<div class="detail-row">
					<span class="label">Network:</span>
					<span class="value">{isOnline ? 'Online' : 'Offline'}</span>
				</div>

				{#if latency !== null}
					<div class="detail-row">
						<span class="label">Latency:</span>
						<span class="value">{latency}ms</span>
					</div>
				{/if}

				<div class="detail-row">
					<span class="label">Socket:</span>
					<span class="value capitalize">{socketMode}</span>
				</div>

				<div class="detail-row">
					<span class="label">Last Check:</span>
					<span class="value text-xs">{formatTimestamp(lastCheckTime)}</span>
				</div>

				<!-- Offline Stats -->
				{#if stats.pendingOrders > 0}
					<div class="detail-row highlight">
						<span class="label">Pending Orders:</span>
						<span class="value font-bold">{stats.pendingOrders}</span>
					</div>
				{/if}

				{#if stats.syncQueueSize > 0}
					<div class="detail-row highlight">
						<span class="label">Sync Queue:</span>
						<span class="value font-bold">{stats.syncQueueSize} items</span>
					</div>
				{/if}

				<!-- Sync Progress -->
				{#if isSyncing}
					<div class="sync-progress">
						<div class="progress-bar">
							<div class="progress-fill" style="width: {syncPercent}%"></div>
						</div>
						<span class="progress-text">Syncing... {syncPercent}%</span>
					</div>
				{/if}

				<!-- Last Sync Time -->
				{#if $syncProgress.lastSyncTime}
					<div class="detail-row">
						<span class="label">Last Sync:</span>
						<span class="value text-xs">{formatTimestamp($syncProgress.lastSyncTime)}</span>
					</div>
				{/if}

				<!-- Actions -->
				<div class="status-actions">
					{#if !isOnline}
						<button
							class="btn-retry"
							on:click={handleRetry}
							disabled={isRetrying}
						>
							{isRetrying ? '⏳ Retrying...' : '🔄 Retry'}
						</button>
					{/if}

					{#if stats.syncQueueSize > 0 && !isSyncing}
						<button
							class="btn-sync"
							on:click={handleManualSync}
						>
							📤 Sync Now
						</button>
					{/if}
				</div>

				<!-- Errors -->
				{#if $syncProgress?.errors && $syncProgress.errors.length > 0}
					<div class="error-list">
						<p class="error-title">Sync Errors ({$syncProgress.errors.length}):</p>
						{#each $syncProgress.errors.slice(0, 3) as error}
							<div class="error-item">
								<span class="error-order">{error?.orderNumber || 'Unknown'}</span>
								<span class="error-msg">{error?.errorMessage || 'Unknown error'}</span>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	.connection-status {
		font-family: system-ui, -apple-system, sans-serif;
		max-width: 320px;
	}

	.connection-status.compact {
		max-width: 200px;
	}

	.status-card {
		background: white;
		border-radius: 12px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		padding: 16px;
		border: 2px solid #e5e7eb;
	}

	.status-header {
		margin-bottom: 12px;
	}

	.badge {
		display: inline-flex;
		align-items: center;
		padding: 6px 12px;
		border-radius: 20px;
		font-size: 14px;
		font-weight: 600;
		gap: 6px;
	}

	.badge-green {
		background: #10b981;
		color: white;
	}

	.badge-yellow {
		background: #f59e0b;
		color: white;
	}

	.badge-red {
		background: #ef4444;
		color: white;
	}

	.status-details {
		display: flex;
		flex-direction: column;
		gap: 8px;
		font-size: 13px;
	}

	.detail-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 4px 0;
	}

	.detail-row.highlight {
		background: #fef3c7;
		padding: 8px;
		border-radius: 6px;
		margin: 4px 0;
	}

	.label {
		color: #6b7280;
		font-weight: 500;
	}

	.value {
		color: #111827;
		font-weight: 600;
	}

	.capitalize {
		text-transform: capitalize;
	}

	.sync-progress {
		margin: 8px 0;
	}

	.progress-bar {
		width: 100%;
		height: 8px;
		background: #e5e7eb;
		border-radius: 4px;
		overflow: hidden;
		margin-bottom: 4px;
	}

	.progress-fill {
		height: 100%;
		background: linear-gradient(90deg, #3b82f6, #2563eb);
		transition: width 0.3s ease;
	}

	.progress-text {
		font-size: 11px;
		color: #6b7280;
	}

	.status-actions {
		display: flex;
		gap: 8px;
		margin-top: 12px;
	}

	.btn-retry,
	.btn-sync {
		flex: 1;
		padding: 8px 12px;
		border: none;
		border-radius: 6px;
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-retry {
		background: #3b82f6;
		color: white;
	}

	.btn-retry:hover:not(:disabled) {
		background: #2563eb;
	}

	.btn-retry:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-sync {
		background: #10b981;
		color: white;
	}

	.btn-sync:hover {
		background: #059669;
	}

	.error-list {
		margin-top: 12px;
		padding: 8px;
		background: #fef2f2;
		border-radius: 6px;
		border: 1px solid #fca5a5;
	}

	.error-title {
		font-size: 11px;
		font-weight: 600;
		color: #991b1b;
		margin-bottom: 6px;
	}

	.error-item {
		display: flex;
		flex-direction: column;
		gap: 2px;
		margin-bottom: 6px;
		font-size: 10px;
	}

	.error-order {
		font-weight: 600;
		color: #dc2626;
	}

	.error-msg {
		color: #6b7280;
	}

	/* Responsive */
	@media (max-width: 640px) {
		.connection-status {
			max-width: 280px;
		}

		.status-card {
			padding: 12px;
		}

		.badge {
			font-size: 12px;
			padding: 4px 10px;
		}
	}
</style>
