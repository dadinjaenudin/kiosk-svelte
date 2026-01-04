/**
 * Kitchen Stations API
 */
import { authFetch } from './auth';

/**
 * Get all kitchen stations with optional outlet filter
 * @param {Object} params - Query parameters
 * @returns {Promise} Kitchen stations data
 */
export async function getKitchenStations(params = {}) {
	const queryParams = new URLSearchParams();
	
	if (params.outlet) queryParams.append('outlet', params.outlet);
	if (params.page) queryParams.append('page', params.page);
	if (params.page_size) queryParams.append('page_size', params.page_size);
	
	const url = `/api/kitchen-stations/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
	return await authFetch(url);
}

/**
 * Get a single kitchen station by ID
 * @param {number} id - Kitchen station ID
 * @returns {Promise} Kitchen station data
 */
export async function getKitchenStation(id) {
	return await authFetch(`/api/kitchen-stations/${id}/`);
}

/**
 * Create a new kitchen station
 * @param {Object} data - Kitchen station data
 * @returns {Promise} Created kitchen station
 */
export async function createKitchenStation(data) {
	return await authFetch('/api/kitchen-stations/', {
		method: 'POST',
		body: JSON.stringify(data)
	});
}

/**
 * Update an existing kitchen station
 * @param {number} id - Kitchen station ID
 * @param {Object} data - Updated kitchen station data
 * @returns {Promise} Updated kitchen station
 */
export async function updateKitchenStation(id, data) {
	return await authFetch(`/api/kitchen-stations/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

/**
 * Partially update a kitchen station
 * @param {number} id - Kitchen station ID
 * @param {Object} data - Partial kitchen station data
 * @returns {Promise} Updated kitchen station
 */
export async function patchKitchenStation(id, data) {
	return await authFetch(`/api/kitchen-stations/${id}/`, {
		method: 'PATCH',
		body: JSON.stringify(data)
	});
}

/**
 * Delete a kitchen station (soft delete)
 * @param {number} id - Kitchen station ID
 * @returns {Promise} Deletion result
 */
export async function deleteKitchenStation(id) {
	return await authFetch(`/api/kitchen-stations/${id}/`, {
		method: 'DELETE'
	});
}
