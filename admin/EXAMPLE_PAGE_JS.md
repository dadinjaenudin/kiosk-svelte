/**
 * Example: Route protection in +page.js
 * 
 * This shows how to protect routes and load data with proper permissions.
 */

import { requireRoleLevel, getQueryParams } from '$lib/utils/routeGuard';

export async function load(event) {
	// Protect route: Require manager level or above
	const user = requireRoleLevel(event, 'manager');
	
	// Get query params with tenant filter
	const params = getQueryParams(event, {
		page: event.url.searchParams.get('page') || '1',
		search: event.url.searchParams.get('search') || ''
	});
	
	// Fetch data from API
	try {
		const response = await event.fetch(
			`/api/admin/products/?${params.toString()}`,
			{
				headers: {
					'Authorization': `Bearer ${user.token}`
				}
			}
		);
		
		if (!response.ok) {
			throw new Error('Failed to load products');
		}
		
		const data = await response.json();
		
		return {
			products: data.results || data,
			pagination: {
				count: data.count,
				next: data.next,
				previous: data.previous
			},
			user
		};
	} catch (error) {
		console.error('Error loading products:', error);
		return {
			products: [],
			pagination: null,
			error: error.message
		};
	}
}
