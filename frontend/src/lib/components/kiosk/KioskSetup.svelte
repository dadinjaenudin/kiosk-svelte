<script lang="ts">
	import { kioskConfig } from '$lib/stores/kioskStore';
	import { createEventDispatcher } from 'svelte';
	
	const dispatch = createEventDispatcher();
	
	let storeCode = '';
	let loading = false;
	let error = '';
	let showQRScanner = false;
	
	const API_BASE = 'http://localhost:8001/api';
	
	async function validateStoreCode() {
		if (!storeCode.trim()) {
			error = 'Please enter a store code';
			return;
		}
		
		loading = true;
		error = '';
		
		try {
			const response = await fetch(
				`${API_BASE}/public/stores/${storeCode}/validate/`
			);
			
			if (response.ok) {
				const data = await response.json();
				
				if (data.valid && data.store) {
					// Save configuration
					kioskConfig.setStore(
						data.store.code,
						data.store.name,
						data.store.id,
						data.store.tenant_name,
						data.store.enable_multi_outlet_payment
					);
					
					dispatch('configured', data.store);
				} else {
					error = 'Invalid store code';
				}
			} else {
				error = 'Store not found. Please check the code.';
			}
		} catch (err) {
			error = 'Connection error. Please check your network.';
			console.error('Store validation error:', err);
		} finally {
			loading = false;
		}
	}
	
	function handleQRScan(event: CustomEvent) {
		const qrCode = event.detail;
		// TODO: Validate QR code and configure kiosk
		console.log('QR scanned:', qrCode);
	}
</script>

<div class="setup-container">
	<div class="setup-card">
		<!-- Header -->
		<div class="setup-header">
			<div class="icon-circle">
				<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
						d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
				</svg>
			</div>
			<h1>Kiosk Configuration</h1>
			<p class="subtitle">Please enter your store code to begin</p>
		</div>
		
		<!-- Input Form -->
		<div class="setup-form">
			<div class="input-group">
				<label for="storeCode">Store Code</label>
				<input
					id="storeCode"
					type="text"
					bind:value={storeCode}
					placeholder="e.g., YOGYA-KAPATIHAN"
					disabled={loading}
					on:keypress={(e) => e.key === 'Enter' && validateStoreCode()}
					class:error={error}
				/>
				<span class="helper-text">
					{#if error}
						<span class="error-text">⚠️ {error}</span>
					{:else}
						Enter the code provided by management
					{/if}
				</span>
			</div>
			
			<button
				class="btn-primary"
				on:click={validateStoreCode}
				disabled={loading || !storeCode.trim()}
			>
				{#if loading}
					<span class="spinner"></span>
					Validating...
				{:else}
					Continue
				{/if}
			</button>
			
			<!-- Divider -->
			<div class="divider">
				<span>OR</span>
			</div>
			
			<!-- QR Scanner Button -->
			<button
				class="btn-secondary"
				on:click={() => showQRScanner = !showQRScanner}
				disabled={loading}
			>
				<svg class="icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
						d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
				</svg>
				Scan QR Code
			</button>
		</div>
		
		<!-- Admin Note -->
		<div class="admin-note">
			<svg class="icon-xs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
					d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			This configuration is required only once during kiosk installation.
			Contact your system administrator if you don't have a store code.
		</div>
	</div>
</div>

<style>
	.setup-container {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		padding: 2rem;
	}
	
	.setup-card {
		background: white;
		border-radius: 1.5rem;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		padding: 3rem;
		max-width: 500px;
		width: 100%;
	}
	
	.setup-header {
		text-align: center;
		margin-bottom: 2.5rem;
	}
	
	.icon-circle {
		width: 80px;
		height: 80px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		margin: 0 auto 1.5rem;
	}
	
	.icon {
		width: 40px;
		height: 40px;
		color: white;
	}
	
	.icon-sm {
		width: 20px;
		height: 20px;
	}
	
	.icon-xs {
		width: 16px;
		height: 16px;
	}
	
	h1 {
		font-size: 2rem;
		font-weight: bold;
		color: #1a202c;
		margin: 0 0 0.5rem;
	}
	
	.subtitle {
		color: #718096;
		font-size: 1rem;
		margin: 0;
	}
	
	.setup-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}
	
	.input-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	
	label {
		font-weight: 600;
		color: #2d3748;
		font-size: 0.95rem;
	}
	
	input {
		padding: 1rem;
		border: 2px solid #e2e8f0;
		border-radius: 0.75rem;
		font-size: 1.1rem;
		text-align: center;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		transition: all 0.2s;
	}
	
	input:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}
	
	input.error {
		border-color: #f56565;
	}
	
	input:disabled {
		background-color: #f7fafc;
		cursor: not-allowed;
	}
	
	.helper-text {
		font-size: 0.875rem;
		color: #718096;
	}
	
	.error-text {
		color: #f56565;
	}
	
	.btn-primary, .btn-secondary {
		padding: 1rem 2rem;
		border-radius: 0.75rem;
		font-size: 1.1rem;
		font-weight: 600;
		border: none;
		cursor: pointer;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
	}
	
	.btn-primary {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}
	
	.btn-primary:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
	}
	
	.btn-primary:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}
	
	.btn-secondary {
		background: white;
		color: #667eea;
		border: 2px solid #667eea;
	}
	
	.btn-secondary:hover:not(:disabled) {
		background: #f7fafc;
	}
	
	.divider {
		display: flex;
		align-items: center;
		text-align: center;
		color: #a0aec0;
		font-size: 0.875rem;
		margin: 0.5rem 0;
	}
	
	.divider::before,
	.divider::after {
		content: '';
		flex: 1;
		border-bottom: 1px solid #e2e8f0;
	}
	
	.divider span {
		padding: 0 1rem;
	}
	
	.admin-note {
		margin-top: 2rem;
		padding: 1rem;
		background: #edf2f7;
		border-radius: 0.75rem;
		display: flex;
		gap: 0.75rem;
		color: #4a5568;
		font-size: 0.875rem;
		line-height: 1.5;
	}
	
	.spinner {
		width: 20px;
		height: 20px;
		border: 3px solid rgba(255, 255, 255, 0.3);
		border-radius: 50%;
		border-top-color: white;
		animation: spin 0.8s linear infinite;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
