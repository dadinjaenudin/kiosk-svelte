<script>
	import { onMount } from 'svelte';
	import KitchenDisplay from '$lib/components/KitchenDisplay.svelte';
	
	const apiUrl = import.meta.env.PUBLIC_API_URL || 'http://localhost:8001/api';
	
	let tenants = [];
	let selectedTenant = null;
	let loading = true;
	
	onMount(async () => {
		await loadTenants();
	});
	
	async function loadTenants() {
		try {
			// Load all tenants from products to get tenant info
			const response = await fetch(`${apiUrl}/products/products/`);
			if (response.ok) {
				const data = await response.json();
				const products = data.results || data || [];
				
				// Extract unique tenants
				const tenantMap = new Map();
				products.forEach(p => {
					if (p.tenant_id && !tenantMap.has(p.tenant_id)) {
						tenantMap.set(p.tenant_id, {
							id: p.tenant_id,
							name: p.tenant_name,
							slug: p.tenant_slug,
							color: p.tenant_color
						});
					}
				});
				
				tenants = Array.from(tenantMap.values());
				
				// Auto-select if only one tenant
				if (tenants.length === 1) {
					selectedTenant = tenants[0];
				}
			}
			
			loading = false;
		} catch (error) {
			console.error('Error loading tenants:', error);
			loading = false;
		}
	}
	
	function selectTenant(tenant) {
		selectedTenant = tenant;
	}
</script>

<svelte:head>
	<title>Kitchen Display - Food Court</title>
</svelte:head>

{#if loading}
	<div class="loading-screen">
		<div class="spinner"></div>
		<h2>Loading Kitchen Display...</h2>
	</div>
{:else if !selectedTenant}
	<div class="tenant-selection">
		<div class="selection-container">
			<h1>🍳 Kitchen Display System</h1>
			<p>Pilih tenant untuk melihat pesanan dapur</p>
			
			<div class="tenants-grid">
				{#each tenants as tenant}
					<button
						class="tenant-card"
						style="border-color: {tenant.color}"
						on:click={() => selectTenant(tenant)}
					>
						<div class="tenant-icon" style="background: {tenant.color}">
							{tenant.name.charAt(0)}
						</div>
						<h3>{tenant.name}</h3>
						<p>Lihat Pesanan →</p>
					</button>
				{/each}
			</div>
			
			<div class="footer-info">
				<p>💡 Pesanan akan otomatis di-refresh setiap 5 detik</p>
			</div>
		</div>
	</div>
{:else}
	<KitchenDisplay
		tenantId={selectedTenant.id}
		tenantName={selectedTenant.name}
		tenantColor={selectedTenant.color}
	/>
	
	<!-- Back button -->
	<button class="back-button" on:click={() => selectedTenant = null}>
		← Ganti Tenant
	</button>
{/if}

<style>
	.loading-screen {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		background: #F3F4F6;
	}
	
	.spinner {
		width: 64px;
		height: 64px;
		border: 6px solid #E5E7EB;
		border-top-color: #10B981;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
		margin-bottom: 24px;
	}
	
	@keyframes spin {
		to { transform: rotate(360deg); }
	}
	
	.loading-screen h2 {
		font-size: 24px;
		font-weight: 700;
		color: #1F2937;
	}
	
	.tenant-selection {
		min-height: 100vh;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 32px;
	}
	
	.selection-container {
		max-width: 900px;
		width: 100%;
		text-align: center;
	}
	
	.selection-container h1 {
		font-size: 48px;
		font-weight: 800;
		color: white;
		margin: 0 0 16px 0;
		text-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
	}
	
	.selection-container > p {
		font-size: 20px;
		color: rgba(255, 255, 255, 0.9);
		margin: 0 0 48px 0;
	}
	
	.tenants-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
		gap: 24px;
		margin-bottom: 32px;
	}
	
	.tenant-card {
		background: white;
		border: 4px solid #E5E7EB;
		border-radius: 20px;
		padding: 32px;
		cursor: pointer;
		transition: all 0.3s;
		text-align: center;
	}
	
	.tenant-card:hover {
		transform: translateY(-8px) scale(1.02);
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
	}
	
	.tenant-icon {
		width: 80px;
		height: 80px;
		margin: 0 auto 20px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 36px;
		font-weight: 800;
		color: white;
	}
	
	.tenant-card h3 {
		font-size: 20px;
		font-weight: 700;
		color: #1F2937;
		margin: 0 0 8px 0;
	}
	
	.tenant-card p {
		font-size: 16px;
		color: #6B7280;
		margin: 0;
	}
	
	.footer-info {
		margin-top: 32px;
	}
	
	.footer-info p {
		font-size: 16px;
		color: rgba(255, 255, 255, 0.8);
	}
	
	.back-button {
		position: fixed;
		top: 24px;
		right: 24px;
		background: white;
		border: 2px solid #E5E7EB;
		padding: 12px 24px;
		border-radius: 12px;
		font-size: 16px;
		font-weight: 700;
		color: #374151;
		cursor: pointer;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		transition: all 0.2s;
		z-index: 100;
	}
	
	.back-button:hover {
		background: #F3F4F6;
		transform: translateY(-2px);
		box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
	}
</style>
