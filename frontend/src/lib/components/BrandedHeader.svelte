<script>
	import { currentTenant, currentUser, hasPermission } from '$lib/stores/tenant.js';
	import OutletSelector from './OutletSelector.svelte';
	
	export let showOutletSelector = true;
	export let title = '';
	
	// Get tenant branding
	$: logo = $currentTenant?.logo_url || '/logo.svg';
	$: tenantName = $currentTenant?.name || 'POS System';
	$: primaryColor = $currentTenant?.primary_color || '#FF6B35';
	$: userName = $currentUser?.full_name || $currentUser?.username || 'User';
	$: userRole = $currentUser?.role || 'user';
	
	// Role badge colors
	const roleBadgeColors = {
		owner: '#8B5CF6',
		admin: '#3B82F6',
		manager: '#10B981',
		cashier: '#F59E0B',
		kitchen: '#EF4444',
		waiter: '#6B7280'
	};
	
	function getRoleBadgeColor(role) {
		return roleBadgeColors[role] || '#6B7280';
	}
</script>

<header class="branded-header" style="border-bottom: 4px solid {primaryColor}">
	<div class="header-content">
		<!-- Left: Logo & Tenant Name -->
		<div class="brand-section">
			<img src={logo} alt={tenantName} class="logo" />
			<div class="brand-info">
				<h1 class="tenant-name">{tenantName}</h1>
				{#if title}
					<p class="page-title">{title}</p>
				{/if}
			</div>
		</div>
		
		<!-- Center: Outlet Selector (if enabled) -->
		{#if showOutletSelector}
			<div class="center-section">
				<OutletSelector />
			</div>
		{/if}
		
		<!-- Right: User Info -->
		<div class="user-section">
			<div class="user-info">
				<span class="user-name">{userName}</span>
				<span 
					class="role-badge" 
					style="background-color: {getRoleBadgeColor(userRole)}"
				>
					{userRole.toUpperCase()}
				</span>
			</div>
			<div class="user-avatar" style="background-color: {primaryColor}">
				{userName.charAt(0).toUpperCase()}
			</div>
		</div>
	</div>
</header>

<style>
	.branded-header {
		background: white;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
		position: sticky;
		top: 0;
		z-index: 100;
	}
	
	.header-content {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 16px 24px;
		max-width: 1920px;
		margin: 0 auto;
		gap: 24px;
	}
	
	/* Brand Section */
	.brand-section {
		display: flex;
		align-items: center;
		gap: 16px;
		flex-shrink: 0;
	}
	
	.logo {
		height: 48px;
		width: auto;
		object-fit: contain;
	}
	
	.brand-info {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	
	.tenant-name {
		font-size: 20px;
		font-weight: 700;
		color: #1f2937;
		margin: 0;
		line-height: 1.2;
	}
	
	.page-title {
		font-size: 13px;
		color: #6b7280;
		margin: 0;
	}
	
	/* Center Section */
	.center-section {
		flex: 1;
		display: flex;
		justify-content: center;
		max-width: 400px;
	}
	
	/* User Section */
	.user-section {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-shrink: 0;
	}
	
	.user-info {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 4px;
	}
	
	.user-name {
		font-size: 14px;
		font-weight: 600;
		color: #1f2937;
	}
	
	.role-badge {
		font-size: 10px;
		font-weight: 700;
		color: white;
		padding: 3px 8px;
		border-radius: 12px;
		letter-spacing: 0.5px;
	}
	
	.user-avatar {
		width: 44px;
		height: 44px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		font-size: 18px;
		font-weight: 700;
		flex-shrink: 0;
	}
	
	@media (max-width: 1024px) {
		.header-content {
			padding: 12px 16px;
		}
		.center-section {
			max-width: 300px;
		}
		.page-title {
			display: none;
		}
	}
	
	@media (max-width: 768px) {
		.header-content {
			flex-wrap: wrap;
			gap: 12px;
		}
		.brand-section {
			flex: 1;
		}
		.logo {
			height: 36px;
		}
		.tenant-name {
			font-size: 16px;
		}
		.center-section {
			order: 3;
			flex-basis: 100%;
			max-width: 100%;
		}
		.user-info {
			display: none;
		}
		.user-avatar {
			width: 36px;
			height: 36px;
			font-size: 16px;
		}
	}
</style>
