<script>
	/**
	 * Example: Product List Page with Role-Based UI
	 * 
	 * This shows how to use RoleGuard and PermissionButton in page components.
	 */
	
	import { goto } from '$app/navigation';
	import RoleGuard from '$lib/components/RoleGuard.svelte';
	import PermissionButton from '$lib/components/PermissionButton.svelte';
	import { canCreate, canDelete } from '$lib/stores/auth';
	
	export let data;
	
	$: ({ products, pagination, user } = data);
	
	function handleCreate() {
		goto('/products/create');
	}
	
	function handleEdit(id) {
		goto(`/products/${id}/edit`);
	}
	
	async function handleDelete(id) {
		if (!confirm('Are you sure you want to delete this product?')) {
			return;
		}
		
		// Delete logic here
		console.log('Deleting product:', id);
	}
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex justify-between items-center">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Products</h1>
			<p class="text-gray-600 mt-1">Manage your product catalog</p>
		</div>
		
		<!-- Create button - only visible to manager and above -->
		<PermissionButton
			action="create"
			resource="products"
			variant="primary"
			on:click={handleCreate}
		>
			<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			Add Product
		</PermissionButton>
	</div>
	
	<!-- Filters -->
	<div class="bg-white rounded-lg shadow p-4">
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<input
				type="search"
				placeholder="Search products..."
				class="input-field"
			/>
			
			<select class="input-field">
				<option value="">All Categories</option>
			</select>
			
			<select class="input-field">
				<option value="">All Status</option>
				<option value="active">Active</option>
				<option value="inactive">Inactive</option>
			</select>
		</div>
	</div>
	
	<!-- Products Table -->
	<div class="bg-white rounded-lg shadow overflow-hidden">
		<table class="min-w-full divide-y divide-gray-200">
			<thead class="bg-gray-50">
				<tr>
					<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
					<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
					<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
					<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stock</th>
					<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
					<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
				</tr>
			</thead>
			<tbody class="bg-white divide-y divide-gray-200">
				{#each products as product (product.id)}
					<tr class="hover:bg-gray-50">
						<td class="px-6 py-4">
							<div class="flex items-center">
								<img
									src={product.image || '/placeholder.png'}
									alt={product.name}
									class="w-10 h-10 rounded-lg object-cover"
								/>
								<div class="ml-4">
									<div class="text-sm font-medium text-gray-900">{product.name}</div>
									<div class="text-sm text-gray-500">{product.sku || 'N/A'}</div>
								</div>
							</div>
						</td>
						<td class="px-6 py-4 text-sm text-gray-900">
							{product.category_name || '-'}
						</td>
						<td class="px-6 py-4 text-sm text-gray-900">
							Rp {product.price?.toLocaleString('id-ID')}
						</td>
						<td class="px-6 py-4 text-sm text-gray-900">
							{product.stock_quantity || 0}
						</td>
						<td class="px-6 py-4">
							<span class="px-2 py-1 text-xs font-semibold rounded-full {
								product.is_available
									? 'bg-green-100 text-green-800'
									: 'bg-red-100 text-red-800'
							}">
								{product.is_available ? 'Available' : 'Unavailable'}
							</span>
						</td>
						<td class="px-6 py-4 text-right text-sm font-medium space-x-2">
							<!-- Edit button - always visible to users who can access products -->
							<button
								on:click={() => handleEdit(product.id)}
								class="text-blue-600 hover:text-blue-900"
							>
								Edit
							</button>
							
							<!-- Delete button - only visible to users with delete permission -->
							<RoleGuard action="delete" resource="products">
								<button
									on:click={() => handleDelete(product.id)}
									class="text-red-600 hover:text-red-900"
								>
									Delete
								</button>
							</RoleGuard>
						</td>
					</tr>
				{:else}
					<tr>
						<td colspan="6" class="px-6 py-12 text-center text-gray-500">
							<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
							</svg>
							<p class="mt-2">No products found</p>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
		
		<!-- Pagination -->
		{#if pagination?.count > 0}
			<div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
				<div class="flex items-center justify-between">
					<div class="text-sm text-gray-700">
						Showing products
					</div>
					<div class="flex space-x-2">
						<button
							disabled={!pagination.previous}
							class="btn btn-secondary btn-sm"
						>
							Previous
						</button>
						<button
							disabled={!pagination.next}
							class="btn btn-secondary btn-sm"
						>
							Next
						</button>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.input-field {
		@apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent;
	}
</style>
