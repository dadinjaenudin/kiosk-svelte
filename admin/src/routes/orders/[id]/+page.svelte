<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import { 
		getOrderDetail, 
		getOrderTimeline, 
		getOrderReceipt,
		updateOrderStatus,
		formatOrderStatus, 
		formatPaymentStatus, 
		formatCurrency, 
		formatDateTime 
	} from '$lib/api/orders';
	
	// Get order ID from URL
	$: orderId = $page.params.id;
	
	// State
	let order = null;
	let timeline = [];
	let isLoading = true;
	let error = null;
	let isUpdatingStatus = false;
	let showStatusModal = false;
	let newStatus = '';
	let showReceiptModal = false;
	let receiptData = null;
	
	// Status transitions (what statuses can be set from current status)
	const statusTransitions = {
		'pending': ['confirmed', 'cancelled'],
		'confirmed': ['preparing', 'cancelled'],
		'preparing': ['ready', 'cancelled'],
		'ready': ['served', 'cancelled'],
		'served': ['completed'],
		'completed': [],
		'cancelled': []
	};
	
	// Load order details
	async function loadOrder() {
		isLoading = true;
		error = null;
		
		try {
			const [orderData, timelineData] = await Promise.all([
				getOrderDetail(orderId),
				getOrderTimeline(orderId)
			]);
			
			order = orderData;
			timeline = timelineData.timeline || [];
			
		} catch (err) {
			console.error('Error loading order:', err);
			error = err.message || 'Failed to load order details';
		} finally {
			isLoading = false;
		}
	}
	
	// Update order status
	async function handleUpdateStatus() {
		if (!newStatus || isUpdatingStatus) return;
		
		isUpdatingStatus = true;
		
		try {
			const response = await updateOrderStatus(orderId, newStatus);
			order = response.order;
			
			// Reload timeline
			const timelineData = await getOrderTimeline(orderId);
			timeline = timelineData.timeline || [];
			
			showStatusModal = false;
			newStatus = '';
			
		} catch (err) {
			console.error('Error updating status:', err);
			alert('Failed to update order status: ' + (err.message || 'Unknown error'));
		} finally {
			isUpdatingStatus = false;
		}
	}
	
	// Print receipt
	async function handlePrintReceipt() {
		try {
			receiptData = await getOrderReceipt(orderId);
			showReceiptModal = true;
		} catch (err) {
			console.error('Error loading receipt:', err);
			alert('Failed to load receipt: ' + (err.message || 'Unknown error'));
		}
	}
	
	// Print receipt (browser print)
	function printReceipt() {
		window.print();
	}
	
	// Get available status options based on current status
	function getAvailableStatuses() {
		if (!order) return [];
		const available = statusTransitions[order.status] || [];
		return available.map(status => ({
			value: status,
			label: formatOrderStatus(status).label
		}));
	}
	
	// Check auth and load order
	onMount(() => {
		if (!$isAuthenticated) {
			goto('/login');
			return;
		}
		
		if (orderId) {
			loadOrder();
		}
	});
</script>

<div class="p-6">
	{#if isLoading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
		</div>
	{:else if error}
		<div class="text-center py-12">
			<p class="text-red-600 mb-4">{error}</p>
			<button
				on:click={loadOrder}
				class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
			>
				Retry
			</button>
		</div>
	{:else if order}
		<!-- Header -->
		<div class="mb-6 flex items-center justify-between">
			<div>
				<button
					on:click={() => goto('/orders')}
					class="text-primary-600 hover:text-primary-800 transition mb-2"
				>
					← Back to Orders
				</button>
				<h1 class="text-2xl font-bold text-gray-900">{order.order_number}</h1>
				<p class="text-gray-600 mt-1">{formatDateTime(order.created_at)}</p>
			</div>
			
			<!-- Actions -->
			<div class="flex gap-2">
				{#if getAvailableStatuses().length > 0}
					<button
						on:click={() => showStatusModal = true}
						class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
					>
						Update Status
					</button>
				{/if}
				<button
					on:click={handlePrintReceipt}
					class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
				>
					🖨️ Print Receipt
				</button>
			</div>
		</div>
		
		<!-- Order Status Cards -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
			<!-- Order Status -->
			<div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
				<div class="text-sm text-gray-600 mb-1">Order Status</div>
				{@const orderStatus = formatOrderStatus(order.status)}
				<div class="text-lg font-semibold">
					<span class="px-3 py-1 rounded-full text-sm {orderStatus.bgColor} {orderStatus.textColor}">
						{orderStatus.label}
					</span>
				</div>
			</div>
			
			<!-- Payment Status -->
			<div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
				<div class="text-sm text-gray-600 mb-1">Payment Status</div>
				{@const paymentStatus = formatPaymentStatus(order.payment_status)}
				<div class="text-lg font-semibold">
					<span class="px-3 py-1 rounded-full text-sm {paymentStatus.bgColor} {paymentStatus.textColor}">
						{paymentStatus.label}
					</span>
				</div>
			</div>
			
			<!-- Total Amount -->
			<div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
				<div class="text-sm text-gray-600 mb-1">Total Amount</div>
				<div class="text-2xl font-bold text-gray-900">{formatCurrency(order.total_amount)}</div>
			</div>
			
			<!-- Items Count -->
			<div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
				<div class="text-sm text-gray-600 mb-1">Total Items</div>
				<div class="text-2xl font-bold text-gray-900">{order.items.length}</div>
			</div>
		</div>
		
		<!-- Main Content Grid -->
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Left Column (2/3 width) -->
			<div class="lg:col-span-2 space-y-6">
				<!-- Order Items -->
				<div class="bg-white rounded-lg shadow-sm border border-gray-200">
					<div class="px-6 py-4 border-b border-gray-200">
						<h2 class="text-lg font-semibold text-gray-900">Order Items</h2>
					</div>
					<div class="p-6">
						<div class="space-y-4">
							{#each order.items as item}
								<div class="flex justify-between items-start pb-4 border-b border-gray-100 last:border-0">
									<div class="flex-1">
										<div class="font-medium text-gray-900">{item.product_name}</div>
										<div class="text-sm text-gray-600">
											Quantity: {item.quantity} × {formatCurrency(item.unit_price)}
										</div>
										
										<!-- Modifiers -->
										{#if item.modifiers && item.modifiers.length > 0}
											<div class="mt-2 space-y-1">
												{#each item.modifiers as modifier}
													<div class="text-sm text-gray-600 pl-4">
														+ {modifier.name}
														{#if modifier.price > 0}
															<span class="text-gray-500">({formatCurrency(modifier.price)})</span>
														{/if}
													</div>
												{/each}
											</div>
										{/if}
										
										<!-- Notes -->
										{#if item.notes}
											<div class="mt-2 text-sm text-gray-600 italic">
												Note: {item.notes}
											</div>
										{/if}
									</div>
									
									<div class="text-right ml-4">
										<div class="font-semibold text-gray-900">{formatCurrency(item.total_price)}</div>
									</div>
								</div>
							{/each}
						</div>
						
						<!-- Order Totals -->
						<div class="mt-6 pt-6 border-t border-gray-200 space-y-2">
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Subtotal</span>
								<span class="text-gray-900">{formatCurrency(order.subtotal)}</span>
							</div>
							{#if order.tax_amount > 0}
								<div class="flex justify-between text-sm">
									<span class="text-gray-600">Tax</span>
									<span class="text-gray-900">{formatCurrency(order.tax_amount)}</span>
								</div>
							{/if}
							{#if order.service_charge_amount > 0}
								<div class="flex justify-between text-sm">
									<span class="text-gray-600">Service Charge</span>
									<span class="text-gray-900">{formatCurrency(order.service_charge_amount)}</span>
								</div>
							{/if}
							{#if order.discount_amount > 0}
								<div class="flex justify-between text-sm text-green-600">
									<span>Discount</span>
									<span>-{formatCurrency(order.discount_amount)}</span>
								</div>
							{/if}
							<div class="flex justify-between text-lg font-bold pt-2 border-t border-gray-200">
								<span class="text-gray-900">Total</span>
								<span class="text-gray-900">{formatCurrency(order.total_amount)}</span>
							</div>
						</div>
					</div>
				</div>
				
				<!-- Order Timeline -->
				<div class="bg-white rounded-lg shadow-sm border border-gray-200">
					<div class="px-6 py-4 border-b border-gray-200">
						<h2 class="text-lg font-semibold text-gray-900">Order Timeline</h2>
					</div>
					<div class="p-6">
						<div class="relative">
							{#each timeline as step, index}
								{#if step.status !== 'draft'}
									<div class="flex gap-4 pb-8 last:pb-0">
										<!-- Timeline Line -->
										<div class="relative">
											<div class="w-8 h-8 rounded-full flex items-center justify-center {step.completed ? 'bg-primary-500' : 'bg-gray-300'}">
												{#if step.completed}
													<span class="text-white text-sm">✓</span>
												{:else}
													<span class="text-white text-sm">○</span>
												{/if}
											</div>
											{#if index < timeline.length - 1}
												<div class="absolute top-8 left-4 w-0.5 h-full {step.completed ? 'bg-primary-500' : 'bg-gray-300'}"></div>
											{/if}
										</div>
										
										<!-- Step Info -->
										<div class="flex-1 pt-1">
											<div class="font-medium text-gray-900">{step.label}</div>
											{#if step.timestamp}
												<div class="text-sm text-gray-600">{formatDateTime(step.timestamp)}</div>
											{:else}
												<div class="text-sm text-gray-400">Pending</div>
											{/if}
										</div>
									</div>
								{/if}
							{/each}
						</div>
					</div>
				</div>
			</div>
			
			<!-- Right Column (1/3 width) -->
			<div class="space-y-6">
				<!-- Customer Info -->
				<div class="bg-white rounded-lg shadow-sm border border-gray-200">
					<div class="px-6 py-4 border-b border-gray-200">
						<h2 class="text-lg font-semibold text-gray-900">Customer Information</h2>
					</div>
					<div class="p-6 space-y-3">
						<div>
							<div class="text-sm text-gray-600">Name</div>
							<div class="font-medium text-gray-900">{order.customer_name || 'Walk-in Customer'}</div>
						</div>
						{#if order.customer_phone}
							<div>
								<div class="text-sm text-gray-600">Phone</div>
								<div class="font-medium text-gray-900">{order.customer_phone}</div>
							</div>
						{/if}
						{#if order.table_number}
							<div>
								<div class="text-sm text-gray-600">Table</div>
								<div class="font-medium text-gray-900">{order.table_number}</div>
							</div>
						{/if}
						{#if order.notes}
							<div>
								<div class="text-sm text-gray-600">Notes</div>
								<div class="font-medium text-gray-900">{order.notes}</div>
							</div>
						{/if}
					</div>
				</div>
				
				<!-- Tenant Info -->
				<div class="bg-white rounded-lg shadow-sm border border-gray-200">
					<div class="px-6 py-4 border-b border-gray-200">
						<h2 class="text-lg font-semibold text-gray-900">Tenant Information</h2>
					</div>
					<div class="p-6">
						<div class="font-medium text-gray-900">{order.tenant_name}</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<!-- Update Status Modal -->
{#if showStatusModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
		<div class="bg-white rounded-lg max-w-md w-full p-6">
			<h2 class="text-xl font-bold text-gray-900 mb-4">Update Order Status</h2>
			
			<div class="mb-4">
				<label class="block text-sm font-medium text-gray-700 mb-2">New Status</label>
				<select
					bind:value={newStatus}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
				>
					<option value="">Select status...</option>
					{#each getAvailableStatuses() as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>
			
			<div class="flex gap-2 justify-end">
				<button
					on:click={() => { showStatusModal = false; newStatus = ''; }}
					class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
					disabled={isUpdatingStatus}
				>
					Cancel
				</button>
				<button
					on:click={handleUpdateStatus}
					disabled={!newStatus || isUpdatingStatus}
					class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{isUpdatingStatus ? 'Updating...' : 'Update Status'}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Print styles for receipt */
	@media print {
		/* Hide everything except receipt */
		:global(body > *:not(.receipt-print)) {
			display: none !important;
		}
		
		.receipt-print {
			display: block !important;
		}
	}
</style>