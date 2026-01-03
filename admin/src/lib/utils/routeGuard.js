/**
 * Route Protection Utilities
 * 
 * Helper functions for protecting routes based on roles and permissions.
 * Use in +page.js or +layout.js load functions.
 */

import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';
import { user } from '$lib/stores/auth';
import { hasRole, hasRoleLevel, canPerform } from '$lib/stores/auth';

/**
 * Require authentication
 * Redirects to /login if not authenticated
 * 
 * @param {object} event - SvelteKit load event
 */
export function requireAuth(event) {
	const currentUser = get(user);
	
	if (!currentUser) {
		throw redirect(302, `/login?redirect=${event.url.pathname}`);
	}
	
	return currentUser;
}

/**
 * Require specific role(s)
 * Redirects to /unauthorized if user doesn't have required role
 * 
 * @param {object} event - SvelteKit load event
 * @param {...string} roles - Required roles
 */
export function requireRole(event, ...roles) {
	const currentUser = requireAuth(event);
	
	if (!hasRole(...roles)) {
		console.warn(`Access denied: User ${currentUser.username} tried to access ${event.url.pathname} but doesn't have required role`);
		throw redirect(302, '/unauthorized');
	}
	
	return currentUser;
}

/**
 * Require minimum role level
 * Redirects to /unauthorized if user doesn't meet role requirement
 * 
 * @param {object} event - SvelteKit load event
 * @param {string} minRole - Minimum required role
 */
export function requireRoleLevel(event, minRole) {
	const currentUser = requireAuth(event);
	
	if (!hasRoleLevel(minRole)) {
		console.warn(`Access denied: User ${currentUser.username} tried to access ${event.url.pathname} but doesn't have required role level`);
		throw redirect(302, '/unauthorized');
	}
	
	return currentUser;
}

/**
 * Require permission for action on resource
 * Redirects to /unauthorized if user doesn't have permission
 * 
 * @param {object} event - SvelteKit load event
 * @param {string} action - Action name
 * @param {string} resource - Resource name
 */
export function requirePermission(event, action, resource) {
	const currentUser = requireAuth(event);
	
	if (!canPerform(action, resource)) {
		console.warn(`Access denied: User ${currentUser.username} tried to ${action} ${resource} but doesn't have permission`);
		throw redirect(302, '/unauthorized');
	}
	
	return currentUser;
}

/**
 * Check if user is admin (for conditional logic, doesn't redirect)
 * 
 * @returns {boolean} True if user is admin
 */
export function isAdminUser() {
	const currentUser = get(user);
	if (!currentUser) return false;
	
	return (
		currentUser.is_superuser ||
		currentUser.role === 'admin' ||
		currentUser.role === 'super_admin'
	);
}

/**
 * Get query params with tenant filter (for admin users)
 * 
 * @param {object} event - SvelteKit load event
 * @param {object} params - Additional query params
 * @returns {URLSearchParams} Query params with tenant filter if applicable
 */
export function getQueryParams(event, params = {}) {
	const searchParams = new URLSearchParams();
	
	// Add existing params
	for (const [key, value] of Object.entries(params)) {
		searchParams.set(key, value);
	}
	
	// Add tenant filter from URL if present (admin feature)
	const tenantId = event.url.searchParams.get('tenant');
	if (tenantId && isAdminUser()) {
		searchParams.set('tenant', tenantId);
	}
	
	return searchParams;
}
