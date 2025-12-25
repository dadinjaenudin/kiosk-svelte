<script>
	import { onMount } from 'svelte';
	import { currentOutlet, selectOutlet, loadOutlets } from '$lib/stores/tenant.js';
	
	let outlets = [];
	let loading = true;
	let showDropdown = false;
	
	onMount(async () => {
		outlets = await loadOutlets();
		loading = false;
	});
	
	function handleSelect(outlet) {
		selectOutlet(outlet);
		showDropdown = false;
	}
	
	function toggleDropdown() {
		showDropdown = !showDropdown;
	}
</script>

<div class="outlet-selector">
	{#if loading}
		<div class="selector-button loading">
			<span class="icon">📍</span>
			<span>Loading outlets...</span>
		</div>
	{:else if outlets.length === 0}
		<div class="selector-button disabled">
			<span class="icon">📍</span>
			<span>No outlets available</span>
		</div>
	{:else if outlets.length === 1}
		<!-- Only one outlet, show as static -->
		<div class="selector-button single">
			<span class="icon">📍</span>
			<div class="outlet-info">
				<div class="outlet-name">{outlets[0].name}</div>
				<div class="outlet-city">{outlets[0].city || 'N/A'}</div>
			</div>
		</div>
	{:else}
		<!-- Multiple outlets, show selector -->
		<div class="selector-wrapper">
			<button 
				class="selector-button"
				class:active={showDropdown}
				on:click={toggleDropdown}
			>
				<span class="icon">📍</span>
				<div class="outlet-info">
					<div class="outlet-name">
						{$currentOutlet?.name || 'Select Outlet'}
					</div>
					<div class="outlet-city">
						{$currentOutlet?.city || 'No outlet selected'}
					</div>
				</div>
				<span class="arrow" class:rotated={showDropdown}>▼</span>
			</button>
			
			{#if showDropdown}
				<div class="dropdown">
					{#each outlets as outlet}
						<button
							class="dropdown-item"
							class:active={$currentOutlet?.id === outlet.id}
							on:click={() => handleSelect(outlet)}
						>
							<div class="outlet-details">
								<div class="outlet-name">{outlet.name}</div>
								<div class="outlet-address">
									{outlet.city || outlet.address || 'N/A'}
								</div>
							</div>
							{#if $currentOutlet?.id === outlet.id}
								<span class="check">✓</span>
							{/if}
						</button>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.outlet-selector {
		position: relative;
		min-width: 240px;
	}
	
	.selector-wrapper {
		position: relative;
	}
	
	.selector-button {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 16px;
		background: white;
		border: 2px solid #e5e7eb;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.2s;
		width: 100%;
		text-align: left;
	}
	
	.selector-button:hover {
		border-color: #FF6B35;
		box-shadow: 0 2px 8px rgba(255, 107, 53, 0.1);
	}
	
	.selector-button.active {
		border-color: #FF6B35;
		background: #fff5f2;
	}
	
	.selector-button.loading,
	.selector-button.disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}
	
	.selector-button.single {
		cursor: default;
	}
	
	.icon {
		font-size: 20px;
		flex-shrink: 0;
	}
	
	.outlet-info {
		flex: 1;
		min-width: 0;
	}
	
	.outlet-name {
		font-weight: 600;
		font-size: 14px;
		color: #1f2937;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	
	.outlet-city {
		font-size: 12px;
		color: #6b7280;
		margin-top: 2px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	
	.arrow {
		font-size: 12px;
		color: #6b7280;
		transition: transform 0.2s;
		flex-shrink: 0;
	}
	
	.arrow.rotated {
		transform: rotate(180deg);
	}
	
	.dropdown {
		position: absolute;
		top: calc(100% + 8px);
		left: 0;
		right: 0;
		background: white;
		border: 2px solid #e5e7eb;
		border-radius: 12px;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
		max-height: 400px;
		overflow-y: auto;
		z-index: 1000;
		animation: slideDown 0.2s ease-out;
	}
	
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
	
	.dropdown-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 14px 16px;
		border: none;
		background: white;
		cursor: pointer;
		transition: background 0.2s;
		width: 100%;
		text-align: left;
		border-bottom: 1px solid #f3f4f6;
	}
	
	.dropdown-item:last-child {
		border-bottom: none;
	}
	
	.dropdown-item:hover {
		background: #f9fafb;
	}
	
	.dropdown-item.active {
		background: #fff5f2;
	}
	
	.outlet-details {
		flex: 1;
		min-width: 0;
	}
	
	.outlet-address {
		font-size: 12px;
		color: #9ca3af;
		margin-top: 2px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	
	.check {
		color: #FF6B35;
		font-weight: bold;
		font-size: 16px;
		flex-shrink: 0;
	}
	
	/* Scrollbar styling */
	.dropdown::-webkit-scrollbar {
		width: 8px;
	}
	
	.dropdown::-webkit-scrollbar-track {
		background: #f1f1f1;
		border-radius: 10px;
	}
	
	.dropdown::-webkit-scrollbar-thumb {
		background: #d1d5db;
		border-radius: 10px;
	}
	
	.dropdown::-webkit-scrollbar-thumb:hover {
		background: #9ca3af;
	}
	
	/* Mobile responsive */
	@media (max-width: 640px) {
		.outlet-selector {
			min-width: 200px;
		}
		
		.selector-button {
			padding: 10px 12px;
			gap: 8px;
		}
		
		.outlet-name {
			font-size: 13px;
		}
		
		.outlet-city {
			font-size: 11px;
		}
	}
</style>
