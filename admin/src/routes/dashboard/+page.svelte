<script>
	import { onMount } from 'svelte';
	import { user } from '$lib/stores/auth';
	import { getDashboardAnalytics } from '$lib/api/dashboard';
	import RevenueChart from '$lib/components/RevenueChart.svelte';

	let stats = {
		today_revenue: 0,
		today_orders: 0,
		pending_orders: 0,
		completed_orders: 0,
		revenue_trend: 0,
		orders_trend: 0
	};

	let topProducts = [];
	let recentOrders = [];
	let revenueChartData = [];
	let loading = true;
	let error = null;
	let selectedPeriod = 'today';

	async function loadDashboard() {
		loading = true;
		error = null;
		
		try {
			const data = await getDashboardAnalytics({ period: selectedPeriod });
			
			// Update stats
			stats = {
				today_revenue: data.metrics.total_revenue,
				today_orders: data.metrics.total_orders,
				pending_orders: data.metrics.pending_orders,
				completed_orders: data.metrics.completed_orders,
				revenue_trend: data.metrics.revenue_trend,
				orders_trend: data.metrics.orders_trend
			};
			
			// Update revenue chart data
			revenueChartData = data.revenue_chart || [];
			
			// Update top products
			topProducts = data.top_products.map(p => ({
				name: p.product_name,
				sold: p.total_sold,
				revenue: p.total_revenue
			}));
			
			// Update recent orders
			recentOrders = data.recent_orders.map(o => ({
				id: o.id,
				order_number: o.order_number,
				customer: o.customer_name,
				total: o.total_amount,
				status: o.status,
				time: o.time_ago
			}));
			
			loading = false;
		} catch (err) {
			console.error('Failed to load dashboard:', err);
			error = err.message;
			loading = false;
		}
	}

	onMount(() => {
		loadDashboard();
	});

	function changePeriod(period) {
		selectedPeriod = period;
		loadDashboard();
	}

	function formatCurrency(amount) {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(amount);
	}

	function getStatusColor(status) {
		const colors = {
			pending: 'badge-warning',
			preparing: 'badge-info',
			ready: 'badge-success',
			completed: 'badge-success'
		};
		return colors[status] || 'badge-info';
	}
</script>

<svelte:head>
	<title>Dashboard - Admin Panel</title>
</svelte:head>

<div class="space-y-6">
	<!-- Welcome message -->
	<div class="flex items-center justify-between">
		<div>
			<h2 class="text-2xl font-bold text-gray-900">Welcome back, {$user?.username || 'Admin'}! 👋</h2>
			<p class="text-gray-600 mt-1">Here's what's happening with your food court today.</p>
		</div>
		
		<!-- Period selector -->
		<div class="flex gap-2">
			<button
				class="btn {selectedPeriod === 'today' ? 'btn-primary' : 'btn-secondary'}"
				on:click={() => changePeriod('today')}
			>
				Today
			</button>
			<button
				class="btn {selectedPeriod === 'week' ? 'btn-primary' : 'btn-secondary'}"
				on:click={() => changePeriod('week')}
			>
				Week
			</button>
			<button
				class="btn {selectedPeriod === 'month' ? 'btn-primary' : 'btn-secondary'}"
				on:click={() => changePeriod('month')}
			>
				Month
			</button>
		</div>
	</div>

	{#if error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4">
			<p class="text-red-800">Error loading dashboard: {error}</p>
			<button class="btn btn-secondary mt-2" on:click={loadDashboard}>Retry</button>
		</div>
	{/if}

	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
		</div>
	{:else}
		<!-- Stats cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<!-- Today's Revenue -->
			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">Revenue</p>
						<p class="text-2xl font-bold text-gray-900 mt-2">
							{formatCurrency(stats.today_revenue)}
						</p>
						<p class="text-sm mt-2 flex items-center {stats.revenue_trend >= 0 ? 'text-green-600' : 'text-red-600'}">
							<span class="mr-1">{stats.revenue_trend >= 0 ? '↑' : '↓'}</span> 
							{Math.abs(stats.revenue_trend).toFixed(1)}% from previous period
						</p>
					</div>
					<div class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center text-2xl">
						💰
					</div>
				</div>
			</div>

			<!-- Today's Orders -->
			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">Orders</p>
						<p class="text-2xl font-bold text-gray-900 mt-2">{stats.today_orders}</p>
						<p class="text-sm mt-2 flex items-center {stats.orders_trend >= 0 ? 'text-green-600' : 'text-red-600'}">
							<span class="mr-1">{stats.orders_trend >= 0 ? '↑' : '↓'}</span> 
							{Math.abs(stats.orders_trend).toFixed(1)}% from previous period
						</p>
					</div>
					<div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-2xl">
						📦
					</div>
				</div>
			</div>

			<!-- Pending Orders -->
			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">Pending Orders</p>
						<p class="text-2xl font-bold text-gray-900 mt-2">{stats.pending_orders}</p>
						<p class="text-sm text-gray-600 mt-2">Needs attention</p>
					</div>
					<div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center text-2xl">
						⏳
					</div>
				</div>
			</div>

			<!-- Completed Orders -->
			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">Completed Orders</p>
						<p class="text-2xl font-bold text-gray-900 mt-2">{stats.completed_orders}</p>
						<p class="text-sm text-green-600 mt-2">Success rate: {stats.today_orders > 0 ? ((stats.completed_orders / stats.today_orders) * 100).toFixed(1) : 0}%</p>
					</div>
					<div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-2xl">
						✅
					</div>
				</div>
			</div>
		</div>

		<!-- Revenue Chart -->
		<div class="card">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Revenue Trend</h3>
			{#if revenueChartData.length > 0}
				<RevenueChart 
					data={revenueChartData} 
					label="Revenue (IDR)" 
					type="line" 
				/>
			{:else}
				<div class="h-[300px] flex items-center justify-center text-gray-500">
					<p>No revenue data available</p>
				</div>
			{/if}
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Top Products -->
			<div class="card">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Top Selling Products</h3>
				<div class="space-y-3">
					{#each topProducts as product, i}
						<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
							<div class="flex items-center">
								<span class="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3">
									{i + 1}
								</span>
								<div>
									<p class="text-sm font-medium text-gray-900">{product.name}</p>
									<p class="text-xs text-gray-500">{product.sold} sold</p>
								</div>
							</div>
							<p class="text-sm font-semibold text-gray-900">
								{formatCurrency(product.revenue)}
							</p>
						</div>
					{/each}
				</div>
			</div>

			<!-- Recent Orders -->
			<div class="card">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-lg font-semibold text-gray-900">Recent Orders</h3>
					<a href="/orders" class="text-sm text-primary-600 hover:text-primary-700">View all →</a>
				</div>
				<div class="space-y-3">
					{#each recentOrders as order}
						<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
							<div class="flex-1">
								<div class="flex items-center justify-between mb-1">
									<p class="text-sm font-medium text-gray-900">{order.order_number}</p>
									<span class="badge {getStatusColor(order.status)}">{order.status}</span>
								</div>
								<p class="text-xs text-gray-500">{order.customer} • {order.time}</p>
							</div>
							<p class="text-sm font-semibold text-gray-900 ml-4">
								{formatCurrency(order.total)}
							</p>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="card">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
				<a href="/orders" class="p-4 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors text-center">
					<div class="text-3xl mb-2">📦</div>
					<p class="text-sm font-medium text-gray-900">View Orders</p>
				</a>
				<a href="/promotions/create" class="p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors text-center">
					<div class="text-3xl mb-2">🔥</div>
					<p class="text-sm font-medium text-gray-900">Create Promo</p>
				</a>
				<a href="/customers" class="p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors text-center">
					<div class="text-3xl mb-2">👥</div>
					<p class="text-sm font-medium text-gray-900">Customers</p>
				</a>
				<a href="/reports" class="p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors text-center">
					<div class="text-3xl mb-2">📈</div>
					<p class="text-sm font-medium text-gray-900">Reports</p>
				</a>
			</div>
		</div>
	{/if}
</div>
