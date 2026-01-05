<script>
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Swal from 'sweetalert2';
	import { isAuthenticated } from '$lib/stores/auth';
	import ProductForm from '$lib/components/ProductForm.svelte';
	import { getProduct, updateProduct } from '$lib/api/products';

	export let data = {};

	let productId = null;
	let product = null;
	let loading = true;
	let submitting = false;
	let error = null;

	$: productId = $page.params.id;

	onMount(() => {
		if (!$isAuthenticated) {
			goto('/login');
			return;
		}
		loadProduct();
	});

	async function loadProduct() {
		loading = true;
		error = null;

		try {
			console.log('Loading product:', productId);
			product = await getProduct(productId);
			console.log('Product loaded:', product);
		} catch (err) {
			console.error('Error loading product:', err);
			error = err.message || 'Failed to load product';
		} finally {
			loading = false;
		}
	}

	async function handleSubmit(event) {
		const formData = event.detail;
		submitting = true;
		error = null;

		try {
			console.log('Updating product with data:', formData);
			const updated = await updateProduct(productId, formData);
			console.log('Product updated:', updated);
			
			// Show success message
			await Swal.fire('Success', 'Product updated successfully', 'success');
			
			// Redirect to product list
			goto('/products');
		} catch (err) {
			console.error('Error updating product:', err);
			console.error('Error details:', err.message, err);
			error = err.message || err.toString() || 'Failed to update product';
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
		<h1 class="text-3xl font-bold text-gray-900">Edit Product</h1>
		<p class="text-gray-600 mt-2">Update product information</p>
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
					<h3 class="text-sm font-medium text-red-800">Error</h3>
					<p class="text-sm text-red-700 mt-1">{error}</p>
				</div>
			</div>
		</div>
	{/if}

	{#if loading}
		<div class="bg-white rounded-lg shadow p-8">
			<div class="flex items-center justify-center">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
				<span class="ml-3 text-gray-600">Loading product...</span>
			</div>
		</div>
	{:else if product}
		<div class="bg-white rounded-lg shadow">
			<ProductForm 
				{product}
				on:submit={handleSubmit}
				on:cancel={handleCancel}
				{submitting}
			/>
		</div>
	{:else}
		<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
			<p class="text-yellow-800">Product not found</p>
		</div>
	{/if}
</div>
