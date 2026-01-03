import { user, isLoading, authError } from '../stores/auth';
import { goto } from '$app/navigation';
import { get } from 'svelte/store';

const API_BASE = '/api';

/**
 * Authenticated fetch wrapper
 * Automatically adds authentication token to requests
 */
export async function authFetch(url, options = {}) {
	const currentUser = get(user);
	
	// Get token from user store
	const token = currentUser?.token;
	
	// Build headers
	const headers = {
		...options.headers
	};
	
	// Don't set Content-Type for FormData - browser will set it with boundary
	// Only set for non-FormData requests
	if (!(options.body instanceof FormData)) {
		headers['Content-Type'] = 'application/json';
	}
	
	// Add token if available
	if (token) {
		headers['Authorization'] = `Token ${token}`;
	}
	
	// Add tenant ID if available (not required for super_admin)
	if (currentUser?.tenant_id) {
		headers['X-Tenant-ID'] = currentUser.tenant_id.toString();
	}
	
	// Make request
	const response = await fetch(url, {
		...options,
		headers,
		credentials: 'include'
	});
	
	// Handle unauthorized
	if (response.status === 401) {
		// Clear user and redirect to login
		user.set(null);
		goto('/login');
		throw new Error('Unauthorized - please login again');
	}
	
	// Handle other errors
	if (!response.ok) {
		const errorText = await response.text();
		let errorMessage = `Request failed with status ${response.status}`;
		
		try {
			const error = JSON.parse(errorText);
			console.error('API Error Response:', JSON.stringify(error, null, 2));
			
			// Try to extract meaningful error message
			if (typeof error === 'string') {
				errorMessage = error;
			} else if (error.message) {
				errorMessage = error.message;
			} else if (error.error) {
				errorMessage = typeof error.error === 'object' ? JSON.stringify(error.error) : error.error;
			} else if (error.detail) {
				errorMessage = typeof error.detail === 'object' ? JSON.stringify(error.detail) : error.detail;
			} else {
				errorMessage = JSON.stringify(error, null, 2);
			}
		} catch (e) {
			console.error('Error parsing error response:', e);
			console.error('Response text:', errorText);
			if (errorText) {
				errorMessage = errorText;
			}
		}
		
		console.error('Final error message:', errorMessage);
		throw new Error(errorMessage);
	}
	
	// Handle 204 No Content (successful DELETE, etc)
	if (response.status === 204) {
		return null;
	}
	
	// Parse and return JSON
	try {
		const data = await response.json();
		return data;
	} catch (e) {
		console.error('Error parsing success response as JSON:', e);
		console.error('Response status:', response.status);
		
		// If response is empty or not JSON, return null for success
		if (response.status >= 200 && response.status < 300) {
			return null;
		}
		
		throw new Error(`Failed to parse response: ${e.message}`);
	}
}

/**
 * Login user with username and password
 */
export async function login(username, password) {
	isLoading.set(true);
	authError.set(null);

	try {
		console.log('🔐 Attempting login:', { username });
		
		const response = await fetch(`${API_BASE}/auth/login/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password }),
			credentials: 'include'
		});

		console.log('📡 Login response status:', response.status);

		if (!response.ok) {
			const errorText = await response.text();
			console.error('❌ Login error response:', errorText);
			
			let errorMessage = 'Login failed';
			try {
				const error = JSON.parse(errorText);
				errorMessage = error.message || error.error || error.detail || errorMessage;
			} catch (e) {
				errorMessage = errorText || errorMessage;
			}
			
			throw new Error(errorMessage);
		}

		const data = await response.json();
		console.log('✅ Login successful:', { username: data.user?.username, role: data.user?.role });

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
		console.error('❌ Login failed:', error.message);
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
		const currentUser = get(user);
		const token = currentUser?.token;
		
		const headers = {
			'Content-Type': 'application/json'
		};
		
		if (token) {
			headers['Authorization'] = `Token ${token}`;
		}
		
		await fetch(`${API_BASE}/auth/logout/`, {
			method: 'POST',
			headers,
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
