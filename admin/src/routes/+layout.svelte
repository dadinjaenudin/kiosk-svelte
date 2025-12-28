<script>
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { user, isAuthenticated, canAccess } from '$lib/stores/auth';
	import { logout } from '$lib/api/auth';
	import '../app.css';

	let sidebarOpen = true;
	let mobileMenuOpen = false;

	// Navigation items
	const navigation = [
		{ name: 'Dashboard', href: '/dashboard', icon: '📊', feature: 'dashboard' },
		{ name: 'Orders', href: '/orders', icon: '📦', feature: 'orders' },
		{ name: 'Customers', href: '/customers', icon: '👥', feature: 'customers' },
		{ name: 'Promotions', href: '/promotions', icon: '🔥', feature: 'promotions' },
		{ name: 'Products', href: '/products', icon: '🍽️', feature: 'products' },
		{ name: 'Toppings', href: '/toppings', icon: '🧀', feature: 'products' },
		{ name: 'Additions', href: '/additions', icon: '➕', feature: 'products' },
		{ name: 'Reports', href: '/reports', icon: '📈', feature: 'reports' },
		{ name: 'Users', href: '/users', icon: '👤', feature: 'users' },
		{ name: 'Settings', href: '/settings', icon: '⚙️', feature: 'settings' }
	];

	// Filter navigation based on user permissions
	$: visibleNavigation = navigation.filter((item) => canAccess(item.feature));

	// Check auth on mount
	onMount(() => {
		if (!$isAuthenticated && $page.url.pathname !== '/login') {
			goto('/login');
		}
	});

	function handleLogout() {
		logout();
	}

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	function toggleMobileMenu() {
		mobileMenuOpen = !mobileMenuOpen;
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
				{#each visibleNavigation as item}
					<a
						href={item.href}
						class="flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors {$page.url.pathname.startsWith(
							item.href
						)
							? 'bg-primary-50 text-primary-700'
							: 'text-gray-700 hover:bg-gray-50'}"
					>
						<span class="text-xl mr-3">{item.icon}</span>
						{item.name}
					</a>
				{/each}
			</nav>

			<!-- User info -->
			<div class="border-t border-gray-200 p-4">
				<div class="flex items-center">
					<div class="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-bold">
						{$user?.username?.[0]?.toUpperCase() || 'A'}
					</div>
					<div class="ml-3 flex-1">
						<p class="text-sm font-medium text-gray-900">{$user?.username || 'Admin'}</p>
						<p class="text-xs text-gray-500">{$user?.role || 'admin'}</p>
					</div>
				</div>
				<button
					on:click={handleLogout}
					class="mt-3 w-full btn btn-secondary text-sm py-2"
				>
					Logout
				</button>
			</div>
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
						{navigation.find((n) => $page.url.pathname.startsWith(n.href))?.name || 'Dashboard'}
					</h1>
				</div>

				<div class="flex items-center space-x-4">
					<!-- Tenant badge -->
					{#if $user?.tenant_name}
						<span class="badge badge-info">
							{$user.tenant_name}
						</span>
					{/if}

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
