/**
 * Promotion API
 */

const API_BASE = '/api';

/**
 * Get all promotions with filters
 * @param {Object} filters - { status, promo_type, search, date_from, date_to, page }
 */
export async function getPromotions(filters = {}) {
	const params = new URLSearchParams();
	
	if (filters.status) params.append('status', filters.status);
	if (filters.promo_type) params.append('promo_type', filters.promo_type);
	if (filters.search) params.append('search', filters.search);
	if (filters.date_from) params.append('date_from', filters.date_from);
	if (filters.date_to) params.append('date_to', filters.date_to);
	if (filters.page) params.append('page', filters.page);
	if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
	if (filters.is_featured !== undefined) params.append('is_featured', filters.is_featured);
	
	const url = `${API_BASE}/promotions/${params.toString() ? '?' + params.toString() : ''}`;
	
	const response = await fetch(url, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.message || 'Failed to fetch promotions');
	}
	
	return response.json();
}

/**
 * Get single promotion by ID
 */
export async function getPromotion(id) {
	const response = await fetch(`${API_BASE}/promotions/${id}/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.message || 'Failed to fetch promotion');
	}
	
	return response.json();
}

/**
 * Create new promotion
 */
export async function createPromotion(data) {
	console.log('📝 Creating promotion:', data);
	
	const response = await fetch(`${API_BASE}/promotions/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include',
		body: JSON.stringify(data)
	});
	
	console.log('📡 Create response status:', response.status);
	
	if (!response.ok) {
		const error = await response.json();
		console.error('❌ Create error:', error);
		throw new Error(error.message || 'Failed to create promotion');
	}
	
	const result = await response.json();
	console.log('✅ Promotion created:', result);
	return result;
}

/**
 * Update promotion
 */
export async function updatePromotion(id, data) {
	console.log('📝 Updating promotion:', id, data);
	
	const response = await fetch(`${API_BASE}/promotions/${id}/`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include',
		body: JSON.stringify(data)
	});
	
	console.log('📡 Update response status:', response.status);
	
	if (!response.ok) {
		const error = await response.json();
		console.error('❌ Update error:', error);
		throw new Error(error.message || 'Failed to update promotion');
	}
	
	const result = await response.json();
	console.log('✅ Promotion updated:', result);
	return result;
}

/**
 * Delete promotion
 */
export async function deletePromotion(id) {
	const response = await fetch(`${API_BASE}/promotions/${id}/`, {
		method: 'DELETE',
		headers: {
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok && response.status !== 204) {
		const error = await response.json();
		throw new Error(error.message || 'Failed to delete promotion');
	}
	
	return true;
}

/**
 * Activate promotion
 */
export async function activatePromotion(id) {
	const response = await fetch(`${API_BASE}/promotions/${id}/activate/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.error || 'Failed to activate promotion');
	}
	
	return response.json();
}

/**
 * Deactivate promotion
 */
export async function deactivatePromotion(id) {
	const response = await fetch(`${API_BASE}/promotions/${id}/deactivate/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.error || 'Failed to deactivate promotion');
	}
	
	return response.json();
}

/**
 * Get promotion preview (affected products and prices)
 */
export async function getPromotionPreview(id) {
	const response = await fetch(`${API_BASE}/promotions/${id}/preview/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.message || 'Failed to get promotion preview');
	}
	
	return response.json();
}

/**
 * Get active promotions
 */
export async function getActivePromotions() {
	const response = await fetch(`${API_BASE}/promotions/active/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.message || 'Failed to fetch active promotions');
	}
	
	return response.json();
}

/**
 * Get promotion statistics
 */
export async function getPromotionStats() {
	const response = await fetch(`${API_BASE}/promotions/stats/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.message || 'Failed to fetch promotion stats');
	}
	
	return response.json();
}

/**
 * Get products for selector (searchable, filterable)
 */
export async function getProductsForSelector(filters = {}) {
	const params = new URLSearchParams();
	
	if (filters.search) params.append('search', filters.search);
	if (filters.tenant) params.append('tenant', filters.tenant);
	if (filters.is_available !== undefined) params.append('is_available', filters.is_available);
	
	const url = `${API_BASE}/product-selector/${params.toString() ? '?' + params.toString() : ''}`;
	
	const response = await fetch(url, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.message || 'Failed to fetch products');
	}
	
	return response.json();
}

/**
 * Get promotion usage history
 */
export async function getPromotionUsage(filters = {}) {
	const params = new URLSearchParams();
	
	if (filters.promotion) params.append('promotion', filters.promotion);
	if (filters.customer_identifier) params.append('customer_identifier', filters.customer_identifier);
	if (filters.page) params.append('page', filters.page);
	
	const url = `${API_BASE}/promotion-usage/${params.toString() ? '?' + params.toString() : ''}`;
	
	const response = await fetch(url, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Token ${localStorage.getItem('token')}`
		},
		credentials: 'include'
	});
	
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.message || 'Failed to fetch promotion usage');
	}
	
	return response.json();
}
