<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import Swal from 'sweetalert2';
	import {
		getUsers,
		deleteUser,
		getUserStats,
		createUser,
		updateUser,
		resetUserPassword,
		changeUserRole,
		bulkUpdateUsers,
		getRoleOptions,
		formatRole,
		formatDate,
		formatLastLogin
	} from '$lib/api/users';
	import { getTenants } from '$lib/api/tenants';
	import { getAllOutlets } from '$lib/api/outlets';

	export let data = {};

	// State
	let users = [];
	let loading = true;
	let stats = { total: 0, active: 0, inactive: 0, by_role: {} };
	
	// Filters
	let searchQuery = '';
	let selectedRole = '';
	let isActiveFilter = '';
	
	// Pagination
	let currentPage = 1;
	let totalPages = 1;
	let totalCount = 0;
	
	// Bulk actions
	let selectedUsers = [];
	let bulkAction = '';
	
	// Modals
	let showDeleteModal = false;
	let userToDelete = null;
	let showCreateModal = false;
	let showPasswordModal = false;
	let showRoleModal = false;
	let editingUser = null;
	
	// Form data
	let formData = {
		username: '',
		email: '',
		first_name: '',
		last_name: '',
		phone_number: '',
		role: 'cashier',
		password: '',
		is_active: true,
		tenant: null,
		outlet: null,
		accessible_outlets: []
	};
	let formErrors = {};
	
	// Password modal
	let newPassword = '';
	let confirmPassword = '';
	let passwordErrors = {};
	
	// Role modal
	let newRole = '';
	
	// Role options
	let roleOptions = getRoleOptions();
	
	// Tenant and outlet data
	let tenants = [];
	let outlets = [];
	let filteredOutlets = []; // Outlets filtered by selected tenant

	onMount(() => {
		loadUsers();
		loadStats();
		loadTenants();
		loadOutlets();
	});
	
	async function loadTenants() {
		try {
			const response = await getTenants();
			tenants = response.results || response;
		} catch (error) {
			console.error('Error loading tenants:', error);
		}
	}
	
	async function loadOutlets() {
		try {
			const response = await getAllOutlets();
			outlets = response.results || response;
			console.log('Loaded outlets:', outlets.length, outlets);
		} catch (error) {
			console.error('Error loading outlets:', error);
		}
	}
	
	// Filter outlets when tenant changes
	$: if (formData.tenant) {
		const tenantId = typeof formData.tenant === 'string' ? parseInt(formData.tenant) : formData.tenant;
		filteredOutlets = outlets.filter(o => {
			const outletTenantId = typeof o.tenant === 'object' ? o.tenant.id : o.tenant;
			return outletTenantId === tenantId;
		});
		console.log('Filtering outlets for tenant:', tenantId, 'Found:', filteredOutlets.length);
		
		// Reset outlet if it's not in the filtered list
		if (formData.outlet && !filteredOutlets.find(o => o.id === parseInt(formData.outlet))) {
			formData.outlet = null;
		}
		// Reset accessible_outlets
		formData.accessible_outlets = formData.accessible_outlets.filter(id => 
			filteredOutlets.find(o => o.id === id)
		);
	} else {
		filteredOutlets = [];
		formData.outlet = null;
		formData.accessible_outlets = [];
	}

	async function loadUsers() {
		loading = true;
		try {
			const response = await getUsers({
				search: searchQuery,
				role: selectedRole,
				is_active: isActiveFilter,
				page: currentPage,
				page_size: 10,
				ordering: '-created_at'
			});
			
			users = response.results || response;
			totalCount = response.count || users.length;
			totalPages = response.next ? Math.ceil(totalCount / 10) : 1;
		} catch (error) {
			console.error('Error loading users:', error);
			alert('Failed to load users');
		} finally {
			loading = false;
		}
	}

	async function loadStats() {
		try {
			const statsData = await getUserStats();
			stats = statsData;
		} catch (error) {
			console.error('Error loading stats:', error);
		}
	}

	function handleSearch() {
		currentPage = 1;
		loadUsers();
	}

	function handleFilterChange() {
		currentPage = 1;
		loadUsers();
	}

	function goToPage(page) {
		currentPage = page;
		loadUsers();
	}

	function openCreateModal() {
		editingUser = null;
		formData = {
			username: '',
			email: '',
			first_name: '',
			last_name: '',
			phone_number: '',
			role: 'cashier',
			password: '',
			is_active: true,
			tenant: null,
			outlet: null,
			accessible_outlets: []
		};
		formErrors = {};
		showCreateModal = true;
	}

	function openEditModal(user) {
		editingUser = user;
		
		// Extract outlet IDs from accessible_outlets if it's an array of objects
		let accessibleOutletIds = [];
		if (user.accessible_outlets) {
			if (Array.isArray(user.accessible_outlets)) {
				// If it's array of objects with 'id' property
				accessibleOutletIds = user.accessible_outlets.map(o => typeof o === 'object' ? o.id : o);
			} else if (user.accessible_outlets === 'all') {
				accessibleOutletIds = [];
			}
		}
		
		console.log('Opening edit modal for user:', user.username);
		console.log('User data:', user);
		console.log('User accessible_outlets:', user.accessible_outlets);
		console.log('Mapped to IDs:', accessibleOutletIds);
		
		formData = {
			username: user.username,
			email: user.email || '',
			first_name: user.first_name || '',
			last_name: user.last_name || '',
			phone_number: user.phone_number || '',
			role: user.role,
			password: '', // Don't pre-fill password
			is_active: user.is_active,
			tenant: user.tenant || null,
			outlet: user.outlet || null,
			accessible_outlets: accessibleOutletIds
		};
		
		console.log('FormData after mapping:', formData);
		console.log('Role value:', formData.role);
		console.log('Available roleOptions:', roleOptions);
		
		formErrors = {};
		showCreateModal = true;
	}

	function validateForm() {
		formErrors = {};
		
		if (!formData.username?.trim()) {
			formErrors.username = 'Username is required';
		}
		
		if (!editingUser && !formData.password) {
			formErrors.password = 'Password is required for new users';
		}
		
		if (formData.password && formData.password.length < 6) {
			formErrors.password = 'Password must be at least 6 characters';
		}
		
		if (formData.email && !formData.email.includes('@')) {
			formErrors.email = 'Invalid email format';
		}
		
		// Validate tenant for non-super-admin roles
		if (formData.role !== 'super_admin' && formData.role !== 'admin') {
			if (!formData.tenant) {
				formErrors.tenant = 'Tenant is required for this role';
			}
			
			// Validate outlet for cashier/kitchen
			if ((formData.role === 'cashier' || formData.role === 'kitchen') && !formData.outlet) {
				formErrors.outlet = 'Outlet is required for this role';
			}
		}
		
		return Object.keys(formErrors).length === 0;
	}

	async function handleSubmit() {
		if (!validateForm()) return;
		
		try {
			const submitData = { ...formData };
			
			// Remove empty password for updates
			if (editingUser && !submitData.password) {
				delete submitData.password;
			}
			
			// Rename accessible_outlets to accessible_outlet_ids for backend
			if (submitData.accessible_outlets && submitData.accessible_outlets.length > 0) {
				submitData.accessible_outlet_ids = submitData.accessible_outlets;
			} else if (submitData.role === 'manager') {
				// Send empty array if manager has no outlets selected
				submitData.accessible_outlet_ids = [];
			}
			delete submitData.accessible_outlets;
			
			console.log('Submitting user data:', JSON.stringify(submitData, null, 2));
			
			if (editingUser) {
				await updateUser(editingUser.id, submitData);
				Swal.fire({
					title: 'Updated!',
					html: `<p>User <strong>${submitData.username}</strong> has been updated successfully.</p>`,
					icon: 'success',
					timer: 3000,
					showConfirmButton: false
				});
			} else {
				await createUser(submitData);
				Swal.fire({
					title: 'Created!',
					html: `<p>User <strong>${submitData.username}</strong> has been created successfully.</p>`,
					icon: 'success',
					timer: 3000,
					showConfirmButton: false
				});
			}
			
			showCreateModal = false;
			loadUsers();
			loadStats();
		} catch (error) {
			console.error('Error saving user:', error);
			Swal.fire('Error', 'Failed to save user: ' + (error.message || 'Unknown error'), 'error');
		}
	}

	function confirmDelete(user) {
		userToDelete = user;
		showDeleteModal = true;
	}

	async function handleDelete() {
		if (!userToDelete) return;
		
		const result = await Swal.fire({
			title: 'Delete User?',
			html: `<p>Are you sure you want to delete user <strong>${userToDelete.username}</strong>?</p><p class="text-sm text-red-600 mt-2">This action cannot be undone.</p>`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#d33',
			cancelButtonColor: '#3085d6',
			confirmButtonText: 'Yes, delete it!',
			cancelButtonText: 'Cancel'
		});
		
		if (!result.isConfirmed) {
			showDeleteModal = false;
			userToDelete = null;
			return;
		}
		
		try {
			await deleteUser(userToDelete.id);
			showDeleteModal = false;
			userToDelete = null;
			loadUsers();
			loadStats();
			
			Swal.fire({
				title: 'Deleted!',
				text: 'User has been deleted successfully.',
				icon: 'success',
				timer: 3000,
				showConfirmButton: false
			});
		} catch (error) {
			console.error('Error deleting user:', error);
			Swal.fire('Error', 'Failed to delete user', 'error');
		}
	}

	function openPasswordModal(user) {
		editingUser = user;
		newPassword = '';
		confirmPassword = '';
		passwordErrors = {};
		showPasswordModal = true;
	}

	async function handlePasswordReset() {
		passwordErrors = {};
		
		if (!newPassword) {
			passwordErrors.newPassword = 'Password is required';
			return;
		}
		
		if (newPassword.length < 6) {
			passwordErrors.newPassword = 'Password must be at least 6 characters';
			return;
		}
		
		if (newPassword !== confirmPassword) {
			passwordErrors.confirmPassword = 'Passwords do not match';
			return;
		}
		
		try {
			await resetUserPassword(editingUser.id, newPassword);
			showPasswordModal = false;
			
			Swal.fire({
				title: 'Password Reset!',
				html: `<p>Password has been reset successfully for <strong>${editingUser.username}</strong>.</p>`,
				icon: 'success',
				timer: 3000,
				showConfirmButton: false
			});
		} catch (error) {
			console.error('Error resetting password:', error);
			Swal.fire('Error', 'Failed to reset password', 'error');
		}
	}

	function openRoleModal(user) {
		editingUser = user;
		newRole = user.role;
		showRoleModal = true;
	}

	async function handleRoleChange() {
		if (!newRole || newRole === editingUser.role) {
			showRoleModal = false;
			return;
		}
		
		try {
			await changeUserRole(editingUser.id, newRole);
			showRoleModal = false;
			loadUsers();
			loadStats();
			
			Swal.fire({
				title: 'Role Changed!',
				html: `<p>Role for <strong>${editingUser.username}</strong> has been changed to <strong>${formatRole(newRole)}</strong>.</p>`,
				icon: 'success',
				timer: 3000,
				showConfirmButton: false
			});
		} catch (error) {
			console.error('Error changing role:', error);
			Swal.fire('Error', 'Failed to change role', 'error');
		}
	}

	function toggleSelectUser(userId) {
		if (selectedUsers.includes(userId)) {
			selectedUsers = selectedUsers.filter(id => id !== userId);
		} else {
			selectedUsers = [...selectedUsers, userId];
		}
	}

	function toggleSelectAll() {
		if (selectedUsers.length === users.length) {
			selectedUsers = [];
		} else {
			selectedUsers = users.map(u => u.id);
		}
	}

	async function handleBulkAction() {
		if (!bulkAction || selectedUsers.length === 0) return;
		
		const updates = {};
		if (bulkAction === 'activate') updates.is_active = true;
		if (bulkAction === 'deactivate') updates.is_active = false;
		
		if (Object.keys(updates).length === 0) return;
		
		try {
			await bulkUpdateUsers(selectedUsers, updates);
			selectedUsers = [];
			bulkAction = '';
			loadUsers();
			loadStats();
		} catch (error) {
			console.error('Error applying bulk action:', error);
			alert('Failed to apply bulk action');
		}
	}
</script>

<svelte:head>
	<title>Users - Admin Panel</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Users Management</h1>
			<p class="text-gray-600 mt-1">Manage system users and permissions</p>
		</div>
		<button
			on:click={openCreateModal}
			class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
		>
			<span>➕</span>
			<span>Add User</span>
		</button>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Total Users</p>
					<p class="text-2xl font-bold text-gray-900 mt-2">{stats.total}</p>
				</div>
				<div class="bg-blue-100 p-3 rounded-lg">
					<span class="text-2xl">👥</span>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Active</p>
					<p class="text-2xl font-bold text-green-600 mt-2">{stats.active}</p>
				</div>
				<div class="bg-green-100 p-3 rounded-lg">
					<span class="text-2xl">✅</span>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Inactive</p>
					<p class="text-2xl font-bold text-gray-600 mt-2">{stats.inactive}</p>
				</div>
				<div class="bg-gray-100 p-3 rounded-lg">
					<span class="text-2xl">❌</span>
				</div>
			</div>
		</div>

		<div class="bg-white rounded-lg shadow p-6">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm font-medium text-gray-600">Roles</p>
					<p class="text-2xl font-bold text-gray-900 mt-2">{Object.keys(stats.by_role || {}).length}</p>
				</div>
				<div class="bg-purple-100 p-3 rounded-lg">
					<span class="text-2xl">🎭</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Filters & Search -->
	<div class="bg-white rounded-lg shadow p-6 mb-6">
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<!-- Search -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
				<input
					type="text"
					bind:value={searchQuery}
					on:input={handleSearch}
					placeholder="Search by name, username, email..."
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				/>
			</div>

			<!-- Role Filter -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
				<select
					bind:value={selectedRole}
					on:change={handleFilterChange}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				>
					<option value="">All Roles</option>
					{#each roleOptions as role}
						<option value={role.value}>{role.label}</option>
					{/each}
				</select>
			</div>

			<!-- Active Filter -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
				<select
					bind:value={isActiveFilter}
					on:change={handleFilterChange}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
				>
					<option value="">All Status</option>
					<option value="true">Active</option>
					<option value="false">Inactive</option>
				</select>
			</div>
		</div>
	</div>

	<!-- Bulk Actions -->
	{#if selectedUsers.length > 0}
		<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-center gap-4">
			<span class="text-blue-900 font-medium">{selectedUsers.length} selected</span>
			<select
				bind:value={bulkAction}
				class="px-4 py-2 border border-blue-300 rounded-lg bg-white"
			>
				<option value="">Choose action...</option>
				<option value="activate">Activate</option>
				<option value="deactivate">Deactivate</option>
			</select>
			<button
				on:click={handleBulkAction}
				disabled={!bulkAction}
				class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
			>
				Apply
			</button>
		</div>
	{/if}

	<!-- Users Table -->
	<div class="bg-white rounded-lg shadow overflow-hidden">
		{#if loading}
			<div class="p-12 text-center">
				<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
				<p class="text-gray-600 mt-4">Loading users...</p>
			</div>
		{:else if users.length === 0}
			<div class="p-12 text-center">
				<span class="text-6xl">👥</span>
				<p class="text-xl font-medium text-gray-900 mt-4">No users found</p>
				<p class="text-gray-600 mt-2">Create your first user to get started</p>
				<button
					on:click={openCreateModal}
					class="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Add User
				</button>
			</div>
		{:else}
			<table class="min-w-full divide-y divide-gray-200">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-6 py-3 text-left">
							<input
								type="checkbox"
								checked={selectedUsers.length === users.length}
								on:change={toggleSelectAll}
								class="rounded border-gray-300"
							/>
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Login</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each users as user}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4">
								<input
									type="checkbox"
									checked={selectedUsers.includes(user.id)}
									on:change={() => toggleSelectUser(user.id)}
									class="rounded border-gray-300"
								/>
							</td>
							<td class="px-6 py-4">
								<div>
									<p class="text-sm font-medium text-gray-900">{user.username}</p>
									{#if user.email}
										<p class="text-sm text-gray-600">{user.email}</p>
									{/if}
									{#if user.tenant_name}
										<p class="text-xs text-gray-500">Tenant: {user.tenant_name}</p>
									{/if}
								</div>
							</td>
							<td class="px-6 py-4">
								{#if true}
									{@const roleInfo = formatRole(user.role)}
									<span class="px-2 py-1 text-xs font-medium rounded-full {roleInfo.bgColor} {roleInfo.textColor}">
										{roleInfo.label}
									</span>
								{/if}
							</td>
							<td class="px-6 py-4">
								{#if true}
									{@const status = user.is_active}
									<span class="px-2 py-1 text-xs font-medium rounded-full {status ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
										{status ? 'Active' : 'Inactive'}
									</span>
								{/if}
							</td>
							<td class="px-6 py-4 text-sm text-gray-600">
								{formatLastLogin(user.last_login)}
							</td>
							<td class="px-6 py-4 text-sm">
								<div class="flex items-center gap-2">
									<button
										on:click={() => openEditModal(user)}
										class="text-blue-600 hover:text-blue-800"
										title="Edit"
									>
										✏️
									</button>
									<button
										on:click={() => openPasswordModal(user)}
										class="text-yellow-600 hover:text-yellow-800"
										title="Reset Password"
									>
										🔑
									</button>
									<button
										on:click={() => openRoleModal(user)}
										class="text-purple-600 hover:text-purple-800"
										title="Change Role"
									>
										🎭
									</button>
									<button
										on:click={() => confirmDelete(user)}
										class="text-red-600 hover:text-red-800"
										title="Delete"
									>
										🗑️
									</button>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>

			<!-- Pagination -->
			{#if totalPages > 1}
				<div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
					<div class="text-sm text-gray-700">
						Showing page {currentPage} of {totalPages} ({totalCount} total)
					</div>
					<div class="flex gap-2">
						<button
							on:click={() => goToPage(currentPage - 1)}
							disabled={currentPage === 1}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Previous
						</button>
						{#each Array(Math.min(5, totalPages)) as _, i}
							{@const page = i + 1}
							<button
								on:click={() => goToPage(page)}
								class="px-3 py-1 border rounded-lg {currentPage === page ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 hover:bg-gray-50'}"
							>
								{page}
							</button>
						{/each}
						<button
							on:click={() => goToPage(currentPage + 1)}
							disabled={currentPage === totalPages}
							class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Next
						</button>
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>

<!-- Create/Edit Modal -->
{#if showCreateModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
			<div class="p-6 border-b border-gray-200">
				<h2 class="text-2xl font-bold text-gray-900">
					{editingUser ? 'Edit User' : 'Add New User'}
				</h2>
			</div>
			
			<form on:submit|preventDefault={handleSubmit} class="p-6 space-y-4">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<!-- Username -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Username <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							bind:value={formData.username}
							disabled={editingUser}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
							placeholder="username"
						/>
						{#if formErrors.username}
							<p class="text-red-500 text-sm mt-1">{formErrors.username}</p>
						{/if}
					</div>

					<!-- Email -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
						<input
							type="email"
							bind:value={formData.email}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="user@example.com"
						/>
						{#if formErrors.email}
							<p class="text-red-500 text-sm mt-1">{formErrors.email}</p>
						{/if}
					</div>

					<!-- First Name -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
						<input
							type="text"
							bind:value={formData.first_name}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="John"
						/>
					</div>

					<!-- Last Name -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
						<input
							type="text"
							bind:value={formData.last_name}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="Doe"
						/>
					</div>

					<!-- Phone -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
						<input
							type="tel"
							bind:value={formData.phone_number}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder="08123456789"
						/>
					</div>

					<!-- Role -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Role <span class="text-red-500">*</span>
						</label>
						<select
							bind:value={formData.role}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
						>
							{#each roleOptions as role}
								<option value={role.value}>{role.label}</option>
							{/each}
						</select>
					</div>
					
					<!-- Tenant (only for non-super-admin roles) -->
					{#if formData.role !== 'super_admin' && formData.role !== 'admin'}
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Tenant <span class="text-red-500">*</span>
							</label>
							<select
								bind:value={formData.tenant}
								class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							>
								<option value={null}>-- Select Tenant --</option>
								{#each tenants as tenant}
									<option value={tenant.id}>{tenant.name}</option>
								{/each}
							</select>
							<p class="text-xs text-gray-500 mt-1">🏢 Which restaurant brand this user belongs to</p>
						</div>
					{/if}
					
					<!-- Outlet (only for cashier/kitchen roles) -->
					{#if (formData.role === 'cashier' || formData.role === 'kitchen') && formData.tenant}
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Outlet <span class="text-red-500">*</span>
							</label>
							<select
								bind:value={formData.outlet}
								class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							>
								<option value={null}>-- Select Outlet --</option>
								{#each filteredOutlets as outlet}
									<option value={outlet.id}>{outlet.name}</option>
								{/each}
							</select>
							<p class="text-xs text-gray-500 mt-1">📍 Specific outlet for this {formData.role}</p>
						</div>
					{/if}
					
					<!-- Accessible Outlets (only for manager role) -->
					{#if formData.role === 'manager' && formData.tenant}
						<div class="md:col-span-2">
							<label class="block text-sm font-medium text-gray-700 mb-2">
								Accessible Outlets
							</label>
							<div class="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-3">
								{#each filteredOutlets as outlet}
									<label class="flex items-center space-x-2">
										<input
											type="checkbox"
											value={outlet.id}
											checked={formData.accessible_outlets.includes(outlet.id)}
											on:change={(e) => {
												if (e.target.checked) {
													formData.accessible_outlets = [...formData.accessible_outlets, outlet.id];
												} else {
													formData.accessible_outlets = formData.accessible_outlets.filter(id => id !== outlet.id);
												}
											}}
											class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
										/>
										<span class="text-sm text-gray-700">{outlet.name}</span>
									</label>
								{/each}
							</div>
							<p class="text-xs text-gray-500 mt-1">📍 Manager can access multiple outlets</p>
						</div>
					{/if}

					<!-- Password -->
					<div class="md:col-span-2">
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Password {#if !editingUser}<span class="text-red-500">*</span>{/if}
						</label>
						<input
							type="password"
							bind:value={formData.password}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
							placeholder={editingUser ? 'Leave blank to keep current password' : 'Min 6 characters'}
						/>
						{#if formErrors.password}
							<p class="text-red-500 text-sm mt-1">{formErrors.password}</p>
						{/if}
					</div>
				</div>

				<!-- Is Active -->
				<div>
					<label class="flex items-center">
						<input
							type="checkbox"
							bind:checked={formData.is_active}
							class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
						/>
						<span class="ml-2 text-sm text-gray-700">Active</span>
					</label>
				</div>

				<!-- Actions -->
				<div class="flex items-center justify-end gap-4 pt-4 border-t border-gray-200">
					<button
						type="button"
						on:click={() => showCreateModal = false}
						class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
					>
						Cancel
					</button>
					<button
						type="submit"
						class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
					>
						{editingUser ? 'Update' : 'Create'} User
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Password Reset Modal -->
{#if showPasswordModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
			<h3 class="text-lg font-bold text-gray-900 mb-4">Reset Password</h3>
			<p class="text-gray-600 mb-4">Set a new password for {editingUser?.username}</p>
			
			<div class="space-y-4">
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
					<input
						type="password"
						bind:value={newPassword}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
						placeholder="Min 6 characters"
					/>
					{#if passwordErrors.newPassword}
						<p class="text-red-500 text-sm mt-1">{passwordErrors.newPassword}</p>
					{/if}
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
					<input
						type="password"
						bind:value={confirmPassword}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
						placeholder="Re-enter password"
					/>
					{#if passwordErrors.confirmPassword}
						<p class="text-red-500 text-sm mt-1">{passwordErrors.confirmPassword}</p>
					{/if}
				</div>
			</div>

			<div class="flex items-center justify-end gap-4 mt-6">
				<button
					on:click={() => showPasswordModal = false}
					class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
				>
					Cancel
				</button>
				<button
					on:click={handlePasswordReset}
					class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Reset Password
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Role Change Modal -->
{#if showRoleModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
			<h3 class="text-lg font-bold text-gray-900 mb-4">Change Role</h3>
			<p class="text-gray-600 mb-4">Change role for {editingUser?.username}</p>
			
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-1">New Role</label>
				<select
					bind:value={newRole}
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
				>
					{#each roleOptions as role}
						<option value={role.value}>{role.label}</option>
					{/each}
				</select>
			</div>

			<div class="flex items-center justify-end gap-4 mt-6">
				<button
					on:click={() => showRoleModal = false}
					class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
				>
					Cancel
				</button>
				<button
					on:click={handleRoleChange}
					class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Change Role
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
			<h3 class="text-lg font-bold text-gray-900 mb-4">Confirm Delete</h3>
			<p class="text-gray-600 mb-6">
				Are you sure you want to delete user "{userToDelete?.username}"? This action cannot be undone.
			</p>
			<div class="flex items-center justify-end gap-4">
				<button
					on:click={() => { showDeleteModal = false; userToDelete = null; }}
					class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
				>
					Cancel
				</button>
				<button
					on:click={handleDelete}
					class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
				>
					Delete
				</button>
			</div>
		</div>
	</div>
{/if}
