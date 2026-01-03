/**
 * Tenants API - CRUD operations for tenant management
 */
import { authFetch } from './auth';

const API_BASE = '/api';

/**
 * Get list of tenants with pagination and filters
 * @param {Object} params - Query parameters (page, page_size, search, is_active, ordering)
 * @returns {Promise<Object>} Paginated tenants list
 */
export async function getTenants(params = {}) {
	const queryParams = new URLSearchParams();
	
	if (params.page) queryParams.append('page', params.page);
	if (params.page_size) queryParams.append('page_size', params.page_size);
	if (params.search) queryParams.append('search', params.search);
	if (params.is_active !== undefined && params.is_active !== '') {
		queryParams.append('is_active', params.is_active);
	}
	if (params.ordering) queryParams.append('ordering', params.ordering);
	
	const url = `${API_BASE}/admin/tenants/?${queryParams.toString()}`;
	const response = await authFetch(url);
	return response;
}

/**
 * Get tenant statistics
 * @returns {Promise<Object>} Tenant stats (total, active, inactive)
 */
export async function getTenantStats() {
	const response = await authFetch(`${API_BASE}/admin/tenants/stats/`);
	return response;
}

/**
 * Get tenant by ID
 * @param {number} id - Tenant ID
 * @returns {Promise<Object>} Tenant detail
 */
export async function getTenant(id) {
	const response = await authFetch(`${API_BASE}/admin/tenants/${id}/`);
	return response;
}

/**
 * Create new tenant
 * @param {Object} tenantData - Tenant data
 * @returns {Promise<Object>} Created tenant
 */
export async function createTenant(tenantData) {
	const response = await authFetch(`${API_BASE}/admin/tenants/`, {
		method: 'POST',
		body: JSON.stringify(tenantData)
	});
	return response;
}

/**
 * Update tenant
 * @param {number} id - Tenant ID
 * @param {Object} tenantData - Tenant data to update
 * @returns {Promise<Object>} Updated tenant
 */
export async function updateTenant(id, tenantData) {
	const response = await authFetch(`${API_BASE}/admin/tenants/${id}/`, {
		method: 'PATCH',
		body: JSON.stringify(tenantData)
	});
	return response;
}

/**
 * Delete tenant
 * @param {number} id - Tenant ID
 * @returns {Promise<void>}
 */
export async function deleteTenant(id) {
	await authFetch(`${API_BASE}/admin/tenants/${id}/`, {
		method: 'DELETE'
	});
}
