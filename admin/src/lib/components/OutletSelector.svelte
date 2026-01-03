<script>
	import { onMount } from 'svelte';
	import {
		user,
		currentOutlet,
		accessibleOutlets,
		isAdmin,
		isTenantOwner,
		switchOutlet,
		fetchAccessibleOutlets
	} from '$lib/stores/auth';

	let isOpen = false;
	let isLoading = false;
	let error = null;

	// Close dropdown when clicking outside
	function handleClickOutside(event) {
		const dropdown = document.getElementById('outlet-selector-dropdown');
		if (dropdown && !dropdown.contains(event.target)) {
			isOpen = false;
		}
	}

	onMount(() => {
		// Load accessible outlets if not already loaded
		if ($user && $accessibleOutlets.length === 0) {
			loadOutlets();
		}

		// Add click outside listener
		document.addEventListener('click', handleClickOutside);

		return () => {
			document.removeEventListener('click', handleClickOutside);
		};
	});

	async function loadOutlets() {
		try {
			isLoading = true;
			error = null;
			await fetchAccessibleOutlets();
		} catch (err) {
			console.error('Failed to load outlets:', err);
			error = err.message;
		} finally {
			isLoading = false;
		}
	}

	async function handleOutletSelect(outlet) {
		if ($currentOutlet?.id === outlet.id) {
			isOpen = false;
			return;
		}

		try {
			isLoading = true;
			error = null;
			await switchOutlet(outlet.id);
			isOpen = false;
			
			// Reload page to refresh data with new outlet context
			window.location.reload();
		} catch (err) {
			console.error('Failed to switch outlet:', err);
			error = err.message;
		} finally {
			isLoading = false;
		}
	}

	function toggleDropdown(event) {
		event.stopPropagation();
		isOpen = !isOpen;
	}

	// Show selector only if user has multiple outlets or is tenant owner/admin
	$: showSelector = $user && (
		$isAdmin || 
		$isTenantOwner || 
		($accessibleOutlets && $accessibleOutlets.length > 1)
	);

	$: displayOutlets = Array.isArray($accessibleOutlets) ? $accessibleOutlets : 
	                    ($accessibleOutlets === 'all' ? [] : []);
</script>

{#if showSelector}
	<div class="relative" id="outlet-selector-dropdown">
		<!-- Selector Button -->
		<button
			on:click={toggleDropdown}
			class="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
			class:opacity-50={isLoading}
			disabled={isLoading}
		>
			<span class="text-lg">📍</span>
			<div class="text-left">
				<div class="text-xs text-gray-500">Outlet</div>
				<div class="font-semibold">
					{#if $currentOutlet}
						{$currentOutlet.name}
					{:else if $isAdmin}
						All Outlets
					{:else}
						Select Outlet
					{/if}
				</div>
			</div>
			<span class="text-gray-400 transition-transform inline-block {isOpen ? 'rotate-180' : ''}">▼</span>
		</button>
		{#if isOpen}
			<div
				class="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-auto"
			>
				{#if isLoading}
					<div class="p-4 text-center text-gray-500">
						<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
						<p class="mt-2 text-sm">Loading outlets...</p>
					</div>
				{:else if error}
					<div class="p-4 text-center text-red-600">
						<p class="text-sm">{error}</p>
						<button
							on:click={loadOutlets}
							class="mt-2 text-xs text-blue-600 hover:underline"
						>
							Try Again
						</button>
					</div>
				{:else if displayOutlets.length === 0 && $accessibleOutlets !== 'all'}
					<div class="p-4 text-center text-gray-500">
						<p class="text-sm">No outlets available</p>
					</div>
				{:else}
					<div class="py-1">
						<!-- Admin: All Outlets Option -->
						{#if $isAdmin}
							<button
								on:click={() => handleOutletSelect({ id: null, name: 'All Outlets' })}
								class="flex items-center justify-between w-full px-4 py-2 text-sm text-left hover:bg-gray-50 transition-colors"
								class:bg-blue-50={!$currentOutlet}
							>
								<div class="flex items-center gap-3">
								<span class="text-lg">📍</span>
								<div>
									<div class="font-medium text-gray-900">All Outlets</div>
									<div class="text-xs text-gray-500">View data from all outlets</div>
								</div>
							</div>
							{#if !$currentOutlet}
								<span class="text-blue-600 font-bold text-lg">✓</span>
								{/if}
							</button>
							<div class="border-t border-gray-200 my-1"></div>
						{/if}

						<!-- Outlet List -->
						{#each displayOutlets as outlet}
							<button
								on:click={() => handleOutletSelect(outlet)}
								class="flex items-center justify-between w-full px-4 py-2 text-sm text-left hover:bg-gray-50 transition-colors"
								class:bg-blue-50={$currentOutlet?.id === outlet.id}
							>
								<div class="flex items-center gap-3">
								<span class="text-lg">📍</span>
								<div>
									<div class="font-medium text-gray-900">{outlet.name}</div>
									{#if outlet.city}
										<div class="text-xs text-gray-500">{outlet.city}</div>
									{/if}
								</div>
							</div>
							{#if $currentOutlet?.id === outlet.id}
								<span class="text-blue-600 font-bold text-lg">✓</span>
								{/if}
							</button>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	</div>
{/if}

<style>
	/* Smooth transitions */
	button {
		transition: all 0.2s ease;
	}

	/* Dropdown animation */
	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.absolute.mt-2 {
		animation: slideDown 0.2s ease-out;
	}
</style>
