import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// User store
export const user = writable(null);

// Loading state
export const isLoading = writable(false);

// Error state
export const authError = writable(null);

// Check if user is authenticated
export const isAuthenticated = derived(user, ($user) => $user !== null);

// Load user from localStorage on init
if (browser) {
	const storedUser = localStorage.getItem('admin_user');
	if (storedUser) {
		try {
			user.set(JSON.parse(storedUser));
		} catch (e) {
			localStorage.removeItem('admin_user');
		}
	}
}

// Subscribe to user changes and persist to localStorage
if (browser) {
	user.subscribe((value) => {
		if (value) {
			localStorage.setItem('admin_user', JSON.stringify(value));
		} else {
			localStorage.removeItem('admin_user');
		}
	});
}

// Helper function to check permissions
export function hasPermission(requiredRole) {
	let currentUser;
	user.subscribe((u) => (currentUser = u))();

	if (!currentUser) return false;

	const roleHierarchy = {
		admin: 5,           // Added admin role
		super_admin: 5,
		tenant_owner: 4,    // Added tenant_owner
		owner: 4,
		outlet_manager: 3,  // Added outlet_manager
		manager: 3,
		cashier: 2,
		kitchen: 1
	};

	const userLevel = roleHierarchy[currentUser.role] || 0;
	const requiredLevel = roleHierarchy[requiredRole] || 0;

	return userLevel >= requiredLevel;
}

// Helper function to check feature permission
export function canAccess(feature) {
	let currentUser;
	user.subscribe((u) => (currentUser = u))();

	if (!currentUser) return false;

	const permissions = {
		admin: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'reports', 'users', 'settings'],
		super_admin: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'reports', 'users', 'settings'],
		tenant_owner: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'reports', 'users', 'settings'],
		owner: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'reports', 'users', 'settings'],
		outlet_manager: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'reports'],
		manager: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'reports'],
		cashier: ['orders'],
		kitchen: ['orders']
	};

	return permissions[currentUser.role]?.includes(feature) || false;
}
