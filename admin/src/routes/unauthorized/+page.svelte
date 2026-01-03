<script>
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores/auth';
	
	function goBack() {
		goto('/dashboard');
	}
	
	function goToLogin() {
		goto('/login');
	}
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
	<div class="max-w-md w-full text-center">
		<!-- Icon -->
		<div class="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-red-100">
			<svg
				class="h-12 w-12 text-red-600"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
				/>
			</svg>
		</div>
		
		<!-- Content -->
		<h1 class="mt-6 text-3xl font-bold text-gray-900">
			Access Denied
		</h1>
		
		<p class="mt-4 text-gray-600">
			You don't have permission to access this page. Please contact your administrator if you believe this is an error.
		</p>
		
		{#if $user}
			<div class="mt-6 p-4 bg-gray-100 rounded-lg">
				<p class="text-sm text-gray-600">
					<span class="font-semibold">Current User:</span> {$user.username}
				</p>
				<p class="text-sm text-gray-600 mt-1">
					<span class="font-semibold">Role:</span> 
					<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
						{$user.role}
					</span>
				</p>
				{#if $user.tenant}
					<p class="text-sm text-gray-600 mt-1">
						<span class="font-semibold">Tenant:</span> {$user.tenant.name}
					</p>
				{/if}
			</div>
		{/if}
		
		<!-- Actions -->
		<div class="mt-8 space-y-3">
			{#if $user}
				<button
					on:click={goBack}
					class="w-full inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
				>
					<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
					</svg>
					Back to Dashboard
				</button>
			{:else}
				<button
					on:click={goToLogin}
					class="w-full inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
				>
					Go to Login
				</button>
			{/if}
			
			<button
				on:click={() => window.history.back()}
				class="w-full inline-flex justify-center items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
			>
				Go Back
			</button>
		</div>
		
		<!-- Help Text -->
		<div class="mt-8 text-sm text-gray-500">
			<p>Need help? Contact your system administrator.</p>
		</div>
	</div>
</div>
