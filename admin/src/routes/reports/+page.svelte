<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import {
		getSalesSummary,
		getSalesByPeriod,
		getTopProducts,
		getTopCategories,
		getCustomerStats,
		getOrderStats,
		getPaymentMethods,
		getHourlySales,
		formatCurrency,
		formatNumber,
		formatPercentage,
		getPeriodLabel,
		getPeriodOptions
	} from '$lib/api/reports';

	export let data = {};

	// State
	let loading = true;
	let selectedPeriod = '30days';
	let customStartDate = '';
	let customEndDate = '';
	
	// Report data
	let salesSummary = {
		total_revenue: 0,
		total_orders: 0,
		average_order_value: 0,
		total_items_sold: 0,
		revenue_growth: 0,
		orders_growth: 0
	};
	let salesTrend = [];
	let topProducts = [];
	let topCategories = [];
	let customerStats = {};
	let orderStats = {};
	let paymentMethods = [];
	let hourlySales = [];
	
	// Period options
	let periodOptions = getPeriodOptions();

	onMount(() => {
		if (!$isAuthenticated) {
			goto('/login');
			return;
		}
		loadReports();
	});

	async function loadReports() {
		loading = true;
		try {
			// Load all reports in parallel
			const [
				summary,
				trend,
				products,
				categories,
				customers,
				orders,
				payments,
				hourly
			] = await Promise.all([
				getSalesSummary(selectedPeriod, customStartDate, customEndDate),
				getSalesByPeriod(selectedPeriod, 'day', customStartDate, customEndDate),
				getTopProducts(selectedPeriod, 5),
				getTopCategories(selectedPeriod),
				getCustomerStats(selectedPeriod),
				getOrderStats(selectedPeriod),
				getPaymentMethods(selectedPeriod),
				getHourlySales(selectedPeriod === 'today' ? 'today' : '7days')
			]);

			salesSummary = summary.summary || salesSummary;
			salesTrend = trend.data || [];
			topProducts = products.data || [];
			topCategories = categories.data || [];
			customerStats = customers || {};
			orderStats = orders || {};
			paymentMethods = payments.data || [];
			hourlySales = hourly.data || [];
		} catch (error) {
			console.error('Error loading reports:', error);
			alert('Failed to load reports');
		} finally {
			loading = false;
		}
	}

	function handlePeriodChange() {
		if (selectedPeriod !== 'custom') {
			customStartDate = '';
			customEndDate = '';
		}
		loadReports();
	}

	function handleCustomDateChange() {
		if (customStartDate && customEndDate) {
			loadReports();
		}
	}

	function exportReport(type) {
		// TODO: Implement export functionality
		alert(`Export ${type} report - Coming soon!`);
	}
</script>

<svelte:head>
	<title>Reports - Admin Panel</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
			<p class="text-gray-600 mt-1">View sales performance and insights</p>
		</div>
		<div class="flex gap-2">
			<button
				on:click={() => exportReport('PDF')}
				class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 flex items-center gap-2"
			>
				📄 Export PDF
			</button>
			<button
				on:click={() => exportReport('Excel')}
				class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
			>
				📊 Export Excel
			</button>
		</div>
	</div>

	<!-- Period Selector -->
	<div class="bg-white rounded-lg shadow p-4 mb-6">
		<div class="flex flex-wrap items-center gap-4">
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">Period</label>
				<select
					bind:value={selectedPeriod}
					on:change={handlePeriodChange}
					class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
				>
					{#each periodOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>

			{#if selectedPeriod === 'custom'}
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
					<input
						type="date"
						bind:value={customStartDate}
						on:change={handleCustomDateChange}
						class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
					<input
						type="date"
						bind:value={customEndDate}
						on:change={handleCustomDateChange}
						class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
					/>
				</div>
			{/if}

			<button
				on:click={loadReports}
				class="mt-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
			>
				🔄 Refresh
			</button>
		</div>
	</div>

	{#if loading}
		<div class="bg-white rounded-lg shadow p-12 text-center">
			<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			<p class="text-gray-600 mt-4">Loading reports...</p>
		</div>
	{:else}
		<!-- Summary Cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
			<!-- Total Revenue -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-4">
					<p class="text-sm font-medium text-gray-600">Total Revenue</p>
					<span class="text-2xl">💰</span>
				</div>
				<p class="text-2xl font-bold text-gray-900">{formatCurrency(salesSummary.total_revenue)}</p>
				<div class="mt-2 flex items-center text-sm">
					<span class={salesSummary.revenue_growth >= 0 ? 'text-green-600' : 'text-red-600'}>
						{formatPercentage(salesSummary.revenue_growth)}
					</span>
					<span class="text-gray-600 ml-1">vs previous period</span>
				</div>
			</div>

			<!-- Total Orders -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-4">
					<p class="text-sm font-medium text-gray-600">Total Orders</p>
					<span class="text-2xl">📦</span>
				</div>
				<p class="text-2xl font-bold text-gray-900">{formatNumber(salesSummary.total_orders)}</p>
				<div class="mt-2 flex items-center text-sm">
					<span class={salesSummary.orders_growth >= 0 ? 'text-green-600' : 'text-red-600'}>
						{formatPercentage(salesSummary.orders_growth)}
					</span>
					<span class="text-gray-600 ml-1">vs previous period</span>
				</div>
			</div>

			<!-- Average Order Value -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-4">
					<p class="text-sm font-medium text-gray-600">Avg Order Value</p>
					<span class="text-2xl">💳</span>
				</div>
				<p class="text-2xl font-bold text-gray-900">{formatCurrency(salesSummary.average_order_value)}</p>
				<p class="text-sm text-gray-600 mt-2">Per order</p>
			</div>

			<!-- Items Sold -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-4">
					<p class="text-sm font-medium text-gray-600">Items Sold</p>
					<span class="text-2xl">📊</span>
				</div>
				<p class="text-2xl font-bold text-gray-900">{formatNumber(salesSummary.total_items_sold)}</p>
				<p class="text-sm text-gray-600 mt-2">Total units</p>
			</div>
		</div>

		<!-- Charts Row 1 -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
			<!-- Top Products -->
			<div class="bg-white rounded-lg shadow p-6">
				<h3 class="text-lg font-bold text-gray-900 mb-4">Top Selling Products</h3>
				{#if topProducts.length > 0}
					<div class="space-y-4">
						{#each topProducts as product, index}
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-3 flex-1">
									<span class="text-lg font-bold text-gray-400 w-6">#{index + 1}</span>
									<div class="flex-1">
										<p class="font-medium text-gray-900">{product.product_name}</p>
										<p class="text-sm text-gray-600">
											{formatNumber(product.quantity_sold)} units • {product.orders_count} orders
										</p>
									</div>
								</div>
								<div class="text-right">
									<p class="font-bold text-gray-900">{formatCurrency(product.revenue)}</p>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-gray-600 text-center py-8">No sales data available</p>
				{/if}
			</div>

			<!-- Top Categories -->
			<div class="bg-white rounded-lg shadow p-6">
				<h3 class="text-lg font-bold text-gray-900 mb-4">Top Categories</h3>
				{#if topCategories.length > 0}
					<div class="space-y-4">
						{#each topCategories.slice(0, 5) as category, index}
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-3 flex-1">
									<span class="text-lg font-bold text-gray-400 w-6">#{index + 1}</span>
									<div class="flex-1">
										<p class="font-medium text-gray-900">{category.category_name}</p>
										<p class="text-sm text-gray-600">
											{formatNumber(category.quantity_sold)} units • {category.orders_count} orders
										</p>
									</div>
								</div>
								<div class="text-right">
									<p class="font-bold text-gray-900">{formatCurrency(category.revenue)}</p>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-gray-600 text-center py-8">No category data available</p>
				{/if}
			</div>
		</div>

		<!-- Customer & Order Stats -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
			<!-- Total Customers -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-2">
					<p class="text-sm font-medium text-gray-600">Total Customers</p>
					<span class="text-xl">👥</span>
				</div>
				<p class="text-2xl font-bold text-gray-900">{formatNumber(customerStats.total_customers || 0)}</p>
			</div>

			<!-- New Customers -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-2">
					<p class="text-sm font-medium text-gray-600">New Customers</p>
					<span class="text-xl">✨</span>
				</div>
				<p class="text-2xl font-bold text-green-600">{formatNumber(customerStats.new_customers || 0)}</p>
			</div>

			<!-- Repeat Customers -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-2">
					<p class="text-sm font-medium text-gray-600">Repeat Customers</p>
					<span class="text-xl">🔄</span>
				</div>
				<p class="text-2xl font-bold text-blue-600">{formatNumber(customerStats.repeat_customers || 0)}</p>
			</div>

			<!-- Avg Orders/Customer -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-2">
					<p class="text-sm font-medium text-gray-600">Avg Orders/Customer</p>
					<span class="text-xl">📈</span>
				</div>
				<p class="text-2xl font-bold text-gray-900">{(customerStats.average_orders_per_customer || 0).toFixed(1)}</p>
			</div>
		</div>

		<!-- Payment Methods -->
		<div class="bg-white rounded-lg shadow p-6 mb-6">
			<h3 class="text-lg font-bold text-gray-900 mb-4">Payment Methods</h3>
			{#if paymentMethods.length > 0}
				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					{#each paymentMethods as payment}
						<div class="border border-gray-200 rounded-lg p-4">
							<p class="text-sm font-medium text-gray-600 mb-2">{payment.method}</p>
							<p class="text-xl font-bold text-gray-900">{formatCurrency(payment.revenue)}</p>
							<p class="text-sm text-gray-600 mt-1">{formatNumber(payment.count)} orders</p>
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-gray-600 text-center py-8">No payment data available</p>
			{/if}
		</div>

		<!-- Sales Trend (Simple Table View) -->
		<div class="bg-white rounded-lg shadow p-6">
			<h3 class="text-lg font-bold text-gray-900 mb-4">Sales Trend</h3>
			{#if salesTrend.length > 0}
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Orders</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
							</tr>
						</thead>
						<tbody class="bg-white divide-y divide-gray-200">
							{#each salesTrend.slice(-10) as day}
								<tr class="hover:bg-gray-50">
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
										{new Date(day.period).toLocaleDateString('id-ID')}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
										{formatNumber(day.orders)}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
										{formatNumber(day.items)}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
										{formatCurrency(day.revenue)}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{:else}
				<p class="text-gray-600 text-center py-8">No sales trend data available</p>
			{/if}
		</div>
	{/if}
</div>
