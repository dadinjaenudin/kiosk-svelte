// Auth check disabled - handled by +layout.svelte to avoid race condition with localStorage
// Protect route: Require cashier level or above

export async function load(event) {
	// Get query params
	const params = {
		page: event.url.searchParams.get('page') || '1',
		search: event.url.searchParams.get('search') || '',
		category: event.url.searchParams.get('category') || '',
		is_available: event.url.searchParams.get('is_available') || ''
	};
	
	return {
		queryParams: params
	};
}
