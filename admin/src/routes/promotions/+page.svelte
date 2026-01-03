<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { selectedTenant } from '$lib/stores/auth';
	import RoleGuard from '$lib/components/RoleGuard.svelte';
	import PermissionButton from '$lib/components/PermissionButton.svelte';
	import {
		getPromotions,
		deletePromotion,
		activatePromotion,
		deactivatePromotion
	} from '$lib/api/promotions';

	// State
	let promotions = [];
	let loading = true;
	let mounted = false;
	let error = '';
	let searchQuery = '';
	let statusFilter = '';
	let typeFilter = '';
	let dateFrom = '';
	let dateTo = '';
	let currentPage = 1;
	let totalPages = 1;
	let showDeleteModal = false;
	let promotionToDelete = null;

	// Promo types
	const promoTypes = [
		{ value: 'percentage', label: 'Percentage Discount' },
		{ value: 'fixed', label: 'Fixed Amount' },
		{ value: 'buy_x_get_y', label: 'Buy X Get Y' },
		{ value: 'bundle', label: 'Bundle Deal' }
	];

	// Status badges
	const statusColors = {
		draft: 'bg-gray-100 text-gray-800',
		scheduled: 'bg-blue-100 text-blue-800',
		active: 'bg-green-100 text-green-800',
		expired: 'bg-red-100 text-red-800',
		paused: 'bg-yellow-100 text-yellow-800'
	};

	onMount(() => {
		loadPromotions();
		mounted = true;
	});

	// Reactive: reload when tenant filter changes
	$: if (mounted) {
		const tenantId = $selectedTenant;
		currentPage = 1;
		loadPromotions();
	}

	async function loadPromotions() {
		try {
			loading = true;
			error = '';

			const filters = {
				search: searchQuery,
				status: statusFilter,
				promo_type: typeFilter,
				date_from: dateFrom,
				date_to: dateTo,
				page: currentPage,
				page_size: 10
			};

			// Add tenant filter
			if ($selectedTenant) {
				filters.tenant = $selectedTenant;
			}

			console.log('Loading promotions with filters:', filters);

			const data = await getPromotions(filters);
			
			// Handle paginated response
			if (data.results) {
				promotions = data.results;
				totalPages = Math.ceil(data.count / 10);
			} else {
				promotions = data;
			}

			console.log('✅ Loaded promotions:', promotions.length, 'Tenant filter:', $selectedTenant);
		} catch (err) {
			console.error('❌ Error loading promotions:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	function handleSearch() {
		currentPage = 1;
		loadPromotions();
	}

	function handleFilterChange() {
		currentPage = 1;
		loadPromotions();
	}

	function handlePageChange(page) {
		currentPage = page;
		loadPromotions();
	}

	function confirmDelete(promo) {
		promotionToDelete = promo;
		showDeleteModal = true;
	}

	async function handleDelete() {
		if (!promotionToDelete) return;

		try {
			await deletePromotion(promotionToDelete.id);
			showDeleteModal = false;
			promotionToDelete = null;
			loadPromotions();
		} catch (err) {
			console.error('❌ Error deleting promotion:', err);
			error = err.message;
		}
	}

	async function toggleActive(promo) {
		try {
			if (promo.is_active) {
				await deactivatePromotion(promo.id);
			} else {
				await activatePromotion(promo.id);
			}
			loadPromotions();
		} catch (err) {
			console.error('❌ Error toggling promotion:', err);
			error = err.message;
			alert(err.message);
		}
	}

	function formatDate(dateStr) {
		const date = new Date(dateStr);
		return date.toLocaleDateString('id-ID', {
			day: '2-digit',
			month: 'short',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function formatCurrency(amount) {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}
</script>

<svelte:head>
	<title>Promotions - Admin Panel</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="flex justify-between items-center mb-6">
		<div>
			<h1 class="text-2xl font-bold text-gray-900">Promotions</h1>
			<p class="text-gray-600 mt-1">Manage discounts and special offers</p>
		</div>
		<PermissionButton
			action="create"
			resource="promotions"
			on:click={() => goto('/promotions/create')}
		>
			<svg
				class="w-5 h-5"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 4v16m8-8H4"
				/>
			</svg>
			Create Promotion
		</PermissionButton>
	</div>
	
	<!-- Search and Filters -->
	<div class="bg-white rounded-lg shadow p-6 mb-6">
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
			<!-- Search -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
				<input
					type="text"
					bind:value={searchQuery}
					on:keyup={(e) => e.key === 'Enter' && handleSearch()}
					placeholder="Search promotions..."
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<!-- Status Filter -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
				<select
					bind:value={statusFilter}
					on:change={handleFilterChange}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				>
					<option value="">All Status</option>
					<option value="draft">Draft</option>
					<option value="scheduled">Scheduled</option>
					<option value="active">Active</option>
					<option value="expired">Expired</option>
					<option value="paused">Paused</option>
				</select>
			</div>

			<!-- Type Filter -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
				<select
					bind:value={typeFilter}
					on:change={handleFilterChange}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				>
					<option value="">All Types</option>
					{#each promoTypes as type}
						<option value={type.value}>{type.label}</option>
					{/each}
				</select>
			</div>

			<!-- Apply Button -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Actions</label>
				<button
					on:click={handleSearch}
					class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
				>
					Apply Filters
				</button>
			</div>
		</div>
	</div>

	<!-- Error Message -->
	{#if error}
		<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
			{error}
		</div>
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="bg-white rounded-lg shadow-sm p-8 text-center">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-blue-600"></div>
			<p class="mt-4 text-gray-600">Loading promotions...</p>
		</div>
	{:else if promotions.length === 0}
		<!-- Empty State -->
		<div class="bg-white rounded-lg shadow-sm p-12 text-center">
			<svg
				class="w-16 h-16 mx-auto text-gray-400 mb-4"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"
				/>
			</svg>
			<h3 class="text-lg font-medium text-gray-900 mb-2">No promotions found</h3>
			<p class="text-gray-600 mb-6">Get started by creating your first promotion</p>
			<button
				on:click={() => goto('/promotions/create')}
				class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
			>
				Create Promotion
			</button>
		</div>
	{:else}
		<!-- Promotions Table -->
		<div class="bg-white rounded-lg shadow-sm overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
								Promotion
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
								Tenant
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
								Type
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
								Discount
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
								Schedule
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
								Status
							</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
								Usage
							</th>
							<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
								Actions
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each promotions as promo}
							<tr class="hover:bg-gray-50 transition-colors">
								<td class="px-6 py-4">
									<div class="flex items-center">
										<div>
											<div class="text-sm font-medium text-gray-900">
												{promo.name}
											</div>
											{#if promo.code}
												<div class="text-xs text-gray-500 font-mono mt-1">
													{promo.code}
												</div>
											{/if}
											{#if promo.product_count}
												<div class="text-xs text-gray-400 mt-1">
													{promo.product_count} products
												</div>
											{/if}
										</div>
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									{#if promo.tenant_name}
										<span class="text-sm text-gray-900">{promo.tenant_name}</span>
									{:else}
										<span class="text-sm text-gray-400">-</span>
									{/if}
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="text-sm text-gray-900">
										{promoTypes.find((t) => t.value === promo.promo_type)?.label || promo.promo_type}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="text-sm font-medium text-gray-900">
										{#if promo.promo_type === 'percentage'}
											{promo.discount_value}%
										{:else}
											{formatCurrency(promo.discount_value)}
										{/if}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									<div>{formatDate(promo.start_date)}</div>
									<div class="text-xs text-gray-400">to</div>
									<div>{formatDate(promo.end_date)}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="px-2 py-1 text-xs font-medium rounded-full {statusColors[promo.status]}">
										{promo.status}
									</span>
									{#if promo.is_active}
										<span class="ml-1 text-xs text-green-600">● Active</span>
									{/if}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									<div>{promo.usage_count || 0}</div>
									{#if promo.usage_limit}
										<div class="text-xs text-gray-400">/ {promo.usage_limit}</div>
									{/if}
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
									<div class="flex justify-end gap-2">
										<button
											on:click={() => goto(`/promotions/${promo.id}`)}
											class="text-blue-600 hover:text-blue-900"
											title="View Details"
										>
											<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
											</svg>
										</button>
										<button
											on:click={() => goto(`/promotions/${promo.id}/edit`)}
											class="text-gray-600 hover:text-gray-900"
											title="Edit"
										>
											<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
											</svg>
										</button>
										<button
											on:click={() => toggleActive(promo)}
											class="{promo.is_active ? 'text-yellow-600 hover:text-yellow-900' : 'text-green-600 hover:text-green-900'}"
											title="{promo.is_active ? 'Deactivate' : 'Activate'}"
										>
											{#if promo.is_active}
												<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
												</svg>
											{:else}
												<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
												</svg>
											{/if}
										</button>
										<button
											on:click={() => confirmDelete(promo)}
											class="text-red-600 hover:text-red-900"
											title="Delete"
										>
											<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
											</svg>
										</button>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<!-- Pagination (if needed) -->
			{#if totalPages > 1}
				<div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
					<div class="text-sm text-gray-700">
						Showing page {currentPage} of {totalPages}
					</div>
					<div class="flex gap-2">
						<button
							on:click={() => handlePageChange(currentPage - 1)}
							disabled={currentPage === 1}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Previous
						</button>
						
						{#if currentPage > 3}
							<button
								on:click={() => handlePageChange(1)}
								class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50"
							>
								1
							</button>
							{#if currentPage > 4}
								<span class="px-3 py-1">...</span>
							{/if}
						{/if}
						
						{#each Array(Math.min(5, totalPages)) as _, i}
							{@const startPage = Math.max(1, Math.min(currentPage - 2, totalPages - 4))}
							{@const page = startPage + i}
							{#if page <= totalPages}
								<button
									on:click={() => handlePageChange(page)}
									class="px-3 py-1 border rounded-lg {currentPage === page ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 hover:bg-gray-50'}"
								>
									{page}
								</button>
							{/if}
						{/each}
						
						{#if currentPage < totalPages - 2}
							{#if currentPage < totalPages - 3}
								<span class="px-3 py-1">...</span>
							{/if}
							<button
								on:click={() => handlePageChange(totalPages)}
								class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50"
							>
								{totalPages}
							</button>
						{/if}
						
						<button
							on:click={() => handlePageChange(currentPage + 1)}
							disabled={currentPage === totalPages}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Next
						</button>
					</div>
				</div>
			{/if}
		</div>
	{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
		<div class="bg-white rounded-lg max-w-md w-full p-6">
			<h3 class="text-lg font-bold text-gray-900 mb-4">Delete Promotion</h3>
			<p class="text-gray-600 mb-6">
				Are you sure you want to delete <strong>{promotionToDelete?.name}</strong>?
				This action cannot be undone.
			</p>
			<div class="flex justify-end gap-3">
				<button
					on:click={() => {
						showDeleteModal = false;
						promotionToDelete = null;
					}}
					class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
				>
					Cancel
				</button>
				<button
					on:click={handleDelete}
					class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
				>
					Delete
				</button>
			</div>
		</div>
	</div>
{/if}
</div>
