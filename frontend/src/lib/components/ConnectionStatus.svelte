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
	export let inline = false; // New: for inline rendering (not fixed position)

	// State
	let isExpanded = false;
	let pendingCount = 0;
	
	function toggleExpanded() {
		isExpanded = !isExpanded;
	}
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
		// Priority: Network status first, then socket
		if (netMode === 'online') {
			if (sockMode === 'dual' || sockMode === 'central') {
				return 'green'; // Fully online with socket
			} else if (sockMode === 'local') {
				return 'yellow'; // Online but only local socket
			} else {
				return 'green'; // Online without socket (HTTP Polling works)
			}
		} else if (netMode === 'offline') {
			if (sockMode === 'local') {
				return 'yellow'; // Offline but LAN works
			} else {
				return 'red'; // No connection at all
			}
		} else if (netMode === 'checking') {
			return 'yellow'; // Checking status
		} else {
			return 'red'; // Error state
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
		if (inline) {
			// Inline mode: no fixed positioning
			return '';
		}
		// Fixed positioning modes
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
	<div class="status-card" class:expanded={isExpanded}>
		<!-- Header with badge (Clickable) -->
		<button class="status-header" on:click={toggleExpanded} title="{statusText} - Click to {isExpanded ? 'hide' : 'show'} details">
			<span class="badge badge-{badgeColor} icon-only">
				{badgeIcon}
				{#if isExpanded}
					<span class="status-text">{statusText}</span>
				{/if}
			</span>
			<span class="toggle-arrow">{isExpanded ? '▼' : '▶'}</span>
		</button>

	{#if isExpanded}
		<!-- Details (compact or full) -->
		<div class="status-details" class:compact-details={compact}>
			{#if !compact}
				<!-- Full details -->
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
			{/if}

			<!-- Offline Stats (shown in both compact and full) -->
			{#if stats.pendingOrders > 0}
				<div class="detail-row highlight">
					<span class="label">Pending:</span>
					<span class="value font-bold">{stats.pendingOrders}</span>
				</div>
			{/if}

			{#if stats.syncQueueSize > 0}
				<div class="detail-row highlight">
					<span class="label">Queue:</span>
					<span class="value font-bold">{stats.syncQueueSize}</span>
			</div>
		{/if}
		
		{#if !compact}
				<!-- Sync Progress -->
				{#if isSyncing}
					<div class="sync-progress">
						<div class="progress-bar">
							<div class="progress-fill" style="width: {syncPercent}%"></div>
						</div>
						<span class="progress-text">
							Syncing... {syncPercent}% 
							({$syncProgress.processedItems}/{$syncProgress.totalItems})
						</span>
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

					{#if stats.pendingOrders > 0 && stats.syncQueueSize === 0}
						<button
							class="btn-rebuild"
							on:click={async () => {
								console.log('🔧 Manual rebuild triggered');
								const rebuilt = await offlineOrderService.rebuildSyncQueue();
								if (rebuilt > 0) {
									await syncService.manualSync();
								}
								await loadStats();
							}}
						>
							🔧 Rebuild Queue ({stats.pendingOrders})
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
					
					<!-- Force Sync: Rebuild + Sync -->
					{#if stats.pendingOrders > 0}
						<button
							class="btn-force-sync"
							on:click={async () => {
								console.log('⚡ Force sync triggered (rebuild + sync)');
								await offlineOrderService.rebuildSyncQueue();
								await syncService.manualSync();
								await loadStats();
							}}
							disabled={isSyncing}
						>
							⚡ Force Sync
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
		transition: all 0.3s ease;
	}
	
	.status-card.expanded {
		padding-bottom: 16px;
	}

	.status-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
		margin-bottom: 0;
		padding: 0;
		background: none;
		border: none;
		cursor: pointer;
		width: 100%;
		text-align: left;
		transition: all 0.2s ease;
	}
	
	.status-header:hover {
		transform: scale(1.02);
	}
	
	.status-card.expanded .status-header {
		margin-bottom: 12px;
	}
	
	.toggle-arrow {
		font-size: 10px;
		color: #6b7280;
		transition: transform 0.2s ease;
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
	
	.badge.icon-only {
		padding: 8px;
		border-radius: 50%;
		font-size: 16px;
	}
	
	.status-text {
		margin-left: 4px;
		font-size: 14px;
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
	
	.status-details.compact-details {
		font-size: 11px;
		gap: 4px;
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
	.btn-sync,
	.btn-rebuild,
	.btn-force-sync {
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
	
	.btn-rebuild {
		background: #f59e0b;
		color: white;
	}
	
	.btn-rebuild:hover {
		background: #d97706;
	}
	
	.btn-force-sync {
		background: #8b5cf6;
		color: white;
	}
	
	.btn-force-sync:hover:not(:disabled) {
		background: #7c3aed;
	}
	
	.btn-force-sync:disabled {
		opacity: 0.5;
		cursor: not-allowed;
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
