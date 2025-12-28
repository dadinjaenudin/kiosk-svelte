/**
 * Promotion API
 */
import { authFetch } from './auth';

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
	return await authFetch(url);
}

/**
 * Get single promotion by ID
 */
export async function getPromotion(id) {
	return await authFetch(`${API_BASE}/promotions/${id}/`);
}

/**
 * Create new promotion
 */
export async function createPromotion(data) {
	console.log('📝 Creating promotion:', data);
	
	const result = await authFetch(`${API_BASE}/promotions/`, {
		method: 'POST',
		body: JSON.stringify(data)
	});
	
	console.log('✅ Promotion created:', result);
	return result;
}

/**
 * Update promotion
 */
export async function updatePromotion(id, data) {
	console.log('📝 Updating promotion:', id, data);
	
	const result = await authFetch(`${API_BASE}/promotions/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
	
	console.log('✅ Promotion updated:', result);
	return result;
}

/**
 * Delete promotion
 */
export async function deletePromotion(id) {
	await authFetch(`${API_BASE}/promotions/${id}/`, {
		method: 'DELETE'
	});
	
	return true;
}

/**
 * Activate promotion
 */
export async function activatePromotion(id) {
	return await authFetch(`${API_BASE}/promotions/${id}/activate/`, {
		method: 'POST'
	});
}

/**
 * Deactivate promotion
 */
export async function deactivatePromotion(id) {
	return await authFetch(`${API_BASE}/promotions/${id}/deactivate/`, {
		method: 'POST'
	});
}

/**
 * Get promotion preview (affected products and prices)
 */
export async function getPromotionPreview(id) {
	return await authFetch(`${API_BASE}/promotions/${id}/preview/`);
}

/**
 * Get active promotions
 */
export async function getActivePromotions() {
	return await authFetch(`${API_BASE}/promotions/active/`);
}

/**
 * Get promotion statistics
 */
export async function getPromotionStats() {
	return await authFetch(`${API_BASE}/promotions/stats/`);
}

/**
 * Get products for selector (searchable, filterable)
 * Fixed: Use correct endpoint /api/products/
 */
export async function getProductsForSelector(filters = {}) {
	const params = new URLSearchParams();
	
	if (filters.search) params.append('search', filters.search);
	if (filters.tenant) params.append('tenant', filters.tenant);
	if (filters.is_available !== undefined) params.append('is_available', filters.is_available);
	
	// Fixed: Changed from /product-selector/ to /products/
	const url = `${API_BASE}/products/${params.toString() ? '?' + params.toString() : ''}`;
	return await authFetch(url);
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
	return await authFetch(url);
}
