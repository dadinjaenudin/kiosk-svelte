import { user, isLoading, authError } from '../stores/auth';
import { goto } from '$app/navigation';

const API_BASE = '/api';

/**
 * Login user with username and password
 */
export async function login(username, password) {
	isLoading.set(true);
	authError.set(null);

	try {
		const response = await fetch(`${API_BASE}/auth/login/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password }),
			credentials: 'include'
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.message || 'Login failed');
		}

		const data = await response.json();

		// Store user data
		user.set({
			id: data.user.id,
			username: data.user.username,
			email: data.user.email,
			role: data.user.role,
			tenant_id: data.user.tenant_id,
			tenant_name: data.user.tenant?.name,
			outlet_id: data.user.outlet_id,
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
export async function logout() {
	isLoading.set(true);

	try {
		await fetch(`${API_BASE}/auth/logout/`, {
			method: 'POST',
			credentials: 'include'
		});
	} catch (error) {
		console.error('Logout error:', error);
	} finally {
		user.set(null);
		isLoading.set(false);
		goto('/login');
	}
}

/**
 * Refresh user session
 */
export async function refreshSession() {
	try {
		const response = await fetch(`${API_BASE}/auth/me/`, {
			credentials: 'include'
		});

		if (!response.ok) {
			throw new Error('Session expired');
		}

		const data = await response.json();

		user.set({
			id: data.id,
			username: data.username,
			email: data.email,
			role: data.role,
			tenant_id: data.tenant_id,
			tenant_name: data.tenant?.name,
			outlet_id: data.outlet_id
		});

		return data;
	} catch (error) {
		user.set(null);
		throw error;
	}
}

/**
 * Check if user is authenticated
 */
export async function checkAuth() {
	try {
		await refreshSession();
		return true;
	} catch (error) {
		return false;
	}
}
