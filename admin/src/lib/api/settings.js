/**
 * API Client for Settings Management
 */

import { authFetch } from './auth';

const API_BASE = '/api';

/**
 * Tenant Settings API
 */

/**
 * Get tenant settings
 * @returns {Promise<Object>} Tenant settings
 */
export async function getTenantSettings() {
	const response = await authFetch(`${API_BASE}/admin/settings/tenant/`);
	return response;
}

/**
 * Update tenant settings
 * @param {number} id - Tenant ID
 * @param {Object} data - Tenant data to update
 * @returns {Promise<Object>} Updated tenant
 */
export async function updateTenantSettings(id, data) {
	const response = await authFetch(`${API_BASE}/admin/settings/tenant/${id}/`, {
		method: 'PATCH',
		body: JSON.stringify(data)
	});
	return response;
}

/**
 * Upload tenant logo
 * @param {number} id - Tenant ID
 * @param {File} logoFile - Logo image file
 * @returns {Promise<Object>} Updated tenant with logo
 */
export async function uploadTenantLogo(id, logoFile) {
	const formData = new FormData();
	formData.append('logo', logoFile);

	const response = await authFetch(`${API_BASE}/admin/settings/tenant/${id}/upload_logo/`, {
		method: 'POST',
		body: formData,
		headers: {} // Let browser set Content-Type for multipart/form-data
	});
	return response;
}

/**
 * Delete tenant logo
 * @param {number} id - Tenant ID
 * @returns {Promise<Object>} Response
 */
export async function deleteTenantLogo(id) {
	const response = await authFetch(`${API_BASE}/admin/settings/tenant/${id}/delete_logo/`, {
		method: 'DELETE'
	});
	return response;
}

/**
 * Outlet Management API
 */

/**
 * Get outlets list
 * @param {Object} filters - Filter parameters
 * @returns {Promise<Object>} Paginated outlets list
 */
export async function getOutlets(filters = {}) {
	const params = new URLSearchParams();

	if (filters.search) params.append('search', filters.search);
	if (filters.tenant) params.append('tenant', filters.tenant);
	if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
	if (filters.city) params.append('city', filters.city);
	if (filters.province) params.append('province', filters.province);
	if (filters.ordering) params.append('ordering', filters.ordering);
	if (filters.page) params.append('page', filters.page);
	if (filters.page_size) params.append('page_size', filters.page_size);

	const url = `${API_BASE}/admin/settings/outlets/${params.toString() ? `?${params.toString()}` : ''}`;
	const response = await authFetch(url);
	return response;
}

/**
 * Get outlet statistics
 * @returns {Promise<Object>} Outlet statistics
 */
export async function getOutletStats() {
	const response = await authFetch(`${API_BASE}/admin/settings/outlets/stats/`);
	return response;
}

/**
 * Get outlet by ID
 * @param {number} id - Outlet ID
 * @returns {Promise<Object>} Outlet detail
 */
export async function getOutlet(id) {
	const response = await authFetch(`${API_BASE}/admin/settings/outlets/${id}/`);
	return response;
}

/**
 * Create new outlet
 * @param {Object} outletData - Outlet data
 * @returns {Promise<Object>} Created outlet
 */
export async function createOutlet(outletData) {
	const response = await authFetch(`${API_BASE}/admin/settings/outlets/`, {
		method: 'POST',
		body: JSON.stringify(outletData)
	});
	return response;
}

/**
 * Update outlet
 * @param {number} id - Outlet ID
 * @param {Object} outletData - Outlet data to update
 * @returns {Promise<Object>} Updated outlet
 */
export async function updateOutlet(id, outletData) {
	const response = await authFetch(`${API_BASE}/admin/settings/outlets/${id}/`, {
		method: 'PATCH',
		body: JSON.stringify(outletData)
	});
	return response;
}

/**
 * Delete outlet (soft delete)
 * @param {number} id - Outlet ID
 * @returns {Promise<void>}
 */
export async function deleteOutlet(id) {
	await authFetch(`${API_BASE}/admin/settings/outlets/${id}/`, {
		method: 'DELETE'
	});
}

/**
 * Bulk update outlets
 * @param {number[]} outletIds - Array of outlet IDs
 * @param {Object} updates - Updates to apply
 * @returns {Promise<Object>} Bulk update result
 */
export async function bulkUpdateOutlets(outletIds, updates) {
	const response = await authFetch(`${API_BASE}/admin/settings/outlets/bulk_update/`, {
		method: 'POST',
		body: JSON.stringify({
			outlet_ids: outletIds,
			updates: updates
		})
	});
	return response;
}

/**
 * Utility Functions
 */

/**
 * Format operating hours
 * @param {string} openingTime - Opening time (HH:MM:SS)
 * @param {string} closingTime - Closing time (HH:MM:SS)
 * @returns {string} Formatted operating hours
 */
export function formatOperatingHours(openingTime, closingTime) {
	if (!openingTime || !closingTime) return 'Not set';

	// Convert to 12-hour format
	const formatTime = (timeStr) => {
		const [hours, minutes] = timeStr.split(':');
		const hour = parseInt(hours);
		const ampm = hour >= 12 ? 'PM' : 'AM';
		const displayHour = hour % 12 || 12;
		return `${displayHour}:${minutes} ${ampm}`;
	};

	return `${formatTime(openingTime)} - ${formatTime(closingTime)}`;
}

/**
 * Format address
 * @param {Object} outlet - Outlet object
 * @returns {string} Formatted address
 */
export function formatAddress(outlet) {
	const parts = [
		outlet.address,
		outlet.city,
		outlet.province,
		outlet.postal_code
	].filter(Boolean);

	return parts.join(', ');
}

/**
 * Format date
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export function formatDate(dateString) {
	if (!dateString) return '-';
	return new Date(dateString).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
}

/**
 * Validate color hex code
 * @param {string} color - Color hex code
 * @returns {boolean} True if valid
 */
export function isValidHexColor(color) {
	return /^#[0-9A-F]{6}$/i.test(color);
}

/**
 * Get status badge class
 * @param {boolean} isActive - Active status
 * @returns {Object} Badge label and color class
 */
export function getStatusBadge(isActive) {
	return isActive
		? { label: 'Active', colorClass: 'bg-green-100 text-green-800' }
		: { label: 'Inactive', colorClass: 'bg-red-100 text-red-800' };
}

/**
 * Get cities list from outlets
 * @param {Array} outlets - Array of outlets
 * @returns {Array} Unique cities
 */
export function getCitiesList(outlets) {
	const cities = outlets.map((o) => o.city).filter(Boolean);
	return [...new Set(cities)].sort();
}

/**
 * Get provinces list from outlets
 * @param {Array} outlets - Array of outlets
 * @returns {Array} Unique provinces
 */
export function getProvincesList(outlets) {
	const provinces = outlets.map((o) => o.province).filter(Boolean);
	return [...new Set(provinces)].sort();
}
