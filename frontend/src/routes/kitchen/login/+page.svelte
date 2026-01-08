<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { kitchenConfig } from '$lib/stores/kitchenStore';
	
	const API_BASE = 'http://localhost:8001/api';
	
	let stores: any[] = [];
	let outlets: any[] = [];
	let selectedStore: number | null = null;
	let selectedOutlet: number | null = null;
	let loading = false;
	let error = '';
	
	onMount(async () => {
		// Load available stores
		await loadStores();
	});
	
	async function loadStores() {
		try {
			const response = await fetch(`${API_BASE}/public/stores/`);
			if (!response.ok) throw new Error('Failed to load stores');
			const data = await response.json();
			stores = data.results || data; // Handle pagination or direct array
		} catch (err) {
			console.error('Failed to load stores:', err);
			error = 'Failed to load stores. Please check your connection.';
		}
	}
	
	async function loadOutlets(storeCode: string) {
		try {
			const response = await fetch(`${API_BASE}/public/stores/${storeCode}/outlets/`);
			if (!response.ok) throw new Error('Failed to load outlets');
			const data = await response.json();
			outlets = data.outlets || [];
		} catch (err) {
			console.error('Failed to load outlets:', err);
			error = 'Failed to load outlets for this store.';
		}
	}
	
	async function handleStoreChange(event: Event) {
		const select = event.target as HTMLSelectElement;
		selectedStore = parseInt(select.value);
		selectedOutlet = null;
		outlets = [];
		
		const store = stores.find(s => s.id === selectedStore);
		if (store) {
			await loadOutlets(store.code);
		}
	}
	
	async function handleLogin() {
		if (!selectedStore || !selectedOutlet) {
			error = 'Please select both store and outlet';
			return;
		}
		
		loading = true;
		error = '';
		
		try {
			const store = stores.find(s => s.id === selectedStore);
			const outlet = outlets.find(o => o.id === selectedOutlet);
			
			if (!store || !outlet) {
				throw new Error('Invalid selection');
			}
			
			// Generate device ID
			const deviceId = `KITCHEN-${Date.now()}-${Math.random().toString(36).substring(2, 9).toUpperCase()}`;
			
			// Save configuration
			kitchenConfig.setConfig({
				tenantId: outlet.tenant,
				tenantName: outlet.tenant_name || store.tenant_name,
				storeId: store.id,
				storeName: store.name,
				outletId: outlet.id,
				outletName: outlet.name,
				deviceId,
				soundEnabled: true,
			});
			
			console.log('✅ Kitchen configured:', {
				store: store.name,
				outlet: outlet.name,
				deviceId
			});
			
			// Redirect to kitchen display
			goto('/kitchen/display');
			
		} catch (err: any) {
			console.error('Login error:', err);
			error = err.message || 'Failed to configure kitchen';
		} finally {
			loading = false;
		}
	}
</script>

<div class="kitchen-login">
	<div class="login-container">
		<div class="login-header">
			<div class="logo">🍳</div>
			<h1>Kitchen Display System</h1>
			<p class="subtitle">Select your kitchen station</p>
		</div>
		
		<form class="login-form" on:submit|preventDefault={handleLogin}>
			{#if error}
				<div class="alert alert-error">
					<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="12" cy="12" r="10"/>
						<line x1="12" y1="8" x2="12" y2="12"/>
						<line x1="12" y1="16" x2="12.01" y2="16"/>
					</svg>
					<span>{error}</span>
				</div>
			{/if}
			
			<div class="form-group">
				<label for="store">Select Store</label>
				<select 
					id="store"
					bind:value={selectedStore}
					on:change={handleStoreChange}
					required
					disabled={loading || stores.length === 0}
				>
					<option value={null}>-- Select Store --</option>
					{#each stores as store}
						<option value={store.id}>{store.name}</option>
					{/each}
				</select>
			</div>
			
			<div class="form-group">
				<label for="outlet">Select Outlet/Brand</label>
				<select 
					id="outlet"
					bind:value={selectedOutlet}
					required
					disabled={loading || outlets.length === 0}
				>
					<option value={null}>-- Select Outlet --</option>
					{#each outlets as outlet}
						<option value={outlet.id}>{outlet.name}</option>
					{/each}
				</select>
			</div>
			
			<button 
				type="submit" 
				class="btn-login"
				disabled={loading || !selectedStore || !selectedOutlet}
			>
				{#if loading}
					<span class="spinner"></span>
					<span>Configuring...</span>
				{:else}
					<span>Start Kitchen Display</span>
					<span class="arrow">→</span>
				{/if}
			</button>
		</form>
		
		<div class="login-footer">
			<p class="info-text">
				<svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="12" cy="12" r="10"/>
					<line x1="12" y1="16" x2="12" y2="12"/>
					<line x1="12" y1="8" x2="12.01" y2="8"/>
				</svg>
				This will configure your device as a kitchen display station
			</p>
		</div>
	</div>
</div>

<style>
	.kitchen-login {
		min-height: 100vh;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
	}
	
	.login-container {
		background: white;
		border-radius: 16px;
		padding: 3rem;
		width: 100%;
		max-width: 500px;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
	}
	
	.login-header {
		text-align: center;
		margin-bottom: 2rem;
	}
	
	.logo {
		font-size: 4rem;
		margin-bottom: 1rem;
	}
	
	h1 {
		font-size: 2rem;
		font-weight: 700;
		color: #1f2937;
		margin-bottom: 0.5rem;
	}
	
	.subtitle {
		color: #6b7280;
		font-size: 1rem;
	}
	
	.login-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}
	
	.alert {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		border-radius: 8px;
		font-size: 0.875rem;
	}
	
	.alert-error {
		background: #fee2e2;
		color: #991b1b;
		border: 1px solid #fecaca;
	}
	
	.alert .icon {
		width: 20px;
		height: 20px;
		flex-shrink: 0;
	}
	
	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	
	label {
		font-size: 0.875rem;
		font-weight: 600;
		color: #374151;
	}
	
	select {
		padding: 0.75rem 1rem;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 1rem;
		background: white;
		cursor: pointer;
		transition: all 0.2s ease;
	}
	
	select:hover:not(:disabled) {
		border-color: #d1d5db;
	}
	
	select:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}
	
	select:disabled {
		background: #f3f4f6;
		cursor: not-allowed;
		opacity: 0.6;
	}
	
	.btn-login {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		padding: 1rem 2rem;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		margin-top: 0.5rem;
	}
	
	.btn-login:hover:not(:disabled) {
		background: #5a67d8;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
	}
	
	.btn-login:active:not(:disabled) {
		transform: translateY(0);
	}
	
	.btn-login:disabled {
		background: #9ca3af;
		cursor: not-allowed;
		transform: none;
	}
	
	.arrow {
		font-size: 1.5rem;
		transition: transform 0.2s ease;
	}
	
	.btn-login:hover:not(:disabled) .arrow {
		transform: translateX(4px);
	}
	
	.spinner {
		width: 20px;
		height: 20px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
	
	.login-footer {
		margin-top: 2rem;
		padding-top: 2rem;
		border-top: 1px solid #e5e7eb;
	}
	
	.info-text {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: #6b7280;
		font-size: 0.875rem;
		text-align: center;
		justify-content: center;
	}
	
	.info-icon {
		width: 18px;
		height: 18px;
		flex-shrink: 0;
	}
	
	@media (max-width: 640px) {
		.login-container {
			padding: 2rem 1.5rem;
		}
		
		h1 {
			font-size: 1.5rem;
		}
		
		.logo {
			font-size: 3rem;
		}
	}
</style>
