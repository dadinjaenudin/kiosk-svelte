/**
 * API Client for Product Modifiers (Toppings & Additions)
 */
import { authFetch } from './auth';

const BASE_URL = '/api/admin/modifiers';

/**
 * Get all modifiers with filters
 */
export async function getModifiers(filters = {}) {
	const params = new URLSearchParams();
	
	if (filters.type) params.append('type', filters.type);
	if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
	if (filters.product) params.append('product', filters.product);
	if (filters.search) params.append('search', filters.search);
	if (filters.ordering) params.append('ordering', filters.ordering);
	if (filters.page) params.append('page', filters.page);
	
	const url = params.toString() ? `${BASE_URL}/?${params}` : `${BASE_URL}/`;
	return authFetch(url);
}

/**
 * Get modifier by ID
 */
export async function getModifier(id) {
	return authFetch(`${BASE_URL}/${id}/`);
}

/**
 * Get modifiers by product
 */
export async function getModifiersByProduct(productId) {
	return authFetch(`${BASE_URL}/by_product/?product_id=${productId}`);
}

/**
 * Create new modifier
 */
export async function createModifier(modifierData) {
	return authFetch(`${BASE_URL}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(modifierData)
	});
}

/**
 * Update modifier
 */
export async function updateModifier(id, modifierData) {
	return authFetch(`${BASE_URL}/${id}/`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(modifierData)
	});
}

/**
 * Partial update modifier
 */
export async function patchModifier(id, updates) {
	return authFetch(`${BASE_URL}/${id}/`, {
		method: 'PATCH',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(updates)
	});
}

/**
 * Delete modifier
 */
export async function deleteModifier(id) {
	return authFetch(`${BASE_URL}/${id}/`, {
		method: 'DELETE'
	});
}

/**
 * Get modifier statistics
 */
export async function getModifierStats() {
	return authFetch(`${BASE_URL}/stats/`);
}

/**
 * Bulk update modifiers
 */
export async function bulkUpdateModifiers(modifierIds, updates) {
	return authFetch(`${BASE_URL}/bulk_update/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			modifier_ids: modifierIds,
			updates
		})
	});
}

/**
 * Format modifier type label
 */
export function formatModifierType(type) {
	const types = {
		size: { label: 'Size', color: 'blue' },
		topping: { label: 'Topping', color: 'green' },
		spicy: { label: 'Spicy Level', color: 'red' },
		extra: { label: 'Extra', color: 'purple' },
		sauce: { label: 'Sauce', color: 'yellow' }
	};
	return types[type] || { label: type, color: 'gray' };
}

/**
 * Format price adjustment
 */
export function formatPriceAdjustment(amount) {
	const formatter = new Intl.NumberFormat('id-ID', {
		style: 'currency',
		currency: 'IDR',
		minimumFractionDigits: 0,
		maximumFractionDigits: 0
	});
	
	if (amount > 0) {
		return '+' + formatter.format(amount);
	} else if (amount < 0) {
		return formatter.format(amount);
	} else {
		return 'Free';
	}
}

/**
 * Get modifier type options for form
 */
export function getModifierTypeOptions() {
	return [
		{ value: 'size', label: 'Size' },
		{ value: 'topping', label: 'Topping' },
		{ value: 'spicy', label: 'Spicy Level' },
		{ value: 'extra', label: 'Extra' },
		{ value: 'sauce', label: 'Sauce' }
	];
}
