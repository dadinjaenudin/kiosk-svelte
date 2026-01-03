// Auth check disabled - handled by +layout.svelte to avoid race condition with localStorage
// Only admin and super_admin can access users management

export async function load(event) {
	return {};
}
