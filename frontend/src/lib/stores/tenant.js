/**
 * Tenant Store - Multi-tenant context management
 */
import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';

// Core tenant stores
export const currentTenant = writable(null);
export const currentOutlet = writable(null);
export const currentUser = writable(null);

// Derived store for tenant ready state
export const tenantReady = derived(
	[currentTenant, currentOutlet],
	([$tenant, $outlet]) => $tenant !== null && $outlet !== null
);

/**
 * Load current tenant information from API
 */
export async function loadTenant() {
	if (!browser) return;
	
	try {
		const response = await fetch('/api/tenants/me/', {
			headers: {
				'Authorization': `Bearer ${getAuthToken()}`,
			}
		});
		
		if (response.ok) {
			const tenant = await response.json();
			currentTenant.set(tenant);
			console.log('✅ Tenant loaded:', tenant.name);
			return tenant;
		} else {
			console.error('❌ Failed to load tenant:', response.status);
			return null;
		}
	} catch (error) {
		console.error('❌ Error loading tenant:', error);
		return null;
	}
}

/**
 * Load outlets for current tenant
 */
export async function loadOutlets() {
	if (!browser) return [];
	
	try {
		const response = await fetch('/api/outlets/', {
			headers: {
				'Authorization': `Bearer ${getAuthToken()}`,
			}
		});
		
		if (response.ok) {
			const data = await response.json();
			const outlets = data.results || data;
			console.log(`✅ Loaded ${outlets.length} outlets`);
			
			// Auto-select first outlet if none selected
			const savedOutletId = localStorage.getItem('outlet_id');
			if (savedOutletId) {
				const savedOutlet = outlets.find(o => o.id === parseInt(savedOutletId));
				if (savedOutlet) {
					selectOutlet(savedOutlet);
				} else if (outlets.length > 0) {
					selectOutlet(outlets[0]);
				}
			} else if (outlets.length > 0) {
				selectOutlet(outlets[0]);
			}
			
			return outlets;
		} else {
			console.error('❌ Failed to load outlets:', response.status);
			return [];
		}
	} catch (error) {
		console.error('❌ Error loading outlets:', error);
		return [];
	}
}

/**
 * Select an outlet as current
 */
export function selectOutlet(outlet) {
	currentOutlet.set(outlet);
	if (browser) {
		localStorage.setItem('outlet_id', outlet.id);
	}
	console.log('✅ Outlet selected:', outlet.name);
}

/**
 * Load current user information
 */
export async function loadCurrentUser() {
	if (!browser) return;
	
	try {
		const response = await fetch('/api/users/me/', {
			headers: {
				'Authorization': `Bearer ${getAuthToken()}`,
			}
		});
		
		if (response.ok) {
			const user = await response.json();
			currentUser.set(user);
			console.log('✅ User loaded:', user.full_name || user.username);
			return user;
		} else {
			console.error('❌ Failed to load user:', response.status);
			return null;
		}
	} catch (error) {
		console.error('❌ Error loading user:', error);
		return null;
	}
}

/**
 * Initialize tenant context (call on app mount)
 */
export async function initializeTenantContext() {
	if (!browser) return;
	
	console.log('🔄 Initializing tenant context...');
	
	// Load tenant info
	const tenant = await loadTenant();
	if (!tenant) {
		console.warn('⚠️ No tenant loaded, redirecting to login...');
		// Could redirect to login here
		return false;
	}
	
	// Load outlets
	await loadOutlets();
	
	// Load current user
	await loadCurrentUser();
	
	console.log('✅ Tenant context initialized');
	return true;
}

/**
 * Clear tenant context (on logout)
 */
export function clearTenantContext() {
	currentTenant.set(null);
	currentOutlet.set(null);
	currentUser.set(null);
	
	if (browser) {
		localStorage.removeItem('outlet_id');
		localStorage.removeItem('auth_token');
	}
	
	console.log('✅ Tenant context cleared');
}

/**
 * Get tenant ID for API requests
 */
export function getTenantId() {
	const tenant = get(currentTenant);
	return tenant?.id || null;
}

/**
 * Get outlet ID for API requests
 */
export function getOutletId() {
	const outlet = get(currentOutlet);
	return outlet?.id || null;
}

/**
 * Get auth token from localStorage
 */
function getAuthToken() {
	if (!browser) return '';
	return localStorage.getItem('auth_token') || '';
}

/**
 * Check if user has specific permission
 */
export function hasPermission(permission) {
	const user = get(currentUser);
	if (!user) return false;
	
	// Superuser has all permissions
	if (user.is_superuser) return true;
	
	// Check role-based permissions
	const rolePermissions = {
		'owner': ['all'],
		'admin': [
			'outlet.create', 'user.create', 'user.edit',
			'product.create', 'product.edit', 'product.delete',
			'order.create', 'order.edit', 'payment.process',
			'report.view_all'
		],
		'manager': [
			'user.view', 'product.create', 'product.edit',
			'order.view', 'report.view'
		],
		'cashier': [
			'order.create', 'order.view', 'order.edit',
			'payment.process'
		],
		'kitchen': [
			'order.view_kitchen', 'order.update_status'
		],
		'waiter': [
			'order.create', 'order.view'
		]
	};
	
	const userPermissions = rolePermissions[user.role] || [];
	
	return userPermissions.includes('all') || userPermissions.includes(permission);
}

/**
 * Check if user has specific role
 */
export function hasRole(role) {
	const user = get(currentUser);
	return user?.role === role;
}

/**
 * Get tenant setting value
 */
export function getTenantSetting(key, defaultValue = null) {
	const tenant = get(currentTenant);
	return tenant?.settings?.[key] || defaultValue;
}

/**
 * Get tenant branding
 */
export function getTenantBranding() {
	const tenant = get(currentTenant);
	return {
		logo: tenant?.logo_url || '/default-logo.png',
		primaryColor: tenant?.primary_color || '#FF6B35',
		name: tenant?.name || 'POS System'
	};
}

export default {
	currentTenant,
	currentOutlet,
	currentUser,
	tenantReady,
	loadTenant,
	loadOutlets,
	selectOutlet,
	loadCurrentUser,
	initializeTenantContext,
	clearTenantContext,
	getTenantId,
	getOutletId,
	hasPermission,
	hasRole,
	getTenantSetting,
	getTenantBranding
};
