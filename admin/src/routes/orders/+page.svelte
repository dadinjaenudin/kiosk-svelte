<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isAuthenticated, selectedTenant } from '$lib/stores/auth';
	import RoleGuard from '$lib/components/RoleGuard.svelte';
	import { getOrders, formatOrderStatus, formatPaymentStatus, formatCurrency, formatDateTime, getTimeAgo } from '$lib/api/orders';
	
	// State
	let orders = [];
	let isLoading = true;
	let error = null;
	let currentPage = 1;
	let totalPages = 1;
	let totalCount = 0;
	let mounted = false;
	
	// Filters
	let filters = {
		status: [],
		payment_status: '',
		start_date: '',
		end_date: '',
		search: '',
		ordering: '-created_at'
	};
	
	let showFilters = false;
	
	// Status options
	const statusOptions = [
		{ value: 'pending', label: 'Pending' },
		{ value: 'confirmed', label: 'Confirmed' },
		{ value: 'preparing', label: 'Preparing' },
		{ value: 'ready', label: 'Ready' },
		{ value: 'served', label: 'Served' },
		{ value: 'completed', label: 'Completed' },
		{ value: 'cancelled', label: 'Cancelled' }
	];
	
	const paymentStatusOptions = [
		{ value: '', label: 'All Payment Status' },
		{ value: 'unpaid', label: 'Unpaid' },
		{ value: 'pending', label: 'Pending' },
		{ value: 'paid', label: 'Paid' }
	];
	
	const sortOptions = [
		{ value: '-created_at', label: 'Newest First' },
		{ value: 'created_at', label: 'Oldest First' },
		{ value: '-total_amount', label: 'Highest Amount' },
		{ value: 'total_amount', label: 'Lowest Amount' }
	];
	
	// Load orders
	async function loadOrders() {
		isLoading = true;
		error = null;
		
		try {
			const params = {
				...filters,
				page: currentPage,
				page_size: 10
			};
			
			// Add tenant filter if selected (for admin/super_admin)
			if ($selectedTenant) {
				params.tenant = $selectedTenant;
			}
			
			const response = await getOrders(params);
			
			orders = response.results || [];
			totalCount = response.count || 0;
			totalPages = Math.ceil(totalCount / 10);
			
		} catch (err) {
			console.error('Error loading orders:', err);
			error = err.message || 'Failed to load orders';
		} finally {
			isLoading = false;
		}
	}
	
	// Apply filters
	function applyFilters() {
		currentPage = 1;
		loadOrders();
	}
	
	// Reset filters
	function resetFilters() {
		filters = {
			status: [],
			payment_status: '',
			start_date: '',
			end_date: '',
			search: '',
			ordering: '-created_at'
		};
		currentPage = 1;
		loadOrders();
	}
	
	// Toggle status filter
	function toggleStatusFilter(status) {
		const index = filters.status.indexOf(status);
		if (index > -1) {
			filters.status = filters.status.filter(s => s !== status);
		} else {
			filters.status = [...filters.status, status];
		}
	}
	
	// Pagination
	function nextPage() {
		if (currentPage < totalPages) {
			currentPage++;
			loadOrders();
		}
	}
	
	function prevPage() {
		if (currentPage > 1) {
			currentPage--;
			loadOrders();
		}
	}
	
	// View order detail
	function viewOrder(orderId) {
		goto(`/orders/${orderId}`);
	}
	
	// Reactive: reload orders when tenant filter changes
	$: if (mounted) {
		const tenantId = $selectedTenant;
		currentPage = 1;
		loadOrders();
	}
	
	// Initial load
	onMount(() => {
		loadOrders();
		mounted = true;
	});
</script>

<div class="p-6">
	<!-- Header -->
	<div class="mb-6">
		<h1 class="text-2xl font-bold text-gray-900">Order Management</h1>
		<p class="text-gray-600 mt-1">View and manage all orders</p>
	</div>
	
	<!-- Filters Bar -->
	<div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
		<div class="p-4">
			<!-- Search and Sort Row -->
			<div class="flex flex-wrap gap-4 mb-4">
				<!-- Search -->
				<div class="flex-1 min-w-[200px]">
					<input
						type="text"
						bind:value={filters.search}
						on:input={applyFilters}
						placeholder="Search by order number, customer name, phone..."
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
					/>
				</div>
				
				<!-- Sort -->
				<select
					bind:value={filters.ordering}
					on:change={applyFilters}
					class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
				>
					{#each sortOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
				
				<!-- Toggle Filters Button -->
				<button
					on:click={() => showFilters = !showFilters}
					class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
				>
					{showFilters ? '▲' : '▼'} Filters
				</button>
			</div>
			
			<!-- Advanced Filters (Collapsible) -->
			{#if showFilters}
				<div class="border-t border-gray-200 pt-4 space-y-4">
					<!-- Status Filter -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Order Status</label>
						<div class="flex flex-wrap gap-2">
							{#each statusOptions as option}
								{@const isSelected = filters.status.includes(option.value)}
								<button
									on:click={() => { toggleStatusFilter(option.value); applyFilters(); }}
									class="px-3 py-1 rounded-full text-sm transition {isSelected ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
								>
									{option.label}
								</button>
							{/each}
						</div>
					</div>
					
					<!-- Payment Status Filter -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Payment Status</label>
						<select
							bind:value={filters.payment_status}
							on:change={applyFilters}
							class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
						>
							{#each paymentStatusOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>
					
					<!-- Date Range Filter -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
							<input
								type="date"
								bind:value={filters.start_date}
								on:change={applyFilters}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
							/>
						</div>
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">End Date</label>
							<input
								type="date"
								bind:value={filters.end_date}
								on:change={applyFilters}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
							/>
						</div>
					</div>
					
					<!-- Reset Button -->
					<div class="flex justify-end">
						<button
							on:click={resetFilters}
							class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition"
						>
							Reset Filters
						</button>
					</div>
				</div>
			{/if}
		</div>
	</div>
	
	<!-- Orders List -->
	<div class="bg-white rounded-lg shadow-sm border border-gray-200">
		{#if isLoading}
			<div class="flex items-center justify-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
			</div>
		{:else if error}
			<div class="p-8 text-center">
				<p class="text-red-600">{error}</p>
				<button
					on:click={loadOrders}
					class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
				>
					Retry
				</button>
			</div>
		{:else if orders.length === 0}
			<div class="p-8 text-center text-gray-500">
				<p class="text-lg">No orders found</p>
				<p class="text-sm mt-2">Try adjusting your filters</p>
			</div>
		{:else}
			<!-- Desktop Table View -->
			<div class="hidden md:block overflow-x-auto">
				<table class="w-full">
					<thead class="bg-gray-50 border-b border-gray-200">
						<tr>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order #</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tenant</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Payment</th>
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
							<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each orders as order}
							{@const orderStatus = formatOrderStatus(order.status)}
							{@const paymentStatus = formatPaymentStatus(order.payment_status)}
							<tr class="hover:bg-gray-50 cursor-pointer transition" on:click={() => viewOrder(order.id)}>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm font-medium text-gray-900">{order.order_number}</div>
									<div class="text-xs text-gray-500">{order.table_number || 'Walk-in'}</div>
								</td>
								<td class="px-6 py-4">
									<div class="text-sm text-gray-900">{order.customer_name || 'Guest'}</div>
									{#if order.customer_phone}
										<div class="text-xs text-gray-500">{order.customer_phone}</div>
									{/if}
								</td>
								<td class="px-6 py-4">
									<div class="text-sm text-gray-900">{order.tenant_name}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm font-semibold text-gray-900">{formatCurrency(order.total_amount)}</div>
									<div class="text-xs text-gray-500">{order.items.length} item{order.items.length > 1 ? 's' : ''}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full {orderStatus.bgColor} {orderStatus.textColor}">
										{orderStatus.label}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full {paymentStatus.bgColor} {paymentStatus.textColor}">
										{paymentStatus.label}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{formatDateTime(order.created_at)}</div>
									<div class="text-xs text-gray-500">{getTimeAgo(order.created_at)}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
									<button
										on:click|stopPropagation={() => viewOrder(order.id)}
										class="text-primary-600 hover:text-primary-900 transition"
									>
										View →
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			
			<!-- Mobile Card View -->
			<div class="md:hidden divide-y divide-gray-200">
				{#each orders as order}
					{@const orderStatus = formatOrderStatus(order.status)}
					{@const paymentStatus = formatPaymentStatus(order.payment_status)}
					<div class="p-4 hover:bg-gray-50 transition" on:click={() => viewOrder(order.id)}>
						<div class="flex justify-between items-start mb-2">
							<div>
								<div class="font-semibold text-gray-900">{order.order_number}</div>
								<div class="text-sm text-gray-600">{order.customer_name || 'Guest'}</div>
							</div>
							<div class="text-right">
								<div class="font-bold text-gray-900">{formatCurrency(order.total_amount)}</div>
								<div class="text-xs text-gray-500">{getTimeAgo(order.created_at)}</div>
							</div>
						</div>
						<div class="flex gap-2 mb-2">
							<span class="px-2 py-1 text-xs font-semibold rounded-full {orderStatus.bgColor} {orderStatus.textColor}">
								{orderStatus.label}
							</span>
							<span class="px-2 py-1 text-xs font-semibold rounded-full {paymentStatus.bgColor} {paymentStatus.textColor}">
								{paymentStatus.label}
							</span>
						</div>
						<div class="text-sm text-gray-600">{order.tenant_name}</div>
					</div>
				{/each}
			</div>
			
			<!-- Pagination -->
			{#if totalPages > 1}
				<div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
					<div class="text-sm text-gray-700">
						Showing page {currentPage} of {totalPages} ({totalCount} total)
					</div>
					<div class="flex gap-2">
						<button
							on:click={prevPage}
							disabled={currentPage === 1}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Previous
						</button>
						
						{#if currentPage > 3}
							<button
								on:click={() => { currentPage = 1; loadOrders(); }}
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
									on:click={() => { currentPage = page; loadOrders(); }}
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
								on:click={() => { currentPage = totalPages; loadOrders(); }}
								class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50"
							>
								{totalPages}
							</button>
						{/if}
						
						<button
							on:click={nextPage}
							disabled={currentPage >= totalPages}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Next
						</button>
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>