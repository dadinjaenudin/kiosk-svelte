import { authFetch } from './auth';

const API_BASE = '/api';

export async function getKitchenStationTypes(tenantId = null) {
	const params = new URLSearchParams();
	if (tenantId) {
		params.append('tenant', tenantId);
	}
	
	const url = `${API_BASE}/kitchen-station-types/${params.toString() ? '?' + params.toString() : ''}`;
	return await authFetch(url);
}

export async function createKitchenStationType(data) {
	return await authFetch(`${API_BASE}/kitchen-station-types/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
}

export async function updateKitchenStationType(id, data) {
	return await authFetch(`${API_BASE}/kitchen-station-types/${id}/`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
}

export async function patchKitchenStationType(id, data) {
	return await authFetch(`${API_BASE}/kitchen-station-types/${id}/`, {
		method: 'PATCH',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
}

export async function deleteKitchenStationType(id) {
	return await authFetch(`${API_BASE}/kitchen-station-types/${id}/`, {
		method: 'DELETE'
	});
}
