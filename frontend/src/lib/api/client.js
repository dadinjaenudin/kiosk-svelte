/**
 * API Client for Backend Communication
 * Enhanced with Multi-Tenant Support
 */

// Get API URL - use environment variable or construct from window location
const getAPIBaseURL = () => {
	if (typeof window === 'undefined') {
		// Server-side: use localhost
		return 'http://localhost:8001/api';
	}
	
	// Check environment variable first
	if (import.meta.env.PUBLIC_API_URL) {
		console.log('Using API URL from env:', import.meta.env.PUBLIC_API_URL);
		return import.meta.env.PUBLIC_API_URL;
	}
	
	// Construct API URL based on current host
	// If accessing from 172.17.46.56:5174, backend should be at 172.17.46.56:8001
	const protocol = window.location.protocol;
	const hostname = window.location.hostname;
	const apiUrl = `${protocol}//${hostname}:8001/api`;
	console.log('Constructed API URL from hostname:', apiUrl);
	return apiUrl;
};

const API_BASE_URL = getAPIBaseURL();
console.log('Final API_BASE_URL:', API_BASE_URL);

class APIClient {
	constructor(baseURL = API_BASE_URL) {
		this.baseURL = baseURL;
		console.log('APIClient initialized with baseURL:', this.baseURL);
		this.accessToken = null;
		this.refreshToken = null;
		this.tenantId = null;
		this.outletId = null;
		
		if (typeof window !== 'undefined') {
			this.accessToken = localStorage.getItem('access_token');
			this.refreshToken = localStorage.getItem('refresh_token');
			this.tenantId = localStorage.getItem('tenant_id');
			this.outletId = localStorage.getItem('outlet_id');
		}
	}
	
	/**
	 * Set authentication tokens
	 */
	setTokens(accessToken, refreshToken) {
		this.accessToken = accessToken;
		this.refreshToken = refreshToken;
		
		if (typeof window !== 'undefined') {
			localStorage.setItem('access_token', accessToken);
			localStorage.setItem('refresh_token', refreshToken);
		}
	}
	
	/**
	 * Set tenant context
	 */
	setTenantContext(tenantId, outletId = null) {
		this.tenantId = tenantId;
		this.outletId = outletId;
		
		if (typeof window !== 'undefined') {
			if (tenantId) {
				localStorage.setItem('tenant_id', tenantId);
			} else {
				localStorage.removeItem('tenant_id');
			}
			
			if (outletId) {
				localStorage.setItem('outlet_id', outletId);
			} else {
				localStorage.removeItem('outlet_id');
			}
		}
	}
	
	/**
	 * Clear authentication tokens
	 */
	clearTokens() {
		this.accessToken = null;
		this.refreshToken = null;
		this.tenantId = null;
		this.outletId = null;
		
		if (typeof window !== 'undefined') {
			localStorage.removeItem('access_token');
			localStorage.removeItem('refresh_token');
			localStorage.removeItem('tenant_id');
			localStorage.removeItem('outlet_id');
		}
	}
	
	/**
	 * Get authorization headers (including tenant context and source tracking)
	 */
	getAuthHeaders() {
		const headers = {
			'Content-Type': 'application/json'
		};
		
		if (this.accessToken) {
			headers['Authorization'] = `Bearer ${this.accessToken}`;
		}
		
		// Add tenant context headers
		if (this.tenantId) {
			headers['X-Tenant-ID'] = String(this.tenantId);
		}
		
		if (this.outletId) {
			headers['X-Outlet-ID'] = String(this.outletId);
		}
		
		// Add source tracking headers
		if (typeof window !== 'undefined') {
			// Detect source from URL path
			const path = window.location.pathname;
			let source = 'web'; // default
			
			if (path.includes('/kiosk')) {
				source = 'kiosk';
			} else if (path.includes('/cashier') || path.includes('/admin')) {
				source = 'cashier';
			}
			
			headers['X-Source'] = source;
			
			// Add device ID (from localStorage or generate)
			let deviceId = localStorage.getItem('device_id');
			if (!deviceId) {
				// Generate device ID once
				deviceId = `${source}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
				localStorage.setItem('device_id', deviceId);
			}
			headers['X-Device-ID'] = deviceId;
		}
		
		return headers;
	}
	
	/**
	 * Make API request
	 */
	async request(endpoint, options = {}) {
		const url = `${this.baseURL}${endpoint}`;
		const config = {
			...options,
			headers: {
				...this.getAuthHeaders(),
				...(options.headers || {})
			}
		};
		
		try {
			const response = await fetch(url, config);
			
			// Handle 401 Unauthorized - try to refresh token
			if (response.status === 401 && this.refreshToken) {
				const refreshed = await this.refreshAccessToken();
				if (refreshed) {
					// Retry original request with new token
					config.headers['Authorization'] = `Bearer ${this.accessToken}`;
					const retryResponse = await fetch(url, config);
					return await this.handleResponse(retryResponse);
				}
			}
			
			return await this.handleResponse(response);
		} catch (error) {
			console.error('API request failed:', error);
			throw error;
		}
	}
	
	/**
	 * Handle API response
	 */
	async handleResponse(response) {
		const contentType = response.headers.get('content-type');
		const isJSON = contentType && contentType.includes('application/json');
		
		const data = isJSON ? await response.json() : await response.text();
		
		if (!response.ok) {
			throw new Error(data.error?.message || data.detail || `HTTP ${response.status}`);
		}
		
		return data;
	}
	
	/**
	 * Refresh access token
	 */
	async refreshAccessToken() {
		try {
			const response = await fetch(`${this.baseURL}/auth/refresh/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ refresh: this.refreshToken })
			});
			
			if (response.ok) {
				const data = await response.json();
				this.setTokens(data.access, data.refresh || this.refreshToken);
				return true;
			} else {
				this.clearTokens();
				return false;
			}
		} catch (error) {
			console.error('Token refresh failed:', error);
			this.clearTokens();
			return false;
		}
	}
	
	/**
	 * GET request
	 */
	async get(endpoint, params = {}) {
		const queryString = new URLSearchParams(params).toString();
		const url = queryString ? `${endpoint}?${queryString}` : endpoint;
		return await this.request(url, { method: 'GET' });
	}
	
	/**
	 * POST request
	 */
	async post(endpoint, data) {
		return await this.request(endpoint, {
			method: 'POST',
			body: JSON.stringify(data)
		});
	}
	
	/**
	 * PATCH request
	 */
	async patch(endpoint, data) {
		return await this.request(endpoint, {
			method: 'PATCH',
			body: JSON.stringify(data)
		});
	}
	
	/**
	 * DELETE request
	 */
	async delete(endpoint) {
		return await this.request(endpoint, { method: 'DELETE' });
	}
	
	/**
	 * Login
	 */
	async login(username, password) {
		const data = await this.post('/auth/login/', { username, password });
		this.setTokens(data.access, data.refresh);
		return data;
	}
	
	/**
	 * Logout
	 */
	logout() {
		this.clearTokens();
	}
}

// Export singleton instance
export const api = new APIClient();
export default api;
