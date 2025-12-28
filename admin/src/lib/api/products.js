/**
 * Products API Client
 * 
 * Admin endpoints for product management with image upload
 */

import { authFetch } from './auth';

const API_BASE = '/api';

/**
 * Get products list with filters
 */
export async function getProducts(filters = {}) {
	const params = new URLSearchParams();
	
	if (filters.search) params.append('search', filters.search);
	if (filters.category) params.append('category', filters.category);
	if (filters.tenant) params.append('tenant', filters.tenant);
	if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
	if (filters.is_available !== undefined) params.append('is_available', filters.is_available);
	if (filters.is_featured !== undefined) params.append('is_featured', filters.is_featured);
	if (filters.is_popular !== undefined) params.append('is_popular', filters.is_popular);
	if (filters.has_promo !== undefined) params.append('has_promo', filters.has_promo);
	if (filters.track_stock !== undefined) params.append('track_stock', filters.track_stock);
	if (filters.ordering) params.append('ordering', filters.ordering);
	if (filters.page) params.append('page', filters.page);
	
	const url = `${API_BASE}/admin/products/${params.toString() ? '?' + params.toString() : ''}`;
	return await authFetch(url);
}

/**
 * Get single product detail
 */
export async function getProduct(id) {
	return await authFetch(`${API_BASE}/admin/products/${id}/`);
}

/**
 * Create new product
 */
export async function createProduct(data) {
	// If data contains image file, use FormData
	if (data.image instanceof File) {
		const formData = new FormData();
		Object.keys(data).forEach(key => {
			if (data[key] !== null && data[key] !== undefined) {
				formData.append(key, data[key]);
			}
		});
		
		return await authFetch(`${API_BASE}/admin/products/`, {
			method: 'POST',
			body: formData,
			// Don't set Content-Type, let browser set it with boundary
			headers: {}
		});
	}
	
	// Otherwise use JSON
	return await authFetch(`${API_BASE}/admin/products/`, {
		method: 'POST',
		body: JSON.stringify(data)
	});
}

/**
 * Update product
 */
export async function updateProduct(id, data) {
	// If data contains image file, use FormData
	if (data.image instanceof File) {
		const formData = new FormData();
		Object.keys(data).forEach(key => {
			if (data[key] !== null && data[key] !== undefined) {
				formData.append(key, data[key]);
			}
		});
		
		return await authFetch(`${API_BASE}/admin/products/${id}/`, {
			method: 'PUT',
			body: formData,
			headers: {}
		});
	}
	
	// Otherwise use JSON
	return await authFetch(`${API_BASE}/admin/products/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

/**
 * Partial update product
 */
export async function patchProduct(id, data) {
	return await authFetch(`${API_BASE}/admin/products/${id}/`, {
		method: 'PATCH',
		body: JSON.stringify(data)
	});
}

/**
 * Delete product
 */
export async function deleteProduct(id) {
	return await authFetch(`${API_BASE}/admin/products/${id}/`, {
		method: 'DELETE'
	});
}

/**
 * Upload product image
 */
export async function uploadProductImage(id, imageFile) {
	const formData = new FormData();
	formData.append('image', imageFile);
	
	return await authFetch(`${API_BASE}/admin/products/${id}/upload_image/`, {
		method: 'POST',
		body: formData,
		headers: {}
	});
}

/**
 * Delete product image
 */
export async function deleteProductImage(id) {
	return await authFetch(`${API_BASE}/admin/products/${id}/delete_image/`, {
		method: 'DELETE'
	});
}

/**
 * Duplicate product
 */
export async function duplicateProduct(id) {
	return await authFetch(`${API_BASE}/admin/products/${id}/duplicate/`, {
		method: 'POST'
	});
}

/**
 * Bulk update products
 */
export async function bulkUpdateProducts(productIds, updates) {
	return await authFetch(`${API_BASE}/admin/products/bulk_update/`, {
		method: 'POST',
		body: JSON.stringify({
			product_ids: productIds,
			updates
		})
	});
}

/**
 * Get product statistics
 */
export async function getProductStats() {
	return await authFetch(`${API_BASE}/admin/products/stats/`);
}

// ===== CATEGORIES =====

/**
 * Get categories list
 */
export async function getCategories(filters = {}) {
	const params = new URLSearchParams();
	
	if (filters.search) params.append('search', filters.search);
	if (filters.tenant) params.append('tenant', filters.tenant);
	if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
	if (filters.ordering) params.append('ordering', filters.ordering);
	
	const url = `${API_BASE}/admin/categories/${params.toString() ? '?' + params.toString() : ''}`;
	return await authFetch(url);
}

/**
 * Get single category
 */
export async function getCategory(id) {
	return await authFetch(`${API_BASE}/admin/categories/${id}/`);
}

/**
 * Create category
 */
export async function createCategory(data) {
	if (data.image instanceof File) {
		const formData = new FormData();
		Object.keys(data).forEach(key => {
			if (data[key] !== null && data[key] !== undefined) {
				formData.append(key, data[key]);
			}
		});
		
		return await authFetch(`${API_BASE}/admin/categories/`, {
			method: 'POST',
			body: formData,
			headers: {}
		});
	}
	
	return await authFetch(`${API_BASE}/admin/categories/`, {
		method: 'POST',
		body: JSON.stringify(data)
	});
}

/**
 * Update category
 */
export async function updateCategory(id, data) {
	if (data.image instanceof File) {
		const formData = new FormData();
		Object.keys(data).forEach(key => {
			if (data[key] !== null && data[key] !== undefined) {
				formData.append(key, data[key]);
			}
		});
		
		return await authFetch(`${API_BASE}/admin/categories/${id}/`, {
			method: 'PUT',
			body: formData,
			headers: {}
		});
	}
	
	return await authFetch(`${API_BASE}/admin/categories/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

/**
 * Delete category
 */
export async function deleteCategory(id) {
	return await authFetch(`${API_BASE}/admin/categories/${id}/`, {
		method: 'DELETE'
	});
}

/**
 * Get category statistics
 */
export async function getCategoryStats() {
	return await authFetch(`${API_BASE}/admin/categories/stats/`);
}

// ===== HELPERS =====

/**
 * Format currency
 */
export function formatCurrency(amount) {
	return new Intl.NumberFormat('id-ID', {
		style: 'currency',
		currency: 'IDR',
		minimumFractionDigits: 0
	}).format(amount);
}

/**
 * Format date
 */
export function formatDate(dateString) {
	if (!dateString) return '-';
	const date = new Date(dateString);
	return new Intl.DateTimeFormat('id-ID', {
		day: '2-digit',
		month: 'short',
		year: 'numeric'
	}).format(date);
}
