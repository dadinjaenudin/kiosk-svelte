/**
 * API Client for Users Management
 */
import { authFetch } from './auth';

const BASE_URL = '/api/admin/users';

/**
 * Get all users with filters
 */
export async function getUsers(filters = {}) {
	const params = new URLSearchParams();
	
	if (filters.role) params.append('role', filters.role);
	if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
	if (filters.tenant) params.append('tenant', filters.tenant);
	if (filters.outlet) params.append('outlet', filters.outlet);
	if (filters.search) params.append('search', filters.search);
	if (filters.ordering) params.append('ordering', filters.ordering);
	if (filters.page) params.append('page', filters.page);
	if (filters.page_size) params.append('page_size', filters.page_size);
	
	const url = params.toString() ? `${BASE_URL}/?${params}` : `${BASE_URL}/`;
	return authFetch(url);
}

/**
 * Get user by ID
 */
export async function getUser(id) {
	return authFetch(`${BASE_URL}/${id}/`);
}

/**
 * Create new user
 */
export async function createUser(userData) {
	return authFetch(`${BASE_URL}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(userData)
	});
}

/**
 * Update user
 */
export async function updateUser(id, userData) {
	return authFetch(`${BASE_URL}/${id}/`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(userData)
	});
}

/**
 * Partial update user
 */
export async function patchUser(id, updates) {
	return authFetch(`${BASE_URL}/${id}/`, {
		method: 'PATCH',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(updates)
	});
}

/**
 * Delete user
 */
export async function deleteUser(id) {
	return authFetch(`${BASE_URL}/${id}/`, {
		method: 'DELETE'
	});
}

/**
 * Reset user password
 */
export async function resetUserPassword(id, newPassword) {
	return authFetch(`${BASE_URL}/${id}/reset_password/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ new_password: newPassword })
	});
}

/**
 * Change user role
 */
export async function changeUserRole(id, newRole) {
	return authFetch(`${BASE_URL}/${id}/change_role/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ role: newRole })
	});
}

/**
 * Get user statistics
 */
export async function getUserStats() {
	return authFetch(`${BASE_URL}/stats/`);
}

/**
 * Bulk update users
 */
export async function bulkUpdateUsers(userIds, updates) {
	return authFetch(`${BASE_URL}/bulk_update/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			user_ids: userIds,
			updates
		})
	});
}

/**
 * Get role options
 */
export function getRoleOptions() {
	return [
		{ value: 'super_admin', label: 'Super Admin', color: 'indigo' },
		{ value: 'admin', label: 'Admin', color: 'red' },
		{ value: 'tenant_owner', label: 'Tenant Owner', color: 'purple' },
		{ value: 'manager', label: 'Manager', color: 'orange' },
		{ value: 'cashier', label: 'Cashier', color: 'blue' },
		{ value: 'kitchen', label: 'Kitchen Staff', color: 'green' }
	];
}

/**
 * Format role label with color
 */
export function formatRole(role) {
	const roles = {
		super_admin: { label: 'Super Admin', color: 'indigo', bgColor: 'bg-indigo-100', textColor: 'text-indigo-800' },
		admin: { label: 'Admin', color: 'red', bgColor: 'bg-red-100', textColor: 'text-red-800' },
		tenant_owner: { label: 'Tenant Owner', color: 'purple', bgColor: 'bg-purple-100', textColor: 'text-purple-800' },
		manager: { label: 'Manager', color: 'orange', bgColor: 'bg-orange-100', textColor: 'text-orange-800' },
		cashier: { label: 'Cashier', color: 'blue', bgColor: 'bg-blue-100', textColor: 'text-blue-800' },
		kitchen: { label: 'Kitchen Staff', color: 'green', bgColor: 'bg-green-100', textColor: 'text-green-800' }
	};
	return roles[role] || { label: role, color: 'gray', bgColor: 'bg-gray-100', textColor: 'text-gray-800' };
}

/**
 * Format date
 */
export function formatDate(dateString) {
	if (!dateString) return '-';
	const date = new Date(dateString);
	return date.toLocaleDateString('id-ID', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
}

/**
 * Format last login
 */
export function formatLastLogin(dateString) {
	if (!dateString) return 'Never';
	return formatDate(dateString);
}
