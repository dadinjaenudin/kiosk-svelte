<script>
	import { onMount } from 'svelte';
	import { user, currentOutlet, accessibleOutlets } from '$lib/stores/auth';
	import { fetchAccessibleOutlets } from '$lib/stores/auth';
	
	let outlets = [];
	let loading = true;
	
	onMount(async () => {
		// Fetch accessible outlets
		await fetchAccessibleOutlets();
		outlets = $accessibleOutlets;
		loading = false;
	});
</script>

<svelte:head>
	<title>Settings - Admin Panel</title>
</svelte:head>

<div class="max-w-4xl mx-auto">
	<div class="mb-6">
		<h1 class="text-2xl font-bold text-gray-900">Settings</h1>
		<p class="text-gray-600 mt-1">View your account information and access details</p>
	</div>

	<!-- User Information Card -->
	<div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
		<div class="px-6 py-4 border-b border-gray-200">
			<h2 class="text-lg font-semibold text-gray-900">User Information</h2>
		</div>
		<div class="px-6 py-4 space-y-4">
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<!-- Username -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
					<div class="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg">
						<p class="text-gray-900">{$user?.username || '-'}</p>
					</div>
				</div>

				<!-- Email -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
					<div class="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg">
						<p class="text-gray-900">{$user?.email || '-'}</p>
					</div>
				</div>

				<!-- Role -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">Role</label>
					<div class="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg">
						<div class="flex items-center gap-2">
							<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
								{$user?.role?.replace('_', ' ') || '-'}
							</span>
							{#if $user?.is_superuser}
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
									Superuser
								</span>
							{/if}
						</div>
					</div>
				</div>

				<!-- User ID -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">User ID</label>
					<div class="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg">
						<p class="text-gray-900 font-mono text-sm">{$user?.id || '-'}</p>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Tenant Information Card -->
	<div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
		<div class="px-6 py-4 border-b border-gray-200">
			<h2 class="text-lg font-semibold text-gray-900">Tenant Access</h2>
		</div>
		<div class="px-6 py-4">
			{#if $user?.role === 'super_admin' || $user?.role === 'admin'}
				<div class="bg-green-50 border border-green-200 rounded-lg p-4">
					<div class="flex items-center">
						<svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
						</svg>
						<div>
							<p class="font-medium text-green-900">All Tenants Access</p>
							<p class="text-sm text-green-700">You have access to all tenants in the system</p>
						</div>
					</div>
				</div>
			{:else if $user?.tenant_name}
				<div class="space-y-3">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">Assigned Tenant</label>
						<div class="px-4 py-3 bg-purple-50 border border-purple-200 rounded-lg">
							<div class="flex items-center">
								<svg class="w-5 h-5 text-purple-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clip-rule="evenodd"/>
								</svg>
								<div>
									<p class="font-semibold text-purple-900">{$user.tenant_name}</p>
									<p class="text-sm text-purple-700">Tenant ID: {$user.tenant}</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			{:else}
				<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
					<p class="text-gray-600">No tenant assigned</p>
				</div>
			{/if}
		</div>
	</div>

	<!-- Outlet Access Card -->
	<div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
		<div class="px-6 py-4 border-b border-gray-200">
			<h2 class="text-lg font-semibold text-gray-900">Outlet Access</h2>
		</div>
		<div class="px-6 py-4">
			{#if loading}
				<div class="flex items-center justify-center py-8">
					<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
					<p class="ml-3 text-gray-600">Loading outlets...</p>
				</div>
			{:else if $user?.role === 'super_admin' || $user?.role === 'admin'}
				<div class="bg-green-50 border border-green-200 rounded-lg p-4">
					<div class="flex items-center">
						<svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
						</svg>
						<div>
							<p class="font-medium text-green-900">All Outlets Access</p>
							<p class="text-sm text-green-700">You have access to all outlets in all tenants</p>
						</div>
					</div>
				</div>
			{:else if $user?.role === 'tenant_owner'}
				<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
					<div class="flex items-center">
						<svg class="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
						</svg>
						<div>
							<p class="font-medium text-blue-900">Tenant Owner - All Outlets</p>
							<p class="text-sm text-blue-700">You have access to all outlets in your tenant</p>
						</div>
					</div>
				</div>
				{#if outlets.length > 0}
					<div class="mt-4">
						<h3 class="text-sm font-medium text-gray-700 mb-3">Available Outlets ({outlets.length})</h3>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
							{#each outlets as outlet}
								<div class="px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg">
									<div class="flex items-start">
										<svg class="w-5 h-5 text-gray-600 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
										</svg>
										<div class="flex-1">
											<p class="font-medium text-gray-900">{outlet.name}</p>
											{#if outlet.address}
												<p class="text-xs text-gray-500 mt-1">{outlet.address}</p>
											{/if}
											{#if $currentOutlet?.id === outlet.id}
												<span class="inline-flex items-center mt-2 px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
													Current
												</span>
											{/if}
										</div>
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			{:else if $user?.role === 'manager' && outlets.length > 0}
				<div class="space-y-4">
					<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
						<p class="text-sm text-blue-900">
							<span class="font-medium">Manager Access:</span> You can access {outlets.length} outlet{outlets.length > 1 ? 's' : ''}
						</p>
					</div>
					<div>
						<h3 class="text-sm font-medium text-gray-700 mb-3">Accessible Outlets</h3>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
							{#each outlets as outlet}
								<div class="px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg">
									<div class="flex items-start">
										<svg class="w-5 h-5 text-gray-600 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
											<path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
										</svg>
										<div class="flex-1">
											<p class="font-medium text-gray-900">{outlet.name}</p>
											{#if outlet.address}
												<p class="text-xs text-gray-500 mt-1">{outlet.address}</p>
											{/if}
											{#if $currentOutlet?.id === outlet.id}
												<span class="inline-flex items-center mt-2 px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
													Current
												</span>
											{/if}
										</div>
									</div>
								</div>
							{/each}
						</div>
					</div>
				</div>
			{:else if $user?.outlet_name}
				<!-- Single outlet for cashier/kitchen -->
				<div class="space-y-3">
					<div class="bg-orange-50 border border-orange-200 rounded-lg p-4">
						<p class="text-sm text-orange-900">
							<span class="font-medium">Single Outlet Access:</span> You are assigned to one specific outlet
						</p>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">Assigned Outlet</label>
						<div class="px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg">
							<div class="flex items-start">
								<svg class="w-5 h-5 text-gray-600 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
								</svg>
								<div>
									<p class="font-semibold text-gray-900">{$user.outlet_name}</p>
									<p class="text-sm text-gray-600 mt-1">Outlet ID: {$user.outlet}</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			{:else}
				<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
					<p class="text-gray-600">No outlet assigned</p>
				</div>
			{/if}
		</div>
	</div>

	<!-- Permissions Info -->
	<div class="bg-white rounded-lg shadow-sm border border-gray-200">
		<div class="px-6 py-4 border-b border-gray-200">
			<h2 class="text-lg font-semibold text-gray-900">Role Permissions</h2>
		</div>
		<div class="px-6 py-4">
			<div class="space-y-3">
				{#if $user?.role === 'super_admin'}
					<div class="flex items-start">
						<svg class="w-5 h-5 text-green-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
						</svg>
						<div>
							<p class="font-medium text-gray-900">Full System Access</p>
							<p class="text-sm text-gray-600">Complete control over all tenants, outlets, users, and data</p>
						</div>
					</div>
				{:else if $user?.role === 'admin'}
					<div class="flex items-start">
						<svg class="w-5 h-5 text-green-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
						</svg>
						<div>
							<p class="font-medium text-gray-900">Admin Access</p>
							<p class="text-sm text-gray-600">Manage all tenants, outlets, products, orders, and users</p>
						</div>
					</div>
				{:else if $user?.role === 'tenant_owner'}
					<div class="flex items-start">
						<svg class="w-5 h-5 text-blue-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
						</svg>
						<div>
							<p class="font-medium text-gray-900">Tenant Owner Access</p>
							<p class="text-sm text-gray-600">Manage all outlets in your tenant: products, orders, promotions, outlets, and staff</p>
						</div>
					</div>
				{:else if $user?.role === 'manager'}
					<div class="flex items-start">
						<svg class="w-5 h-5 text-blue-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
						</svg>
						<div>
							<p class="font-medium text-gray-900">Manager Access</p>
							<p class="text-sm text-gray-600">Manage products, orders, and promotions for accessible outlets</p>
						</div>
					</div>
				{:else if $user?.role === 'cashier'}
					<div class="flex items-start">
						<svg class="w-5 h-5 text-orange-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
						</svg>
						<div>
							<p class="font-medium text-gray-900">Cashier Access</p>
							<p class="text-sm text-gray-600">View products and manage orders for your assigned outlet</p>
						</div>
					</div>
				{:else if $user?.role === 'kitchen'}
					<div class="flex items-start">
						<svg class="w-5 h-5 text-red-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
						</svg>
						<div>
							<p class="font-medium text-gray-900">Kitchen Staff Access</p>
							<p class="text-sm text-gray-600">View and update orders for your assigned outlet</p>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	.badge {
		@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
	}
	.badge-info {
		@apply bg-purple-100 text-purple-800;
	}
	.badge-success {
		@apply bg-green-100 text-green-800;
	}
</style>
