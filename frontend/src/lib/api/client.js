/**
 * API Client for Backend Communication
 */

const API_BASE_URL = typeof window !== 'undefined' 
	? (import.meta.env.PUBLIC_API_URL || 'http://localhost:8000/api')
	: 'http://localhost:8000/api';

class APIClient {
	constructor(baseURL = API_BASE_URL) {
		this.baseURL = baseURL;
		this.accessToken = null;
		this.refreshToken = null;
		
		if (typeof window !== 'undefined') {
			this.accessToken = localStorage.getItem('access_token');
			this.refreshToken = localStorage.getItem('refresh_token');
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
	 * Clear authentication tokens
	 */
	clearTokens() {
		this.accessToken = null;
		this.refreshToken = null;
		
		if (typeof window !== 'undefined') {
			localStorage.removeItem('access_token');
			localStorage.removeItem('refresh_token');
		}
	}
	
	/**
	 * Get authorization headers
	 */
	getAuthHeaders() {
		const headers = {
			'Content-Type': 'application/json'
		};
		
		if (this.accessToken) {
			headers['Authorization'] = `Bearer ${this.accessToken}`;
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
