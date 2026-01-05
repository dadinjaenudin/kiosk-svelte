<script>
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { user, isAuthenticated, isAdmin, visibleFeatures, currentOutlet, selectedTenant } from '$lib/stores/auth';
	import { logout } from '$lib/api/auth';
	import RoleGuard from '$lib/components/RoleGuard.svelte';
	import TenantSelector from '$lib/components/TenantSelector.svelte';
	import OutletSelector from '$lib/components/OutletSelector.svelte';
	import '../app.css';

	let sidebarOpen = true;
	let mobileMenuOpen = false;
	let authCheckDone = false;
	let userMenuOpen = false;

	// Navigation items with grouping
	const navigationGroups = [
		{
			name: 'Operations',
			icon: '⚡',
			items: [
				{ name: 'Dashboard', href: '/dashboard', icon: '📊', feature: 'dashboard' },
				{ name: 'Orders', href: '/orders', icon: '📦', feature: 'orders' },
				{ name: 'Customers', href: '/customers', icon: '👥', feature: 'customers' }
			]
		},
		{
			name: 'Menu',
			icon: '🍽️',
			items: [
				{ name: 'Categories', href: '/categories', icon: '📁', feature: 'categories' },
				{ name: 'Products', href: '/products', icon: '🍽️', feature: 'products' },
				{ name: 'Toppings', href: '/toppings', icon: '🧀', feature: 'products' },
				{ name: 'Spicy Levels', href: '/spicy-levels', icon: '🌶️', feature: 'products' },
				{ name: 'Additions', href: '/additions', icon: '➕', feature: 'products' }
			]
		},
		{
			name: 'Marketing',
			icon: '🎯',
			items: [
				{ name: 'Promotions', href: '/promotions', icon: '🔥', feature: 'promotions' }
			]
		},
		{
			name: 'Analytics',
			icon: '📊',
			items: [
				{ name: 'Reports', href: '/reports', icon: '📈', feature: 'reports' }
			]
		},
		{
			name: 'System',
			icon: '⚙️',
			items: [
				{ name: 'Users', href: '/users', icon: '👤', feature: 'users' },
				{ name: 'Tenants', href: '/tenants', icon: '🏢', feature: 'tenants' },
				{ name: 'Outlets', href: '/outlets', icon: '📍', feature: 'outlets' },
				{ name: 'Kitchen Stations', href: '/kitchen-stations', icon: '🍳', feature: 'outlets' },
				{ name: 'Kitchen Station Types', href: '/kitchen-station-types', icon: '🏷️', feature: 'outlets' }
			]
		}
	];

	// Flatten navigation for backward compatibility
	const navigation = navigationGroups.flatMap(group => group.items);

	// Filter navigation groups based on user permissions (reactive)
	$: visibleNavigationGroups = navigationGroups.map(group => ({
		...group,
		items: group.items.filter(item => $visibleFeatures.includes(item.feature))
	})).filter(group => group.items.length > 0);

	// Check auth on mount
	onMount(() => {
		// Wait a tick for store to initialize from localStorage
		setTimeout(() => {
			authCheckDone = true;
			if (!$isAuthenticated && $page.url.pathname !== '/login') {
				goto('/login');
			}
		}, 100);
	});
	
	// Reactive auth check - redirect to login if logged out
	$: if (authCheckDone && !$isAuthenticated && $page.url.pathname !== '/login') {
		goto('/login');
	}

	function handleLogout() {
		logout();
	}

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	function toggleMobileMenu() {
		mobileMenuOpen = !mobileMenuOpen;
	}
	
	function handleTenantChange(tenantId) {
		console.log('=== Tenant filter changed ===');
		console.log('New tenant ID:', tenantId);
		console.log('Type:', typeof tenantId);
		selectedTenant.set(tenantId);
		console.log('Store updated. Current value:', tenantId);
		// Pages will reactively update when they subscribe to selectedTenant store
	}
	
	function toggleUserMenu() {
		userMenuOpen = !userMenuOpen;
	}
</script>

{#if $isAuthenticated}
	<div class="min-h-screen bg-gray-100">
		<!-- Sidebar for desktop -->
		<aside
			class="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transition-transform duration-300 {sidebarOpen
				? 'translate-x-0'
				: '-translate-x-full'} md:translate-x-0"
		>
			<!-- Logo -->
			<div class="h-16 flex items-center justify-between px-4 border-b border-gray-200">
				<div class="flex items-center">
					<span class="text-2xl">🏪</span>
					<span class="ml-2 text-lg font-bold text-gray-900">Food Court</span>
				</div>
				<button on:click={toggleSidebar} class="md:hidden text-gray-500 hover:text-gray-700">
					✕
				</button>
			</div>

			<!-- Navigation -->
			<nav class="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
				{#each visibleNavigationGroups as group}
					<div class="mb-4">
						<!-- Group Header -->
						<div class="px-3 mb-2 flex items-center">
							<span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">
								{group.icon} {group.name}
							</span>
						</div>
						
						<!-- Group Items -->
						{#each group.items as item}
							<a
								href={item.href}
								class="flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors {$page.url.pathname.startsWith(
									item.href
								)
									? 'bg-primary-50 text-primary-700'
									: 'text-gray-700 hover:bg-gray-50'}"
							>
								<span class="text-xl mr-3">{item.icon}</span>
								{item.name}
							</a>
						{/each}
					</div>
				{/each}
			</nav>

			<!-- Outlet Selector (Tenant Owner & Manager) -->
			<RoleGuard roles={['tenant_owner', 'manager']}>
				<div class="border-t border-gray-200 p-4">
					<OutletSelector />
				</div>
			</RoleGuard>
		</aside>

		<!-- Main content -->
		<div class="md:pl-64">
			<!-- Top header -->
			<header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sticky top-0 z-40">
				<div class="flex items-center">
					<button
						on:click={toggleSidebar}
						class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 md:hidden"
					>
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
						</svg>
					</button>
					<h1 class="ml-2 text-xl font-semibold text-gray-900">
						{#each visibleNavigationGroups as group}
							{#each group.items as item}
								{#if $page.url.pathname.startsWith(item.href)}
									{item.name}
								{/if}
							{/each}
						{/each}
					</h1>
				</div>

				<div class="flex items-center space-x-4">
					<!-- Tenant badge -->
					{#if $user?.tenant_name}
						<span class="badge badge-info">
							{$user.tenant_name}
						</span>
					{/if}
					<!-- Outlet badge -->
					{#if $currentOutlet}
						<span class="badge badge-success">
							📍 {$currentOutlet.name}
						</span>
					{/if}
					
					<!-- Tenant Selector (Admin Only) -->
					<RoleGuard roles={['admin', 'super_admin']}>
						<div class="min-w-[200px]">
							<TenantSelector selectedTenant={$selectedTenant} onChange={handleTenantChange} compact={true} />
						</div>
					</RoleGuard>
					
					<!-- Notifications -->
					<button class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 relative">
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
							/>
						</svg>
						<span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
					</button>
					
					<!-- User Profile Menu -->
					<div class="relative">
						<button 
							on:click={toggleUserMenu}
							class="flex items-center space-x-2 hover:bg-gray-50 rounded-lg px-2 py-1.5 transition-colors"
						>
							<div class="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-white font-bold text-sm">
								{$user?.username?.[0]?.toUpperCase() || 'A'}
							</div>
							<div class="hidden md:block text-left">
								<p class="text-sm font-medium text-gray-900">{$user?.username || 'Admin'}</p>
								<p class="text-xs text-gray-500 capitalize">
									{$user?.role?.replace('_', ' ') || 'admin'}
								</p>
							</div>
							<svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
							</svg>
						</button>
						
						<!-- Dropdown menu -->
						{#if userMenuOpen}
							<div class="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
								<div class="px-4 py-3 border-b border-gray-200">
									<p class="text-sm font-medium text-gray-900">{$user?.username || 'Admin'}</p>
									<p class="text-xs text-gray-500">{$user?.email || 'admin@example.com'}</p>
									<p class="text-xs text-gray-500 capitalize mt-1">
										{$user?.role?.replace('_', ' ') || 'admin'}
										{#if $user?.is_superuser}
											<span class="ml-1 px-1.5 py-0.5 text-xs bg-yellow-100 text-yellow-800 rounded">Superuser</span>
										{/if}
									</p>
								</div>
								<a 
									href="/settings" 
									class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
									on:click={() => userMenuOpen = false}
								>
									<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									</svg>
									Settings
								</a>
								<button
									on:click={() => { userMenuOpen = false; handleLogout(); }}
									class="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50"
								>
									<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
									</svg>
									Logout
								</button>
							</div>
						{/if}
					</div>
				</div>
			</header>

			<!-- Page content -->
			<main class="p-6">
				<slot />
			</main>
		</div>
	</div>
{:else}
	<slot />
{/if}
