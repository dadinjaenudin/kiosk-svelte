<script>
	/**
	 * RoleGuard Component
	 * 
	 * Conditionally renders content based on user role or permissions.
	 * 
	 * Usage:
	 *   <RoleGuard roles={['admin', 'manager']}>
	 *     <button>Admin/Manager Only</button>
	 *   </RoleGuard>
	 * 
	 *   <RoleGuard action="delete" resource="products">
	 *     <button>Delete Product</button>
	 *   </RoleGuard>
	 * 
	 *   <RoleGuard minRole="manager">
	 *     <div>Manager and above</div>
	 *   </RoleGuard>
	 */
	
	import { user } from '$lib/stores/auth';
	import { hasRole, hasRoleLevel, canPerform } from '$lib/stores/auth';
	
	// Props
	export let roles = null;           // Array of specific roles (e.g., ['admin', 'manager'])
	export let minRole = null;         // Minimum role level (e.g., 'manager')
	export let action = null;          // Action to check (e.g., 'create', 'delete')
	export let resource = null;        // Resource to check (e.g., 'products', 'orders')
	export let tenant = null;          // Tenant ID to check access
	export let fallback = null;        // Fallback content when access denied
	export let showFallback = true;    // Show fallback or hide completely
	
	// Reactive check
	$: hasAccess = checkAccess($user);
	
	function checkAccess(currentUser) {
		if (!currentUser) return false;
		
		// Check specific roles
		if (roles && roles.length > 0) {
			return hasRole(...roles);
		}
		
		// Check minimum role level
		if (minRole) {
			return hasRoleLevel(minRole);
		}
		
		// Check action permission
		if (action && resource) {
			return canPerform(action, resource);
		}
		
		// Check tenant access
		if (tenant) {
			return canAccessTenant(tenant);
		}
		
		// Default: authenticated user
		return true;
	}
</script>

{#if hasAccess}
	<slot />
{:else if showFallback && fallback}
	{@html fallback}
{:else if showFallback}
	<slot name="fallback" />
{/if}
