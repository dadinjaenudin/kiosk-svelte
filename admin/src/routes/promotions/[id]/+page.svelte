<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getPromotion, deletePromotion, activatePromotion, deactivatePromotion } from '$lib/api/promotions';
	import Swal from 'sweetalert2';

	let promotion = null;
	let loading = true;
	let error = '';

	$: id = $page.params.id;

	const promoTypes = {
		percentage: 'Percentage Discount',
		fixed: 'Fixed Amount',
		buy_x_get_y: 'Buy X Get Y',
		bundle: 'Bundle Deal'
	};

	const statusColors = {
		draft: 'bg-gray-100 text-gray-800',
		scheduled: 'bg-blue-100 text-blue-800',
		active: 'bg-green-100 text-green-800',
		expired: 'bg-red-100 text-red-800',
		paused: 'bg-yellow-100 text-yellow-800'
	};

	onMount(() => {
		loadPromotion();
	});

	async function loadPromotion() {
		try {
			loading = true;
			error = '';
			promotion = await getPromotion(id);
		} catch (err) {
			console.error('Error loading promotion:', err);
			error = err.message;
		} finally {
			loading = false;
		}
	}

	async function handleDelete() {
		const result = await Swal.fire({
			title: 'Delete Promotion?',
			text: `Are you sure you want to delete "${promotion.name}"?`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#dc2626',
			cancelButtonColor: '#6b7280',
			confirmButtonText: 'Yes, delete it!'
		});

		if (result.isConfirmed) {
			try {
				await deletePromotion(id);
				await Swal.fire('Deleted!', 'Promotion has been deleted.', 'success');
				goto('/promotions');
			} catch (err) {
				Swal.fire('Error!', err.message, 'error');
			}
		}
	}

	async function handleToggleActive() {
		try {
			if (promotion.is_active) {
				await deactivatePromotion(id);
			} else {
				await activatePromotion(id);
			}
			await loadPromotion();
			Swal.fire('Success!', `Promotion ${promotion.is_active ? 'activated' : 'deactivated'}.`, 'success');
		} catch (err) {
			Swal.fire('Error!', err.message, 'error');
		}
	}

	function formatDate(dateStr) {
		if (!dateStr) return '-';
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
	<title>{promotion ? promotion.name : 'Loading...'} - Promotion Details</title>
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<!-- Header -->
	<div class="flex items-center justify-between mb-6">
		<div class="flex items-center gap-4">
			<button on:click={() => goto('/promotions')} class="px-4 py-2 bg-gray-200 text-gray-700 hover:bg-gray-300 rounded-lg font-medium transition-colors">
				← Back
			</button>
			<h1 class="text-2xl font-bold text-gray-900">Promotion Details</h1>
		</div>

		{#if promotion}
			<div class="flex gap-2">
				<button
					on:click={() => goto(`/promotions/${id}/edit`)}
					class="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg font-medium transition-colors"
				>
					✏️ Edit
				</button>
				<button
					on:click={handleToggleActive}
					class="px-4 py-2 {promotion.is_active ? 'bg-yellow-500' : 'bg-green-600'} text-white hover:{promotion.is_active ? 'bg-yellow-600' : 'bg-green-700'} rounded-lg font-medium transition-colors"
				>
					{promotion.is_active ? '⏸️ Deactivate' : '▶️ Activate'}
				</button>
				<button on:click={handleDelete} class="px-4 py-2 bg-red-600 text-white hover:bg-red-700 rounded-lg font-medium transition-colors">
					🗑️ Delete
				</button>
			</div>
		{/if}
	</div>

	{#if loading}
		<div class="flex justify-center items-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
			{error}
		</div>
	{:else if promotion}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Main Info -->
			<div class="lg:col-span-2 space-y-6">
				<!-- Basic Info Card -->
				<div class="card">
					<div class="card-body">
						<h2 class="text-xl font-semibold mb-4">Basic Information</h2>
						
						<div class="space-y-4">
							<div>
								<label class="text-sm text-gray-500">Name</label>
								<p class="text-lg font-medium">{promotion.name}</p>
							</div>

							{#if promotion.description}
								<div>
									<label class="text-sm text-gray-500">Description</label>
									<p class="text-gray-700">{promotion.description}</p>
								</div>
							{/if}

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label class="text-sm text-gray-500">Promo Type</label>
									<p class="font-medium">{promoTypes[promotion.promo_type] || promotion.promo_type}</p>
								</div>

								<div>
									<label class="text-sm text-gray-500">Discount Value</label>
									<p class="font-medium text-green-600">
										{#if promotion.promo_type === 'percentage'}
											{promotion.discount_value}%
										{:else}
											{formatCurrency(promotion.discount_value)}
										{/if}
									</p>
								</div>
							</div>

							{#if promotion.code}
								<div>
									<label class="text-sm text-gray-500">Promo Code</label>
									<p class="font-mono bg-gray-100 px-3 py-2 rounded inline-block">{promotion.code}</p>
								</div>
							{/if}

							{#if promotion.tenant_name}
								<div>
									<label class="text-sm text-gray-500">Tenant</label>
									<p class="font-medium">{promotion.tenant_name}</p>
								</div>
							{/if}
						</div>
					</div>
				</div>

				<!-- Conditions Card -->
				<div class="card">
					<div class="card-body">
						<h2 class="text-xl font-semibold mb-4">Conditions & Limits</h2>
						
						<div class="grid grid-cols-2 gap-4">
							{#if promotion.min_purchase_amount}
								<div>
									<label class="text-sm text-gray-500">Minimum Purchase</label>
									<p class="font-medium">{formatCurrency(promotion.min_purchase_amount)}</p>
								</div>
							{/if}

							{#if promotion.max_discount_amount}
								<div>
									<label class="text-sm text-gray-500">Max Discount Amount</label>
									<p class="font-medium">{formatCurrency(promotion.max_discount_amount)}</p>
								</div>
							{/if}

							{#if promotion.usage_limit}
								<div>
									<label class="text-sm text-gray-500">Total Usage Limit</label>
									<p class="font-medium">{promotion.usage_limit}</p>
								</div>
							{/if}

							{#if promotion.usage_limit_per_customer}
								<div>
									<label class="text-sm text-gray-500">Per Customer Limit</label>
									<p class="font-medium">{promotion.usage_limit_per_customer}</p>
								</div>
							{/if}

							{#if promotion.promo_type === 'buy_x_get_y'}
								<div>
									<label class="text-sm text-gray-500">Buy Quantity</label>
									<p class="font-medium">{promotion.buy_quantity}</p>
								</div>

								<div>
									<label class="text-sm text-gray-500">Get Quantity</label>
									<p class="font-medium">{promotion.get_quantity}</p>
								</div>
							{/if}
						</div>
					</div>
				</div>

				<!-- Schedule Card -->
				<div class="card">
					<div class="card-body">
						<h2 class="text-xl font-semibold mb-4">Schedule</h2>
						
						<div class="space-y-4">
							<div class="grid grid-cols-2 gap-4">
								<div>
									<label class="text-sm text-gray-500">Start Date</label>
									<p class="font-medium">{formatDate(promotion.start_date)}</p>
								</div>

								<div>
									<label class="text-sm text-gray-500">End Date</label>
									<p class="font-medium">{formatDate(promotion.end_date)}</p>
								</div>
							</div>

							{#if promotion.time_start && promotion.time_end}
								<div class="grid grid-cols-2 gap-4">
									<div>
										<label class="text-sm text-gray-500">Time Start</label>
										<p class="font-medium">{promotion.time_start}</p>
									</div>

									<div>
										<label class="text-sm text-gray-500">Time End</label>
										<p class="font-medium">{promotion.time_end}</p>
									</div>
								</div>
							{/if}

							<div>
								<label class="text-sm text-gray-500 block mb-2">Active Days</label>
								<div class="flex gap-2">
									{#each ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] as day}
										<span class="px-3 py-1 text-sm rounded {promotion[day] ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-400'}">
											{day.substring(0, 3)}
										</span>
									{/each}
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Products Card -->
				{#if promotion.product_count > 0}
					<div class="card">
						<div class="card-body">
							<h2 class="text-xl font-semibold mb-4">
								Applicable Products ({promotion.product_count})
							</h2>
							<p class="text-gray-600">This promotion applies to {promotion.product_count} product(s).</p>
						</div>
					</div>
				{/if}
			</div>

			<!-- Sidebar -->
			<div class="space-y-6">
				<!-- Status Card -->
				<div class="card">
					<div class="card-body">
						<h3 class="text-lg font-semibold mb-4">Status</h3>
						
						<div class="space-y-3">
							<div>
								<label class="text-sm text-gray-500">Current Status</label>
								<p>
									<span class="px-3 py-1 text-sm font-medium rounded-full {statusColors[promotion.status]}">
										{promotion.status}
									</span>
								</p>
							</div>

							<div>
								<label class="text-sm text-gray-500">Active</label>
								<p class="font-medium {promotion.is_active ? 'text-green-600' : 'text-gray-400'}">
									{promotion.is_active ? '✓ Yes' : '✗ No'}
								</p>
							</div>

							<div>
								<label class="text-sm text-gray-500">Featured</label>
								<p class="font-medium {promotion.is_featured ? 'text-blue-600' : 'text-gray-400'}">
									{promotion.is_featured ? '✓ Yes' : '✗ No'}
								</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Usage Stats Card -->
				<div class="card">
					<div class="card-body">
						<h3 class="text-lg font-semibold mb-4">Usage Statistics</h3>
						
						<div class="space-y-3">
							<div>
								<label class="text-sm text-gray-500">Times Used</label>
								<p class="text-2xl font-bold text-blue-600">{promotion.usage_count || 0}</p>
							</div>

							{#if promotion.usage_limit}
								<div>
									<label class="text-sm text-gray-500">Usage Limit</label>
									<p class="font-medium">{promotion.usage_limit}</p>
									<div class="mt-2 bg-gray-200 rounded-full h-2">
										<div
											class="bg-blue-600 h-2 rounded-full"
											style="width: {Math.min((promotion.usage_count / promotion.usage_limit) * 100, 100)}%"
										></div>
									</div>
								</div>
							{/if}
						</div>
					</div>
				</div>

				<!-- Metadata Card -->
				<div class="card">
					<div class="card-body">
						<h3 class="text-lg font-semibold mb-4">Metadata</h3>
						
						<div class="space-y-2 text-sm">
							<div>
								<label class="text-gray-500">Created</label>
								<p class="font-medium">{formatDate(promotion.created_at)}</p>
							</div>

							<div>
								<label class="text-gray-500">Last Updated</label>
								<p class="font-medium">{formatDate(promotion.updated_at)}</p>
							</div>

							<div>
								<label class="text-gray-500">ID</label>
								<p class="font-mono text-xs bg-gray-100 px-2 py-1 rounded">{promotion.id}</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
