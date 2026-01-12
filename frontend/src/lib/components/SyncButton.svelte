<script lang="ts">
	/**
	 * Sync Button Component
	 * 
	 * Displays pending order count and allows manual sync trigger
	 * 
	 * Features:
	 * - Shows pending orders count badge
	 * - Manual sync trigger
	 * - Sync status indicator (syncing, success, error)
	 * - Auto-refresh queue count
	 * 
	 * Version: 1.0.0
	 * Date: 2026-01-12
	 */

	import { onMount, onDestroy } from 'svelte';
	import { serviceWorkerManager } from '$lib/services/serviceWorkerManager';

	// ============================================================================
	// PROPS
	// ============================================================================

	export let showLabel = true;
	export let size: 'sm' | 'md' | 'lg' = 'md';
	export let variant: 'primary' | 'secondary' | 'outline' = 'primary';

	// ============================================================================
	// STATE
	// ============================================================================

	let queueSize = 0;
	let isSyncing = false;
	let syncStatus: 'idle' | 'syncing' | 'success' | 'error' = 'idle';
	let syncMessage = '';
	let isServiceWorkerReady = false;

	// Auto-refresh interval
	let refreshInterval: ReturnType<typeof setInterval> | null = null;

	// ============================================================================
	// SIZE CLASSES
	// ============================================================================

	const sizeClasses = {
		sm: 'px-2 py-1 text-sm',
		md: 'px-4 py-2',
		lg: 'px-6 py-3 text-lg'
	};

	const iconSizes = {
		sm: 'w-4 h-4',
		md: 'w-5 h-5',
		lg: 'w-6 h-6'
	};

	const badgeSizes = {
		sm: 'text-xs px-1.5',
		md: 'text-sm px-2',
		lg: 'text-base px-2.5'
	};

	// ============================================================================
	// VARIANT CLASSES
	// ============================================================================

	const variantClasses = {
		primary: 'bg-blue-600 hover:bg-blue-700 text-white',
		secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
		outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50'
	};

	// ============================================================================
	// LIFECYCLE
	// ============================================================================

	onMount(async () => {
		// Check service worker status
		isServiceWorkerReady = serviceWorkerManager.isReady();

		// Initial queue size
		await updateQueueSize();

		// Auto-refresh every 10 seconds
		refreshInterval = setInterval(updateQueueSize, 10000);
	});

	onDestroy(() => {
		if (refreshInterval) {
			clearInterval(refreshInterval);
		}
	});

	// ============================================================================
	// METHODS
	// ============================================================================

	/**
	 * Update queue size from service worker
	 */
	async function updateQueueSize(): Promise<void> {
		if (!isServiceWorkerReady) return;

		try {
			// Try to get queue size from service worker
			const count = await getQueueCount();
			queueSize = count;
		} catch (error) {
			console.error('Failed to get queue size:', error);
		}
	}

	/**
	 * Get queue count from service worker via message
	 */
	async function getQueueCount(): Promise<number> {
		return new Promise((resolve) => {
			if (!navigator.serviceWorker.controller) {
				resolve(0);
				return;
			}

			const messageChannel = new MessageChannel();

			messageChannel.port1.onmessage = (event) => {
				resolve(event.data.count || 0);
			};

			navigator.serviceWorker.controller.postMessage(
				{ type: 'GET_QUEUE_SIZE' },
				[messageChannel.port2]
			);

			// Timeout after 5 seconds
			setTimeout(() => resolve(0), 5000);
		});
	}

	/**
	 * Trigger manual sync
	 */
	async function handleSync(): Promise<void> {
		if (isSyncing || !isServiceWorkerReady) return;

		isSyncing = true;
		syncStatus = 'syncing';
		syncMessage = 'Syncing...';

		try {
			const success = await serviceWorkerManager.syncNow();

			if (success) {
				syncStatus = 'success';
				syncMessage = 'Sync completed!';
				
				// Update queue size
				await updateQueueSize();

				// Reset after 3 seconds
				setTimeout(() => {
					syncStatus = 'idle';
					syncMessage = '';
				}, 3000);
			} else {
				throw new Error('Sync failed');
			}
		} catch (error) {
			console.error('Sync error:', error);
			syncStatus = 'error';
			syncMessage = error instanceof Error ? error.message : 'Sync failed';

			// Reset after 5 seconds
			setTimeout(() => {
				syncStatus = 'idle';
				syncMessage = '';
			}, 5000);
		} finally {
			isSyncing = false;
		}
	}
</script>

<!-- ============================================================================ -->
<!-- TEMPLATE -->
<!-- ============================================================================ -->

<div class="relative inline-flex items-center gap-2">
	<!-- Sync Button -->
	<button
		type="button"
		on:click={handleSync}
		disabled={isSyncing || !isServiceWorkerReady || queueSize === 0}
		class="
			relative
			rounded-lg
			font-medium
			transition-all
			duration-200
			disabled:opacity-50
			disabled:cursor-not-allowed
			flex items-center gap-2
			{sizeClasses[size]}
			{variantClasses[variant]}
		"
		title={queueSize > 0 ? `Sync ${queueSize} pending order${queueSize > 1 ? 's' : ''}` : 'No pending orders'}
	>
		<!-- Icon -->
		<svg
			class="{iconSizes[size]} {isSyncing ? 'animate-spin' : ''}"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
			xmlns="http://www.w3.org/2000/svg"
		>
			{#if syncStatus === 'success'}
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M5 13l4 4L19 7"
				/>
			{:else if syncStatus === 'error'}
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			{:else}
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
				/>
			{/if}
		</svg>

		<!-- Label -->
		{#if showLabel}
			<span>
				{#if syncStatus === 'syncing'}
					Syncing...
				{:else if syncStatus === 'success'}
					Synced!
				{:else if syncStatus === 'error'}
					Failed
				{:else}
					Sync
				{/if}
			</span>
		{/if}

		<!-- Badge with count -->
		{#if queueSize > 0}
			<span
				class="
					absolute
					-top-2
					-right-2
					rounded-full
					bg-red-500
					text-white
					font-bold
					leading-none
					{badgeSizes[size]}
				"
			>
				{queueSize > 99 ? '99+' : queueSize}
			</span>
		{/if}
	</button>

	<!-- Status Message -->
	{#if syncMessage && syncStatus !== 'idle'}
		<div
			class="
				absolute
				top-full
				left-0
				mt-2
				px-3
				py-2
				rounded
				text-sm
				font-medium
				whitespace-nowrap
				shadow-lg
				z-10
				{syncStatus === 'success' ? 'bg-green-500 text-white' : ''}
				{syncStatus === 'error' ? 'bg-red-500 text-white' : ''}
				{syncStatus === 'syncing' ? 'bg-blue-500 text-white' : ''}
			"
		>
			{syncMessage}
		</div>
	{/if}
</div>

<!-- ============================================================================ -->
<!-- STYLES -->
<!-- ============================================================================ -->

<style>
	/* Animation for badge pulse */
	@keyframes pulse-badge {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.7;
		}
	}

	button:not(:disabled) span[class*="bg-red-500"] {
		animation: pulse-badge 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
</style>
