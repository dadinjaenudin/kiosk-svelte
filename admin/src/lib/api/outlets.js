/**
 * Outlets API
 */
import { authFetch } from './auth';

/**
 * Get all outlets (admin only - for forms)
 */
export async function getAllOutlets() {
	return await authFetch('/api/outlets/all_outlets/');
}

/**
 * Get all outlets
 */
export async function getOutlets(params = {}) {
	const queryParams = new URLSearchParams();
	
	if (params.tenant) queryParams.append('tenant', params.tenant);
	if (params.search) queryParams.append('search', params.search);
	if (params.is_active !== undefined) queryParams.append('is_active', params.is_active);
	if (params.page) queryParams.append('page', params.page);
	if (params.page_size) queryParams.append('page_size', params.page_size);
	
	const url = `/api/outlets/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
	return await authFetch(url);
}

/**
 * Get single outlet
 */
export async function getOutlet(id) {
	return await authFetch(`/api/outlets/${id}/`);
}

/**
 * Create outlet
 */
export async function createOutlet(data) {
	return await authFetch('/api/outlets/', {
		method: 'POST',
		body: JSON.stringify(data)
	});
}

/**
 * Update outlet
 */
export async function updateOutlet(id, data) {
	return await authFetch(`/api/outlets/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

/**
 * Delete outlet
 */
export async function deleteOutlet(id) {
	return await authFetch(`/api/outlets/${id}/`, {
		method: 'DELETE'
	});
}

/**
 * Get outlet stats
 */
export async function getOutletStats() {
	return await authFetch('/api/outlets/stats/');
}
