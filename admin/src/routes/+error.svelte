<script>
	import { page } from '$app/stores';
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-100">
	<div class="max-w-md w-full bg-white shadow-lg rounded-lg p-8 text-center">
		<div class="text-6xl mb-4">⚠️</div>
		<h1 class="text-3xl font-bold text-gray-800 mb-2">
			{$page.status || 500}
		</h1>
		<p class="text-gray-600 mb-6">
			{$page.error?.message || 'Something went wrong'}
		</p>
		<a
			href="/dashboard"
			class="inline-block bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary-dark transition-colors"
		>
			Go to Dashboard
		</a>
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
	}
</style>
