<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Swal from 'sweetalert2';
	import { isAuthenticated } from '$lib/stores/auth';
	import ProductForm from '$lib/components/ProductForm.svelte';
	import { createProduct } from '$lib/api/products';

	let submitting = false;
	let error = null;

	onMount(() => {
		if (!$isAuthenticated) {
			goto('/login');
		}
	});

	async function handleSubmit(event) {
		const formData = event.detail;
		submitting = true;
		error = null;

		try {
			console.log('Creating product with data:', formData);
			const product = await createProduct(formData);
			console.log('Product created:', product);
			
			// Show success message
			await Swal.fire('Success', 'Product created successfully', 'success');
			
			// Redirect to product list
			goto('/products');
		} catch (err) {
			console.error('Error creating product:', err);
			error = err.message || 'Failed to create product';
		} finally {
			submitting = false;
		}
	}

	function handleCancel() {
		goto('/products');
	}
</script>

<div class="container mx-auto px-4 py-8">
	<div class="mb-6">
		<h1 class="text-3xl font-bold text-gray-900">Create New Product</h1>
		<p class="text-gray-600 mt-2">Add a new product to your menu</p>
	</div>

	{#if error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
			<div class="flex">
				<div class="flex-shrink-0">
					<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
					</svg>
				</div>
				<div class="ml-3">
					<h3 class="text-sm font-medium text-red-800">Error creating product</h3>
					<p class="text-sm text-red-700 mt-1">{error}</p>
				</div>
			</div>
		</div>
	{/if}

	<div class="bg-white rounded-lg shadow">
		<ProductForm 
			on:submit={handleSubmit}
			on:cancel={handleCancel}
			{submitting}
		/>
	</div>
</div>
