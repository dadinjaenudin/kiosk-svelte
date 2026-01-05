<script>
	import { onMount } from 'svelte';
	import { selectedTenant } from '$lib/stores/auth';
	import {
		getKitchenStationTypes,
		createKitchenStationType,
		updateKitchenStationType,
		patchKitchenStationType,
		deleteKitchenStationType
	} from '$lib/api/kitchenStationTypes';
	import { getTenants } from '$lib/api/tenants';

	let types = [];
	let tenants = [];
	let loading = false;
	let error = null;
	let showModal = false;
	let editingType = null;
	let formData = {
		name: '',
		code: '',
		description: '',
		icon: '🍳',
		color: '#FF6B35',
		tenant: null,
		is_global: false,
		is_active: true,
		sort_order: 0
	};

	// Available icons
	const iconOptions = [
		'🍳', '☕', '🍰', '🍕', '🍔', '🍟', '🍜', '🥘', '🍲', '🥗',
		'🍱', '🍛', '🍝', '🥙', '🌮', '🌯', '🥪', '🍖', '🍗', '🦐'
	];

	// Load tenants for dropdown
	onMount(async () => {
		await loadTenants();
		await loadTypes();
	});

	// Reactive: reload when tenant filter changes
	$: if ($selectedTenant !== undefined) {
		loadTypes();
	}

	async function loadTenants() {
		try {
			const response = await getTenants();
			tenants = response.results || response;
		} catch (err) {
			console.error('Error loading tenants:', err);
		}
	}

	async function loadTypes() {
		loading = true;
		error = null;
		try {
			const response = await getKitchenStationTypes($selectedTenant);
			types = response.results || response;
			
			// Sort by sort_order, then by name
			types.sort((a, b) => {
				if (a.sort_order !== b.sort_order) {
					return a.sort_order - b.sort_order;
				}
				return a.name.localeCompare(b.name);
			});
		} catch (err) {
			error = err.message;
			console.error('Error loading types:', err);
		} finally {
			loading = false;
		}
	}

	function openCreateModal() {
		editingType = null;
		formData = {
			name: '',
			code: '',
			description: '',
			icon: '🍳',
			color: '#FF6B35',
			tenant: null,
			is_global: false,
			is_active: true,
			sort_order: types.length
		};
		showModal = true;
	}

	function openEditModal(type) {
		editingType = type;
		formData = {
			name: type.name,
			code: type.code,
			description: type.description || '',
			icon: type.icon || '🍳',
			color: type.color || '#FF6B35',
			tenant: type.tenant,
			is_global: type.is_global,
			is_active: type.is_active,
			sort_order: type.sort_order
		};
		showModal = true;
	}

	function closeModal() {
		showModal = false;
		editingType = null;
	}

	async function handleSubmit() {
		try {
			// Prepare data
			const data = {
				...formData,
				tenant: formData.is_global ? null : formData.tenant
			};

			if (editingType) {
				await updateKitchenStationType(editingType.id, data);
			} else {
				await createKitchenStationType(data);
			}

			closeModal();
			await loadTypes();
		} catch (err) {
			error = err.message;
			console.error('Error saving type:', err);
		}
	}

	async function toggleActive(type) {
		try {
			await patchKitchenStationType(type.id, {
				is_active: !type.is_active
			});
			await loadTypes();
		} catch (err) {
			error = err.message;
			console.error('Error toggling active:', err);
		}
	}

	async function handleDelete(type) {
		if (!confirm(`Are you sure you want to delete "${type.name}"?`)) {
			return;
		}

		try {
			await deleteKitchenStationType(type.id);
			await loadTypes();
		} catch (err) {
			error = err.message;
			console.error('Error deleting type:', err);
		}
	}

	function getTenantName(tenantId) {
		if (!tenantId) return 'Global';
		const tenant = tenants.find(t => t.id === tenantId);
		return tenant ? tenant.name : 'Unknown';
	}
</script>

<div class="p-6">
	<!-- Header -->
	<div class="flex justify-between items-center mb-6">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Kitchen Station Types</h1>
			<p class="mt-1 text-sm text-gray-500">
				Manage kitchen station types (MAIN, BEVERAGE, DESSERT, etc.)
			</p>
		</div>
		<button
			on:click={openCreateModal}
			class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
		>
			➕ Create Type
		</button>
	</div>

	<!-- Error Display -->
	{#if error}
		<div class="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
			{error}
		</div>
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="text-center py-12">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			<p class="mt-2 text-gray-600">Loading...</p>
		</div>
	{:else if types.length === 0}
		<div class="text-center py-12 bg-white rounded-lg border border-gray-200">
			<span class="text-6xl">🏷️</span>
			<h3 class="mt-4 text-lg font-medium text-gray-900">No kitchen station types</h3>
			<p class="mt-2 text-gray-500">Get started by creating a new station type.</p>
			<button
				on:click={openCreateModal}
				class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
			>
				Create First Type
			</button>
		</div>
	{:else}
		<!-- Types Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each types as type}
				<div
					class="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow {!type.is_active
						? 'opacity-60'
						: ''}"
				>
					<!-- Header -->
					<div class="flex items-start justify-between mb-3">
						<div class="flex items-center">
							<span
								class="text-3xl mr-3"
								style="filter: drop-shadow(0 2px 4px {type.color}40);"
							>
								{type.icon}
							</span>
							<div>
								<h3 class="font-semibold text-gray-900">{type.name}</h3>
								<code
									class="text-xs px-2 py-0.5 rounded"
									style="background-color: {type.color}20; color: {type.color};"
								>
									{type.code}
								</code>
							</div>
						</div>
						<div class="flex items-center gap-1">
							{#if type.is_global}
								<span
									class="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full"
									title="Available to all tenants"
								>
									🌐 Global
								</span>
							{/if}
						</div>
					</div>

					<!-- Description -->
					{#if type.description}
						<p class="text-sm text-gray-600 mb-3">{type.description}</p>
					{/if}

					<!-- Tenant Info -->
					<div class="mb-3 text-xs text-gray-500">
						<span class="font-medium">Tenant:</span>
						{getTenantName(type.tenant)}
					</div>

					<!-- Actions -->
					<div class="flex items-center justify-between pt-3 border-t border-gray-100">
						<div class="flex items-center gap-2">
							<button
								on:click={() => toggleActive(type)}
								class="text-sm px-3 py-1 rounded-md transition-colors {type.is_active
									? 'bg-green-100 text-green-700 hover:bg-green-200'
									: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
							>
								{type.is_active ? '✓ Active' : '✕ Inactive'}
							</button>
						</div>
						<div class="flex items-center gap-1">
							<button
								on:click={() => openEditModal(type)}
								class="p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
								title="Edit"
							>
								✏️
							</button>
							<button
								on:click={() => handleDelete(type)}
								class="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
								title="Delete"
							>
								🗑️
							</button>
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
			<!-- Modal Header -->
			<div class="flex items-center justify-between p-6 border-b border-gray-200">
				<h2 class="text-xl font-bold text-gray-900">
					{editingType ? 'Edit Kitchen Station Type' : 'Create Kitchen Station Type'}
				</h2>
				<button
					on:click={closeModal}
					class="text-gray-400 hover:text-gray-600 text-2xl leading-none"
				>
					×
				</button>
			</div>

			<!-- Modal Body -->
			<form on:submit|preventDefault={handleSubmit} class="p-6">
				<div class="space-y-4">
					<!-- Name -->
					<div>
						<label for="name" class="block text-sm font-medium text-gray-700 mb-1">
							Name <span class="text-red-500">*</span>
						</label>
						<input
							id="name"
							type="text"
							bind:value={formData.name}
							required
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							placeholder="e.g., Main Kitchen, Beverage Station"
						/>
					</div>

					<!-- Code -->
					<div>
						<label for="code" class="block text-sm font-medium text-gray-700 mb-1">
							Code <span class="text-red-500">*</span>
						</label>
						<input
							id="code"
							type="text"
							bind:value={formData.code}
							required
							maxlength="20"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase"
							placeholder="e.g., MAIN, BEVERAGE, DESSERT"
							style="text-transform: uppercase;"
							on:input={(e) => {
								formData.code = e.target.value.toUpperCase();
							}}
						/>
						<p class="mt-1 text-xs text-gray-500">
							Unique identifier, uppercase letters only (e.g., MAIN, BEVERAGE)
						</p>
					</div>

					<!-- Description -->
					<div>
						<label for="description" class="block text-sm font-medium text-gray-700 mb-1">
							Description
						</label>
						<textarea
							id="description"
							bind:value={formData.description}
							rows="2"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							placeholder="Optional description"
						/>
					</div>

					<!-- Icon & Color Row -->
					<div class="grid grid-cols-2 gap-4">
						<!-- Icon Selector -->
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">Icon</label>
							<div class="grid grid-cols-5 gap-2">
								{#each iconOptions as icon}
									<button
										type="button"
										on:click={() => (formData.icon = icon)}
										class="text-2xl p-2 rounded-lg border-2 transition-all {formData.icon ===
										icon
											? 'border-blue-500 bg-blue-50'
											: 'border-gray-200 hover:border-gray-300'}"
									>
										{icon}
									</button>
								{/each}
							</div>
						</div>

						<!-- Color Picker -->
						<div>
							<label for="color" class="block text-sm font-medium text-gray-700 mb-1">
								Color
							</label>
							<div class="flex items-center gap-2">
								<input
									id="color"
									type="color"
									bind:value={formData.color}
									class="h-10 w-20 rounded-lg border border-gray-300 cursor-pointer"
								/>
								<input
									type="text"
									bind:value={formData.color}
									class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase"
									placeholder="#FF6B35"
									maxlength="7"
								/>
							</div>
							<div class="mt-2 flex items-center gap-2">
								<span class="text-3xl" style="filter: drop-shadow(0 2px 4px {formData.color}40);">
									{formData.icon}
								</span>
								<span class="text-sm text-gray-500">Preview</span>
							</div>
						</div>
					</div>

					<!-- Global / Tenant Selection -->
					<div class="space-y-3 p-4 bg-gray-50 rounded-lg">
						<div class="flex items-center">
							<input
								id="is_global"
								type="checkbox"
								bind:checked={formData.is_global}
								class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<label for="is_global" class="ml-2 block text-sm text-gray-700">
								🌐 Global Type (available to all tenants)
							</label>
						</div>

						{#if !formData.is_global}
							<div>
								<label for="tenant" class="block text-sm font-medium text-gray-700 mb-1">
									Tenant <span class="text-red-500">*</span>
								</label>
								<select
									id="tenant"
									bind:value={formData.tenant}
									required={!formData.is_global}
									class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
								>
									<option value={null}>Select tenant</option>
									{#each tenants as tenant}
										<option value={tenant.id}>{tenant.name}</option>
									{/each}
								</select>
							</div>
						{/if}
					</div>

					<!-- Active Status -->
					<div class="flex items-center">
						<input
							id="is_active"
							type="checkbox"
							bind:checked={formData.is_active}
							class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
						/>
						<label for="is_active" class="ml-2 block text-sm text-gray-700">
							Active (visible in category/product forms)
						</label>
					</div>

					<!-- Sort Order -->
					<div>
						<label for="sort_order" class="block text-sm font-medium text-gray-700 mb-1">
							Sort Order
						</label>
						<input
							id="sort_order"
							type="number"
							bind:value={formData.sort_order}
							min="0"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
						<p class="mt-1 text-xs text-gray-500">Lower numbers appear first</p>
					</div>
				</div>

				<!-- Modal Footer -->
				<div class="flex justify-end gap-3 mt-6 pt-6 border-t border-gray-200">
					<button
						type="button"
						on:click={closeModal}
						class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
					>
						Cancel
					</button>
					<button
						type="submit"
						class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
					>
						{editingType ? 'Update' : 'Create'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
