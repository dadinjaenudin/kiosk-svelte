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
		super_admin: 5,
		owner: 4,
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
		super_admin: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'reports', 'users', 'settings'],
		owner: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'reports', 'users', 'settings'],
		manager: ['dashboard', 'orders', 'customers', 'promotions', 'products', 'reports'],
		cashier: ['orders'],
		kitchen: ['orders']
	};

	return permissions[currentUser.role]?.includes(feature) || false;
}
