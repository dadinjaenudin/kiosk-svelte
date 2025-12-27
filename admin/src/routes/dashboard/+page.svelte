<script>
	import { onMount } from 'svelte';
	import { user } from '$lib/stores/auth';

	let stats = {
		today_revenue: 0,
		today_orders: 0,
		pending_orders: 0,
		completed_orders: 0
	};

	let topProducts = [];
	let recentOrders = [];
	let loading = true;

	onMount(async () => {
		// TODO: Fetch dashboard data from API
		// For now, using mock data
		setTimeout(() => {
			stats = {
				today_revenue: 15750000,
				today_orders: 127,
				pending_orders: 8,
				completed_orders: 119
			};

			topProducts = [
				{ name: 'Ayam Geprek Keju', sold: 45, revenue: 1575000 },
				{ name: 'Nasi Goreng Spesial', sold: 38, revenue: 1064000 },
				{ name: 'Rendang Sapi', sold: 32, revenue: 1440000 },
				{ name: 'Mie Ayam Jumbo', sold: 28, revenue: 896000 },
				{ name: 'Soto Betawi', sold: 25, revenue: 950000 }
			];

			recentOrders = [
				{ id: 1, order_number: 'ORD-001', customer: 'John Doe', total: 125000, status: 'completed', time: '5 min ago' },
				{ id: 2, order_number: 'ORD-002', customer: 'Jane Smith', total: 85000, status: 'preparing', time: '8 min ago' },
				{ id: 3, order_number: 'ORD-003', customer: 'Bob Wilson', total: 150000, status: 'ready', time: '12 min ago' },
				{ id: 4, order_number: 'ORD-004', customer: 'Alice Brown', total: 95000, status: 'pending', time: '15 min ago' },
				{ id: 5, order_number: 'ORD-005', customer: 'Charlie Davis', total: 110000, status: 'completed', time: '18 min ago' }
			];

			loading = false;
		}, 500);
	});

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
	<div>
		<h2 class="text-2xl font-bold text-gray-900">Welcome back, {$user?.username || 'Admin'}! 👋</h2>
		<p class="text-gray-600 mt-1">Here's what's happening with your food court today.</p>
	</div>

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
						<p class="text-sm text-gray-600">Today's Revenue</p>
						<p class="text-2xl font-bold text-gray-900 mt-2">
							{formatCurrency(stats.today_revenue)}
						</p>
						<p class="text-sm text-green-600 mt-2 flex items-center">
							<span class="mr-1">↑</span> 12.5% from yesterday
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
						<p class="text-sm text-gray-600">Today's Orders</p>
						<p class="text-2xl font-bold text-gray-900 mt-2">{stats.today_orders}</p>
						<p class="text-sm text-green-600 mt-2 flex items-center">
							<span class="mr-1">↑</span> 8.3% from yesterday
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
						<p class="text-sm text-green-600 mt-2">Today's success</p>
					</div>
					<div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-2xl">
						✅
					</div>
				</div>
			</div>
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
