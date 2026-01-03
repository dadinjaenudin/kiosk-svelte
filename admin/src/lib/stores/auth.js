import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';

// ============================================================================
// ROLE HIERARCHY & CONSTANTS
// ============================================================================

export const ROLE_HIERARCHY = {
	super_admin: 100,  // Platform superadmin - all access
	admin: 90,         // Multi-tenant admin - all access
	tenant_owner: 80,  // Tenant owner - all outlets in tenant
	manager: 50,       // Tenant manager - full tenant access
	cashier: 30,       // Cashier - create orders, process payments
	kitchen: 20        // Kitchen staff - view & update order status
};

// Legacy role mapping for backward compatibility
const LEGACY_ROLE_MAP = {
	owner: 'manager',
	outlet_manager: 'manager'
};

// ============================================================================
// STORES
// ============================================================================

// User store
export const user = writable(null);

// Current outlet store (for multi-outlet support)
export const currentOutlet = writable(null);

// Accessible outlets store
export const accessibleOutlets = writable([]);

// Selected tenant filter (for admin/super_admin global filtering)
export const selectedTenant = writable(null);

// Loading state
export const isLoading = writable(false);

// Error state
export const authError = writable(null);

// Check if user is authenticated
export const isAuthenticated = derived(user, ($user) => $user !== null);

// Check if user is admin or super_admin
export const isAdmin = derived(user, ($user) => {
	if (!$user) return false;
	return $user.role === 'admin' || $user.role === 'super_admin' || $user.is_superuser;
});

// Check if user is tenant owner
export const isTenantOwner = derived(user, ($user) => {
	if (!$user) return false;
	return $user.role === 'tenant_owner' || $user.is_superuser;
});

// Get normalized role (convert legacy roles)
export const normalizedRole = derived(user, ($user) => {
	if (!$user) return null;
	return LEGACY_ROLE_MAP[$user.role] || $user.role;
});

// ============================================================================
// INITIALIZATION & PERSISTENCE
// ============================================================================

// Load user from localStorage on init
if (browser) {
	const storedUser = localStorage.getItem('admin_user');
	const storedToken = localStorage.getItem('admin_token');
	const storedOutletId = localStorage.getItem('admin_current_outlet_id');
	
	if (storedUser && storedToken) {
		try {
			const userData = JSON.parse(storedUser);
			user.set({ ...userData, token: storedToken });
			
			// Set accessible outlets if available
			if (userData.accessible_outlets) {
				accessibleOutlets.set(userData.accessible_outlets);
			}
			
			// Restore current outlet if stored
			if (storedOutletId && userData.accessible_outlets) {
				const outlet = userData.accessible_outlets.find(o => String(o.id) === storedOutletId);
				if (outlet) {
					currentOutlet.set(outlet);
				}
			}
		} catch (e) {
			console.error('Failed to parse stored user:', e);
			localStorage.removeItem('admin_user');
			localStorage.removeItem('admin_token');
			localStorage.removeItem('admin_current_outlet_id');
		}
	}
}

// Subscribe to user changes and persist to localStorage
if (browser) {
	user.subscribe((value) => {
		if (value) {
			const { token, ...userData } = value;
			localStorage.setItem('admin_user', JSON.stringify(userData));
			if (token) {
				localStorage.setItem('admin_token', token);
			}
			
			// Update accessible outlets
			if (value.accessible_outlets) {
				accessibleOutlets.set(value.accessible_outlets);
			}
		} else {
			localStorage.removeItem('admin_user');
			localStorage.removeItem('admin_token');
			localStorage.removeItem('admin_current_outlet_id');
			accessibleOutlets.set([]);
			currentOutlet.set(null);
		}
	});
	
	// Persist current outlet to localStorage
	currentOutlet.subscribe((value) => {
		if (value) {
			localStorage.setItem('admin_current_outlet_id', String(value.id));
		} else {
			localStorage.removeItem('admin_current_outlet_id');
		}
	});
}

// ============================================================================
// ROLE CHECKING FUNCTIONS
// ============================================================================

/**
 * Get numeric level for a role
 * @param {string} role - Role name
 * @returns {number} Role level
 */
export function getRoleLevel(role) {
	const normalizedRole = LEGACY_ROLE_MAP[role] || role;
	return ROLE_HIERARCHY[normalizedRole] || 0;
}

/**
 * Check if user has specific role(s)
 * @param {...string} roles - Role names to check
 * @returns {boolean} True if user has any of the specified roles
 */
export function hasRole(...roles) {
	const currentUser = get(user);
	if (!currentUser) return false;
	
	const userRole = LEGACY_ROLE_MAP[currentUser.role] || currentUser.role;
	return roles.includes(userRole) || currentUser.is_superuser;
}

/**
 * Check if user has role level equal or higher than required
 * @param {string} requiredRole - Minimum required role
 * @returns {boolean} True if user meets role requirement
 */
export function hasRoleLevel(requiredRole) {
	const currentUser = get(user);
	if (!currentUser) return false;
	
	// Superuser always passes
	if (currentUser.is_superuser) return true;
	
	const userLevel = getRoleLevel(currentUser.role);
	const requiredLevel = getRoleLevel(requiredRole);
	
	return userLevel >= requiredLevel;
}

/**
 * Check if user can access specific tenant
 * @param {number|string} tenantId - Tenant ID to check
 * @returns {boolean} True if user can access tenant
 */
export function canAccessTenant(tenantId) {
	const currentUser = get(user);
	if (!currentUser) return false;
	
	// Admin can access all tenants
	if (currentUser.is_superuser || currentUser.role === 'admin' || currentUser.role === 'super_admin') {
		return true;
	}
	
	// Regular users can only access their own tenant
	return currentUser.tenant && String(currentUser.tenant) === String(tenantId);
}

/**
 * Get list of tenant IDs user can access
 * @returns {number[]|null} Array of tenant IDs, or null for all tenants (admin)
 */
export function getAccessibleTenants() {
	const currentUser = get(user);
	if (!currentUser) return [];
	
	// Admin can access all tenants
	if (currentUser.is_superuser || currentUser.role === 'admin' || currentUser.role === 'super_admin') {
		return null; // null means all tenants
	}
	
	// Regular users can only access their tenant
	return currentUser.tenant ? [currentUser.tenant] : [];
}

// ============================================================================
// PERMISSION CHECKING FUNCTIONS
// ============================================================================

/**
 * Check if user can perform action on resource
 * @param {string} action - Action name (create, read, update, delete)
 * @param {string} resource - Resource name (products, orders, users, etc)
 * @returns {boolean} True if user has permission
 */
export function canPerform(action, resource) {
	const currentUser = get(user);
	if (!currentUser) return false;
	
	const userRole = LEGACY_ROLE_MAP[currentUser.role] || currentUser.role;
	
	// Admin has all permissions
	if (currentUser.is_superuser || userRole === 'admin' || userRole === 'super_admin') {
		return true;
	}
	
	// Permission matrix
	const permissions = {
		tenant_owner: {
			products: ['create', 'read', 'update', 'delete'],
			categories: ['create', 'read', 'update', 'delete'],
			orders: ['create', 'read', 'update', 'delete'],
			customers: ['create', 'read', 'update', 'delete'],
			promotions: ['create', 'read', 'update', 'delete'],
			outlets: ['create', 'read', 'update', 'delete'],
			reports: ['read'],
			users: ['read']
		},
		manager: {
			products: ['create', 'read', 'update', 'delete'],
			categories: ['create', 'read', 'update', 'delete'],
			orders: ['create', 'read', 'update', 'delete'],
			customers: ['create', 'read', 'update', 'delete'],
			promotions: ['create', 'read', 'update', 'delete'],
			reports: ['read'],
			outlets: ['read', 'update'],
			users: ['read']
		},
		cashier: {
			products: ['read'],
			categories: ['read'],
			orders: ['create', 'read', 'update'],
			customers: ['create', 'read'],
			payments: ['create', 'read']
		},
		kitchen: {
			orders: ['read', 'update']
		}
	};
	
	const rolePermissions = permissions[userRole] || {};
	const resourcePermissions = rolePermissions[resource] || [];
	
	return resourcePermissions.includes(action);
}

/**
 * Shortcut: Can create resource
 */
export function canCreate(resource) {
	return canPerform('create', resource);
}

/**
 * Shortcut: Can read resource
 */
export function canRead(resource) {
	return canPerform('read', resource);
}

/**
 * Shortcut: Can update resource
 */
export function canUpdate(resource) {
	return canPerform('update', resource);
}

/**
 * Shortcut: Can delete resource
 */
export function canDelete(resource) {
	return canPerform('delete', resource);
}

// ============================================================================
// FEATURE ACCESS (for navigation menu)
// ============================================================================

/**
 * Check if user can access feature/page
 * @param {string} feature - Feature name
 * @returns {boolean} True if user has access
 */
export function canAccess(feature) {
	const currentUser = get(user);
	if (!currentUser) return false;
	
	const userRole = LEGACY_ROLE_MAP[currentUser.role] || currentUser.role;
	
	const featureAccess = {
		admin: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'categories', 'reports', 'users', 'tenants', 'outlets', 'settings'],
		super_admin: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'categories', 'reports', 'users', 'tenants', 'outlets', 'settings'],
		manager: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'categories', 'reports', 'outlets'],
		cashier: ['dashboard', 'orders', 'customers'],
		kitchen: ['orders']
	};
	
	return featureAccess[userRole]?.includes(feature) || false;
}

// Derived store for navigation visibility (reactive)
export const visibleFeatures = derived(user, ($user) => {
	if (!$user) return [];

	const userRole = LEGACY_ROLE_MAP[$user.role] || $user.role;

	const featureAccess = {
		admin: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'categories', 'reports', 'users', 'tenants', 'outlets', 'settings'],
		super_admin: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'categories', 'reports', 'users', 'tenants', 'outlets', 'settings'],
		manager: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'categories', 'reports', 'outlets'],
		cashier: ['dashboard', 'orders', 'customers'],
		kitchen: ['orders']
	};

	return featureAccess[userRole] || [];
});

// ============================================================================
// AUTH ACTIONS
// ============================================================================

/**
 * Login user
 * @param {object} credentials - Username and password
 * @returns {Promise<object>} User data with token
 */
export async function login(credentials) {
	isLoading.set(true);
	authError.set(null);
	
	try {
		const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/auth/login/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(credentials)
		});
		
		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.detail || 'Login failed');
		}
		
		const data = await response.json();
		
		// Set user with token
		user.set({
			...data.user,
			token: data.token
		});
		
		return data;
	} catch (error) {
		authError.set(error.message);
		throw error;
	} finally {
		isLoading.set(false);
	}
}

/**
 * Logout user
 */
export function logout() {
	user.set(null);
	authError.set(null);
	
	if (browser) {
		localStorage.removeItem('admin_user');
		localStorage.removeItem('admin_token');
	}
}

/**
 * Get current user from API
 * @returns {Promise<object>} User data
 */
export async function fetchCurrentUser() {
	const currentUser = get(user);
	if (!currentUser?.token) {
		throw new Error('No authentication token');
	}
	
	try {
		const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/auth/me/`, {
			headers: {
				'Authorization': `Bearer ${currentUser.token}`
			}
		});
		
		if (!response.ok) {
			throw new Error('Failed to fetch user');
		}
		
		const userData = await response.json();
		
		// Update user but keep token
		user.set({
			...userData,
			token: currentUser.token
		});
		
		// Update accessible outlets
		if (userData.accessible_outlets) {
			accessibleOutlets.set(userData.accessible_outlets);
			
			// If user has outlets but no current outlet set, set first one
			if (userData.accessible_outlets.length > 0 && !get(currentOutlet)) {
				// Check if there's a stored outlet
				const storedOutletId = browser ? localStorage.getItem('admin_current_outlet_id') : null;
				if (storedOutletId) {
					const storedOutlet = userData.accessible_outlets.find(o => String(o.id) === storedOutletId);
					if (storedOutlet) {
						currentOutlet.set(storedOutlet);
					} else {
						currentOutlet.set(userData.accessible_outlets[0]);
					}
				} else {
					currentOutlet.set(userData.accessible_outlets[0]);
				}
			}
		}
		
		return userData;
	} catch (error) {
		console.error('Failed to fetch current user:', error);
		// On auth error, logout
		if (error.message.includes('401') || error.message.includes('403')) {
			logout();
		}
		throw error;
	}
}

// ============================================================================
// OUTLET MANAGEMENT FUNCTIONS
// ============================================================================

/**
 * Set current outlet
 * @param {object} outlet - Outlet object
 */
export function setCurrentOutlet(outlet) {
	currentOutlet.set(outlet);
}

/**
 * Get current outlet
 * @returns {object|null} Current outlet
 */
export function getCurrentOutlet() {
	return get(currentOutlet);
}

/**
 * Check if user can access outlet
 * @param {number|string} outletId - Outlet ID
 * @returns {boolean} True if user can access
 */
export function canAccessOutlet(outletId) {
	const currentUser = get(user);
	if (!currentUser) return false;
	
	// Admin can access all outlets
	if (currentUser.is_superuser || currentUser.role === 'admin' || currentUser.role === 'super_admin') {
		return true;
	}
	
	// Tenant owner can access all outlets in their tenant
	if (currentUser.role === 'tenant_owner') {
		return true;
	}
	
	// Check accessible_outlets
	const outlets = get(accessibleOutlets);
	if (Array.isArray(outlets)) {
		return outlets.some(o => String(o.id) === String(outletId));
	}
	
	// Check user's primary outlet
	if (currentUser.outlet) {
		return String(currentUser.outlet) === String(outletId);
	}
	
	return false;
}

/**
 * Switch to outlet (calls API to set outlet context)
 * @param {number} outletId - Outlet ID to switch to
 * @returns {Promise<object>} Outlet data
 */
export async function switchOutlet(outletId) {
	const currentUser = get(user);
	if (!currentUser?.token) {
		throw new Error('No authentication token');
	}
	
	try {
		const response = await fetch(
			`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/outlets/${outletId}/set_current/`,
			{
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${currentUser.token}`,
					'Content-Type': 'application/json'
				}
			}
		);
		
		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.detail || error.error || 'Failed to switch outlet');
		}
		
		const data = await response.json();
		
		// Update current outlet in store
		if (data.outlet) {
			currentOutlet.set(data.outlet);
		}
		
		return data;
	} catch (error) {
		console.error('Failed to switch outlet:', error);
		throw error;
	}
}

/**
 * Fetch accessible outlets for current user
 * @returns {Promise<object[]>} Array of outlets
 */
export async function fetchAccessibleOutlets() {
	const currentUser = get(user);
	if (!currentUser?.token) {
		throw new Error('No authentication token');
	}
	
	try {
		// Import authFetch dynamically to avoid circular dependency
		const { authFetch } = await import('$lib/api/auth');
		const data = await authFetch('/api/outlets/accessible/');
		
		// Update accessible outlets
		if (data.outlets) {
			accessibleOutlets.set(data.outlets);
		}
		
		return data;
	} catch (error) {
		console.error('Failed to fetch accessible outlets:', error);
		throw error;
	}
}
