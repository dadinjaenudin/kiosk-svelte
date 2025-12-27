/**
 * Dashboard API client
 */

const API_BASE = '/api';

/**
 * Fetch dashboard analytics data
 * @param {Object} params - Query parameters
 * @param {string} params.period - Period filter: 'today', 'week', 'month', 'custom'
 * @param {string} params.start_date - Start date for custom period (YYYY-MM-DD)
 * @param {string} params.end_date - End date for custom period (YYYY-MM-DD)
 * @param {number} params.tenant_id - Optional tenant ID filter
 * @returns {Promise<Object>} Dashboard data
 */
export async function getDashboardAnalytics(params = {}) {
	console.log('📊 Fetching dashboard analytics with params:', params);
	
	// Build query string
	const queryParams = new URLSearchParams();
	
	if (params.period) {
		queryParams.append('period', params.period);
	}
	
	if (params.start_date) {
		queryParams.append('start_date', params.start_date);
	}
	
	if (params.end_date) {
		queryParams.append('end_date', params.end_date);
	}
	
	if (params.tenant_id) {
		queryParams.append('tenant_id', params.tenant_id);
	}
	
	const queryString = queryParams.toString();
	const url = `${API_BASE}/orders/dashboard_analytics/${queryString ? '?' + queryString : ''}`;
	
	console.log('📡 Dashboard API URL:', url);
	
	try {
		const response = await fetch(url, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		
		console.log('📡 Dashboard response status:', response.status);
		
		if (!response.ok) {
			const errorText = await response.text();
			console.error('❌ Dashboard API error:', errorText);
			throw new Error(`Failed to fetch dashboard data: ${response.status}`);
		}
		
		const data = await response.json();
		console.log('✅ Dashboard data loaded:', data);
		
		return data;
	} catch (error) {
		console.error('❌ Dashboard fetch error:', error);
		throw error;
	}
}

/**
 * Get real-time order updates
 * This will be used for WebSocket connection later
 */
export async function getRecentOrders(limit = 10) {
	console.log('📦 Fetching recent orders, limit:', limit);
	
	try {
		const response = await fetch(`${API_BASE}/orders/?limit=${limit}`, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		
		console.log('📡 Recent orders response status:', response.status);
		
		if (!response.ok) {
			throw new Error(`Failed to fetch recent orders: ${response.status}`);
		}
		
		const data = await response.json();
		console.log('✅ Recent orders loaded:', data);
		
		return data;
	} catch (error) {
		console.error('❌ Recent orders fetch error:', error);
		throw error;
	}
}
