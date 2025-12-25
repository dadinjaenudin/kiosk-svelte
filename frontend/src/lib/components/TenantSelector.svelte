<script>
	import { createEventDispatcher } from 'svelte';
	
	const dispatch = createEventDispatcher();
	
	export let tenants = [];
	export let loading = false;
	
	function selectTenant(tenant) {
		dispatch('select', tenant);
	}
</script>

<style>
	.tenant-selection {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	}
	
	.tenant-card {
		background: white;
		border-radius: 1.5rem;
		padding: 3rem;
		box-shadow: 0 20px 60px rgba(0,0,0,0.3);
		max-width: 600px;
		width: 100%;
		animation: slideUp 0.5s ease-out;
	}
	
	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(30px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
	
	.title {
		font-size: 2.5rem;
		font-weight: 800;
		text-align: center;
		margin-bottom: 0.5rem;
		color: #1a202c;
	}
	
	.subtitle {
		text-align: center;
		color: #718096;
		margin-bottom: 2.5rem;
		font-size: 1.125rem;
	}
	
	.tenant-list {
		display: grid;
		gap: 1rem;
	}
	
	.tenant-item {
		padding: 1.75rem;
		border: 2px solid #e2e8f0;
		border-radius: 1rem;
		cursor: pointer;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		background: white;
		position: relative;
		overflow: hidden;
	}
	
	.tenant-item::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		opacity: 0;
		transition: opacity 0.3s;
		z-index: 0;
	}
	
	.tenant-item:hover::before {
		opacity: 0.05;
	}
	
	.tenant-item:hover {
		border-color: #667eea;
		box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
		transform: translateY(-4px);
	}
	
	.tenant-content {
		position: relative;
		z-index: 1;
	}
	
	.tenant-name {
		font-weight: 700;
		font-size: 1.5rem;
		margin-bottom: 0.5rem;
		color: #2d3748;
	}
	
	.tenant-description {
		color: #718096;
		font-size: 1rem;
		line-height: 1.5;
	}
	
	.loading-spinner {
		text-align: center;
		padding: 3rem;
	}
	
	.spinner {
		display: inline-block;
		width: 50px;
		height: 50px;
		border: 4px solid #f3f4f6;
		border-top: 4px solid #667eea;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
	
	.empty-state {
		text-align: center;
		padding: 3rem;
		color: #718096;
	}
	
	.empty-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
		opacity: 0.5;
	}
</style>

<div class="tenant-selection">
	<div class="tenant-card">
		<h1 class="title">🏪 Welcome!</h1>
		<p class="subtitle">Select your restaurant to begin ordering</p>
		
		{#if loading}
			<div class="loading-spinner">
				<div class="spinner"></div>
				<p style="margin-top: 1rem; color: #718096;">Loading restaurants...</p>
			</div>
		{:else if tenants.length === 0}
			<div class="empty-state">
				<div class="empty-icon">🍽️</div>
				<p style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">No restaurants available</p>
				<p style="font-size: 0.875rem;">Please contact support</p>
			</div>
		{:else}
			<div class="tenant-list">
				{#each tenants as tenant}
					<div class="tenant-item" on:click={() => selectTenant(tenant)} on:keypress={() => selectTenant(tenant)} role="button" tabindex="0">
						<div class="tenant-content">
							<h3 class="tenant-name">{tenant.name}</h3>
							{#if tenant.description}
								<p class="tenant-description">{tenant.description}</p>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
