<script>
	import { onMount } from 'svelte';
	import { authFetch } from '$lib/api/auth';
	import { selectedTenant } from '$lib/stores/auth';
	import Swal from 'sweetalert2';
	
	const API_BASE = '/api';
	
	let locations = [];
	let allLocations = [];
	let loading = true;
	let error = '';
	let showModal = false;
	let editingLocation = null;
	let deleteConfirm = null;
	
	// Filter stores by selected tenant
	$: if ($selectedTenant) {
		console.log('🔍 Filtering stores by tenant:', $selectedTenant);
		locations = allLocations.filter(loc => loc.tenant === parseInt($selectedTenant));
		console.log('✅ Filtered stores:', locations.length);
	} else {
		locations = allLocations;
	}
	
	// Form state
	let formData = {
		code: '',
		name: '',
		address: '',
		city: '',
		province: '',
		postal_code: '',
		enable_multi_outlet_payment: true,
		payment_split_method: 'proportional',
		is_active: true
	};
	
	onMount(async () => {
		console.log('🏪 Locations page mounted!');
		await loadLocations();
	});
	
	async function loadLocations() {
		loading = true;
		error = '';
		
		try {
			console.log('📡 Fetching stores from:', `${API_BASE}/admin/stores/`);
			const data = await authFetch(`${API_BASE}/admin/stores/`);
			console.log('✅ Stores API response:', data);
			allLocations = data.results || data;
			locations = allLocations;
			console.log('✅ Total stores:', locations.length);
			if (locations.length > 0) {
				console.log('📋 First store sample:', locations[0]);
			}
		} catch (err) {
			console.error('❌ Load stores error:', err);
			error = err.message || 'Failed to load stores';
		} finally {
			loading = false;
		}
	}
	
	function openCreateModal() {
		editingLocation = null;
		const tenantId = localStorage.getItem('tenantId');
		formData = {
			tenant: tenantId ? parseInt(tenantId) : null,
			code: '',
			name: '',
			address: '',
			city: '',
			province: '',
			postal_code: '',
			enable_multi_outlet_payment: true,
			payment_split_method: 'proportional',
			is_active: true
		};
		showModal = true;
	}
	
	function openEditModal(location) {
		console.log('📝 Opening edit modal for:', location);
		console.log('   Tenant Name:', location.tenant_name);
		console.log('   Outlets Count:', location.outlets_count);
		console.log('   Active Outlets:', location.active_outlets_count);
		editingLocation = location;
		formData = {
			tenant: location.tenant,
			code: location.code,
			name: location.name,
			address: location.address,
			city: location.city,
			province: location.province,
			postal_code: location.postal_code || '',
			enable_multi_outlet_payment: location.enable_multi_outlet_payment,
			payment_split_method: location.payment_split_method,
			is_active: location.is_active
		};
		showModal = true;
	}
	
	function closeModal() {
		showModal = false;
		editingLocation = null;
	}
	
	async function handleSubmit() {
		const url = editingLocation 
			? `${API_BASE}/admin/stores/${editingLocation.id}/`
			: `${API_BASE}/admin/stores/`;
		
		const method = editingLocation ? 'PUT' : 'POST';
		
		try {
			await authFetch(url, {
				method,
				body: JSON.stringify(formData)
			});
			
			await loadLocations();
			closeModal();
			
			if (editingLocation) {
				Swal.fire('Success', 'Store updated successfully', 'success');
			} else {
				Swal.fire('Success', 'Store created successfully', 'success');
			}
		} catch (err) {
			error = err.message || 'Save error';
			Swal.fire('Error', 'Failed to save store: ' + error, 'error');
		}
	}
	
	async function handleDelete(location) {
		if (location.outlets_count > 0) {
			Swal.fire('Cannot Delete', `Cannot delete store with ${location.outlets_count} outlets assigned. Please reassign outlets first.`, 'warning');
			return;
		}
		
		const result = await Swal.fire({
			title: 'Are you sure?',
			text: `Delete store "${location.name}"? This cannot be undone.`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#d33',
			cancelButtonColor: '#3085d6',
			confirmButtonText: 'Yes, delete it!'
		});
		
		if (result.isConfirmed) {
			deleteConfirm = location;
			await confirmDelete();
		}
	}
	
	async function confirmDelete() {
		try {
			await authFetch(`${API_BASE}/admin/stores/${deleteConfirm.id}/`, {
				method: 'DELETE'
			});
			
			await loadLocations();
			deleteConfirm = null;
			Swal.fire('Deleted!', 'Store has been deleted.', 'success');
		} catch (err) {
			error = err.message || 'Delete error';
			Swal.fire('Error', 'Failed to delete store', 'error');
		}
	}
	
	async function regenerateQR(location) {
		try {
			await authFetch(`${API_BASE}/admin/stores/${location.id}/regenerate_qr/`, {
				method: 'POST'
			});
			
			await loadLocations();
		} catch (err) {
			console.error('QR regeneration error:', err);
		}
	}
</script>

<div class="container mx-auto px-4 py-8">
	<!-- Header -->
	<div class="mb-8">
		<div class="flex justify-between items-start">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">🏪 Stores</h1>
				<p class="text-gray-600 mt-1">Manage physical stores for kiosk deployment</p>
			</div>
			<button
				on:click={openCreateModal}
				class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors"
			>
				<span class="text-xl">+</span>
				Add Store
			</button>
		</div>
	</div>
	
	<!-- Error Alert -->
	{#if error}
		<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
			{error}
		</div>
	{/if}
	
	<!-- Loading -->
	{#if loading}
		<div class="text-center py-12">
			<div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
			<p class="mt-4 text-gray-600">Loading stores...</p>
		</div>
	{:else if locations.length === 0}
		<div class="text-center py-12 bg-gray-50 rounded-lg">
			<span class="text-6xl">🏪</span>
			<p class="mt-4 text-xl text-gray-600">No stores found</p>
			<p class="text-gray-500 mt-2">Create your first store to get started</p>
			<button
				on:click={openCreateModal}
				class="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
			>
				Create Store
			</button>
		</div>
	{:else}
		<!-- Locations Grid -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			{#each locations as location (location.id)}
				<div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
					<!-- Header -->
					<div class="flex justify-between items-start mb-4">
						<div class="flex-1">
							<div class="flex items-center gap-2">
								<h3 class="text-xl font-bold text-gray-900">{location.name}</h3>
								{#if !location.is_active}
									<span class="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">Inactive</span>
								{/if}
							</div>
							<p class="text-gray-600 text-sm mt-1">
								Code: <span class="font-mono font-semibold">{location.code}</span>
							</p>
							{#if location.tenant_name}
								<p class="text-blue-600 text-sm mt-1">
									🏢 {location.tenant_name}
								</p>
							{/if}
						</div>
						
						<div class="flex gap-2">
							<button
								on:click={() => openEditModal(location)}
								class="text-blue-600 hover:text-blue-700 p-2"
								title="Edit"
							>
								✏️
							</button>
							<button
								on:click={() => handleDelete(location)}
								class="text-red-600 hover:text-red-700 p-2"
								title="Delete"
							>
								🗑️
							</button>
						</div>
					</div>
					
					<!-- Info -->
					<div class="space-y-2 text-sm">
						<p class="text-gray-700">
							<span class="font-medium">📍 Address:</span> {location.address}
						</p>
						<p class="text-gray-700">
							<span class="font-medium">🏙️ City:</span> {location.city}, {location.province}
						</p>
						
						<!-- Stats -->
						<div class="flex gap-4 mt-4 pt-4 border-t">
							<div class="text-center">
								<p class="text-2xl font-bold text-blue-600">{location.active_outlets_count || 0}</p>
								<p class="text-xs text-gray-600">Active Outlets</p>
							</div>
							<div class="text-center">
								<p class="text-2xl font-bold text-gray-600">{location.outlets_count || 0}</p>
								<p class="text-xs text-gray-600">Total Outlets</p>
							</div>
						</div>
						
						<!-- Manage Outlets Button -->
						<div class="mt-3">
							<a
								href="/store-outlets?store={location.id}"
								class="block w-full px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-lg transition-colors text-center text-sm font-medium"
							>
								<span class="inline-flex items-center gap-2">
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
									</svg>
									Manage Outlets ({location.outlets_count || 0})
								</span>
							</a>
						</div>
						
						<!-- QR Code -->
						<div class="mt-4 pt-4 border-t">
							<div class="flex justify-between items-center">
								<div>
									<p class="text-xs text-gray-600 mb-1">Kiosk QR Code:</p>
									<p class="font-mono text-sm font-semibold text-gray-900">{location.kiosk_qr_code}</p>
								</div>
								<button
									on:click={() => regenerateQR(location)}
									class="text-xs text-blue-600 hover:text-blue-700 px-3 py-1 border border-blue-600 rounded"
									title="Regenerate QR Code"
								>
									🔄 Regenerate
								</button>
							</div>
						</div>
						
						<!-- Settings -->
						<div class="mt-4 pt-4 border-t">
							<p class="text-xs text-gray-600 mb-2">Settings:</p>
							<div class="flex gap-2 flex-wrap">
								{#if location.enable_multi_outlet_payment}
									<span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">✅ Multi-Outlet Payment</span>
								{:else}
									<span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">❌ Single Outlet Only</span>
								{/if}
								<span class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded capitalize">
									{location.payment_split_method}
								</span>
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Create/Edit Modal -->
{#if showModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
		<div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
			<div class="p-6">
				<h2 class="text-2xl font-bold mb-6">
					{editingLocation ? 'Edit Store' : 'Create New Store'}
				</h2>
				
				<form on:submit|preventDefault={handleSubmit} class="space-y-4">
					<!-- Tenant (Read-only, auto-assigned) -->
					{#if editingLocation && editingLocation.tenant_name}
						<div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
							<p class="text-sm text-gray-700">
								<span class="font-medium">🏢 Tenant:</span>
								<span class="text-blue-700 font-semibold">{editingLocation.tenant_name}</span>
							</p>
							{#if editingLocation.outlets_count > 0}
								<p class="text-xs text-gray-600 mt-1">
									📍 {editingLocation.active_outlets_count} active outlets / {editingLocation.outlets_count} total outlets assigned
								</p>
							{:else}
								<p class="text-xs text-gray-600 mt-1">
									📍 No outlets assigned to this location yet
								</p>
							{/if}
						</div>
					{:else if editingLocation}
						<div class="bg-gray-50 border border-gray-200 rounded-lg p-3">
							<p class="text-xs text-gray-600">
								ℹ️ Tenant will be assigned automatically based on your account
							</p>
						</div>
					{/if}
					
					<!-- Code -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Store Code <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.code}
							placeholder="e.g., YOGYA-KAPATIHAN"
							required
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase"
						/>
						<p class="text-xs text-gray-500 mt-1">Unique identifier (uppercase, alphanumeric with dashes)</p>
					</div>
					
					<!-- Name -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Store Name <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.name}
							placeholder="e.g., Yogya Food Court - Level 3"
							required
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<!-- Address -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Address <span class="text-red-500">*</span>
						</label>
						<textarea
							bind:value={formData.address}
							placeholder="Full address"
							required
							rows="2"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						></textarea>
					</div>
					
					<!-- City & Province -->
					<div class="grid grid-cols-2 gap-4">
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								City <span class="text-red-500">*</span>
							</label>
							<input
								type="text"
								bind:value={formData.city}
								required
								class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Province <span class="text-red-500">*</span>
							</label>
							<input
								type="text"
								bind:value={formData.province}
								required
								class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>
					</div>
					
					<!-- Postal Code -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Postal Code
						</label>
						<input
							type="text"
							bind:value={formData.postal_code}
							placeholder="Optional"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<!-- Settings -->
					<div class="border-t pt-4">
						<h3 class="font-medium text-gray-900 mb-3">Kiosk Settings</h3>
						
						<!-- Multi-Outlet Payment -->
						<div class="flex items-center mb-3">
							<input
								type="checkbox"
								id="multi_outlet"
								bind:checked={formData.enable_multi_outlet_payment}
								class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
							/>
							<label for="multi_outlet" class="ml-2 text-sm text-gray-700">
								Enable Multi-Outlet Payment
							</label>
						</div>
						
						<!-- Payment Split Method -->
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Payment Split Method
							</label>
							<select
								bind:value={formData.payment_split_method}
								class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							>
								<option value="proportional">Proportional to Order Total</option>
								<option value="even">Split Evenly</option>
								<option value="manual">Manual Split</option>
							</select>
						</div>
						
						<!-- Active -->
						<div class="flex items-center mt-3">
							<input
								type="checkbox"
								id="is_active"
								bind:checked={formData.is_active}
								class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
							/>
							<label for="is_active" class="ml-2 text-sm text-gray-700">
								Active
							</label>
						</div>
					</div>
					
					<!-- Buttons -->
					<div class="flex gap-3 pt-4">
						<button
							type="submit"
							class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
						>
							{editingLocation ? 'Update' : 'Create'} Location
						</button>
						<button
							type="button"
							on:click={closeModal}
							class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium transition-colors"
						>
							Cancel
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

<!-- Delete Confirmation -->
{#if deleteConfirm}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
		<div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
			<h3 class="text-xl font-bold text-gray-900 mb-4">Confirm Delete</h3>
			<p class="text-gray-700 mb-6">
				Are you sure you want to delete location <strong>{deleteConfirm.name}</strong>?
				This action cannot be undone.
			</p>
			<div class="flex gap-3">
				<button
					on:click={confirmDelete}
					class="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium"
				>
					Delete
				</button>
				<button
					on:click={() => deleteConfirm = null}
					class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium"
				>
					Cancel
				</button>
			</div>
		</div>
	</div>
{/if}
