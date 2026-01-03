// Auth check disabled - handled by +layout.svelte to avoid race condition with localStorage
// Kitchen staff can access orders (to update order status)

export async function load(event) {
	return {};
}
