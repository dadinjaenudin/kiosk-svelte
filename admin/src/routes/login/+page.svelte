<script>
	import { goto } from '$app/navigation';
	import { login } from '$lib/api/auth';
	import { authError, isLoading } from '$lib/stores/auth';
	import '../app.css';

	let username = '';
	let password = '';
	let error = '';

	async function handleSubmit() {
		error = '';

		if (!username || !password) {
			error = 'Please fill in all fields';
			return;
		}

		try {
			await login(username, password);
			goto('/dashboard');
		} catch (err) {
			error = err.message;
		}
	}
</script>

<svelte:head>
	<title>Login - Admin Panel</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full">
		<!-- Logo/Brand -->
		<div class="text-center mb-8">
			<h1 class="text-4xl font-bold text-white mb-2">🏪 Food Court Admin</h1>
			<p class="text-primary-100">Management Dashboard</p>
		</div>

		<!-- Login Card -->
		<div class="bg-white rounded-2xl shadow-2xl p-8">
			<div class="mb-6">
				<h2 class="text-2xl font-bold text-gray-900 text-center">Welcome Back</h2>
				<p class="text-gray-600 text-center mt-2">Please sign in to continue</p>
			</div>

			<!-- Error Message -->
			{#if error || $authError}
				<div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
					<p class="text-sm text-red-800">
						{error || $authError}
					</p>
				</div>
			{/if}

			<!-- Login Form -->
			<form on:submit|preventDefault={handleSubmit} class="space-y-6">
				<div>
					<label for="username" class="label">
						Username
					</label>
					<input
						id="username"
						type="text"
						bind:value={username}
						class="input"
						placeholder="Enter your username"
						disabled={$isLoading}
						required
					/>
				</div>

				<div>
					<label for="password" class="label">
						Password
					</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						class="input"
						placeholder="Enter your password"
						disabled={$isLoading}
						required
					/>
				</div>

				<div class="flex items-center justify-between">
					<label class="flex items-center">
						<input type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
						<span class="ml-2 text-sm text-gray-600">Remember me</span>
					</label>

					<a href="/forgot-password" class="text-sm text-primary-600 hover:text-primary-700">
						Forgot password?
					</a>
				</div>

				<button
					type="submit"
					class="w-full btn btn-primary py-3 text-lg"
					disabled={$isLoading}
				>
					{#if $isLoading}
						<span class="flex items-center justify-center">
							<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							Signing in...
						</span>
					{:else}
						Sign In
					{/if}
				</button>
			</form>

			<!-- Demo Credentials -->
			<div class="mt-6 p-4 bg-gray-50 rounded-lg">
				<p class="text-xs text-gray-600 mb-2 font-semibold">Demo Credentials:</p>
				<div class="space-y-1 text-xs text-gray-500">
					<p>Super Admin: <code class="bg-gray-200 px-1 rounded">admin / admin123</code></p>
					<p>Owner: <code class="bg-gray-200 px-1 rounded">warung-nasi-padang / password123</code></p>
					<p>Manager: <code class="bg-gray-200 px-1 rounded">manager / password123</code></p>
				</div>
			</div>
		</div>

		<!-- Footer -->
		<div class="mt-6 text-center text-primary-100 text-sm">
			<p>&copy; 2024 Food Court Kiosk. All rights reserved.</p>
		</div>
	</div>
</div>

<style>
	code {
		font-family: 'Courier New', monospace;
	}
</style>
