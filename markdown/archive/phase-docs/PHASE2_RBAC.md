# Phase 2: Frontend Foundation - RBAC Implementation

**Status:** ✅ COMPLETED  
**Duration:** Completed in one session  
**Date:** 2024

---

## 📋 Overview

Phase 2 implements the frontend foundation for Role-Based Access Control (RBAC) in the Admin Panel. This phase focuses on creating reusable components, utilities, and patterns for implementing permission-based UI across all admin pages.

**Key Objectives:**
- ✅ Enhance auth store with comprehensive role helper functions
- ✅ Create reusable components for permission-based UI rendering
- ✅ Implement route protection utilities
- ✅ Update navigation with role-based visibility
- ✅ Create example implementations for future pages
- ✅ Build unauthorized access page

---

## 🏗️ Architecture

### Component Hierarchy
```
+layout.svelte (Root)
├── TenantSelector (Admin only)
├── Sidebar Navigation (Role-based items)
└── Page Routes
    ├── +page.js (Route protection)
    └── +page.svelte (UI components)
        ├── RoleGuard (Conditional rendering)
        ├── PermissionButton (Auto-hide buttons)
        └── Regular UI elements
```

### Data Flow
```
User Login → Auth Store → Role Helpers
                ↓
        Route Protection
                ↓
     Page Component Load
                ↓
    RoleGuard/PermissionButton
                ↓
        Conditional UI
```

---

## 📁 Files Created/Modified

### 1. **admin/src/lib/stores/auth.js** ✅
Enhanced authentication store with comprehensive role management.

**New Exports:**
```javascript
// Constants
export const ROLE_HIERARCHY = {
  super_admin: 100,
  admin: 90,
  manager: 50,
  cashier: 30,
  kitchen: 20
};

export const PERMISSION_MATRIX = {
  products: {
    create: ['super_admin', 'admin', 'manager'],
    read: ['super_admin', 'admin', 'manager', 'cashier'],
    update: ['super_admin', 'admin', 'manager'],
    delete: ['super_admin', 'admin', 'manager']
  },
  orders: {
    create: ['super_admin', 'admin', 'manager', 'cashier'],
    read: ['super_admin', 'admin', 'manager', 'cashier', 'kitchen'],
    update: ['super_admin', 'admin', 'manager', 'cashier', 'kitchen'],
    delete: ['super_admin', 'admin', 'manager']
  },
  // ... more resources
};

// Helper Functions
export function getRoleLevel(role)
export function hasRole(...roles)
export function hasRoleLevel(minRole)
export function isAdmin()
export function canAccessTenant(tenantId)
export function canPerform(action, resource)
export function canCreate(resource)
export function canRead(resource)
export function canUpdate(resource)
export function canDelete(resource)
```

**Usage Example:**
```javascript
import { hasRole, canCreate, isAdmin } from '$lib/stores/auth';

if (hasRole('manager', 'admin')) {
  // Show manager-level features
}

if (canCreate('products')) {
  // Show create product button
}

if (isAdmin()) {
  // Show tenant selector
}
```

---

### 2. **admin/src/lib/components/RoleGuard.svelte** ✅
Conditionally renders content based on roles or permissions.

**Props:**
```javascript
export let roles = null;           // ['admin', 'manager']
export let minRole = null;         // 'manager'
export let action = null;          // 'create', 'update', 'delete'
export let resource = null;        // 'products', 'orders'
export let showFallback = false;   // Show fallback slot
```

**Usage Examples:**
```svelte
<!-- By specific roles -->
<RoleGuard roles={['admin', 'super_admin']}>
  <button>Admin Only Button</button>
</RoleGuard>

<!-- By minimum role level -->
<RoleGuard minRole="manager">
  <div>Manager and above can see this</div>
</RoleGuard>

<!-- By permission -->
<RoleGuard action="delete" resource="products">
  <button>Delete Product</button>
</RoleGuard>

<!-- With fallback -->
<RoleGuard roles={['admin']} showFallback={true}>
  <div>Admin content</div>
  <div slot="fallback">
    <p>You need admin access to see this</p>
  </div>
</RoleGuard>
```

**Features:**
- Multiple authorization strategies (roles, minRole, action+resource)
- Optional fallback content for unauthorized users
- Reactive to auth store changes
- Zero UI footprint when access denied

---

### 3. **admin/src/lib/components/PermissionButton.svelte** ✅
Self-hiding button based on permissions.

**Props:**
```javascript
export let action;              // Required: 'create', 'update', 'delete'
export let resource;            // Required: 'products', 'orders'
export let variant = 'primary'; // 'primary', 'secondary', 'danger'
export let size = 'md';         // 'sm', 'md', 'lg'
export let disabled = false;
export let type = 'button';
```

**Usage Example:**
```svelte
<PermissionButton
  action="create"
  resource="products"
  variant="primary"
  on:click={handleCreate}
>
  <svg>...</svg>
  Create Product
</PermissionButton>

<PermissionButton
  action="delete"
  resource="orders"
  variant="danger"
  size="sm"
  on:click={() => deleteOrder(id)}
>
  Delete
</PermissionButton>
```

**Features:**
- Auto-hides when user lacks permission
- Built-in styling variants (primary, secondary, danger)
- Size variants (sm, md, lg)
- Forwards all click events
- Responsive design

---

### 4. **admin/src/lib/components/TenantSelector.svelte** ✅
Dropdown for admin users to switch tenant context.

**Props:**
```javascript
export let selectedTenant = null;  // Current tenant ID or null for "All"
export let onChange = null;        // Callback(tenantId)
```

**Usage Example:**
```svelte
<script>
  let selectedTenant = null;
  
  function handleTenantChange(tenantId) {
    selectedTenant = tenantId;
    // Reload data with new tenant filter
    loadData();
  }
</script>

<TenantSelector
  selectedTenant={selectedTenant}
  onChange={handleTenantChange}
/>
```

**Features:**
- Only visible to admin users
- Loads tenants from `/api/admin/tenants/`
- "All Tenants" option for global view
- Loading and error states
- Styled with TailwindCSS
- Auto-hides for non-admin users

---

### 5. **admin/src/lib/utils/routeGuard.js** ✅
Server-side route protection utilities for SvelteKit.

**Exports:**
```javascript
export function requireAuth(event)
export function requireRole(event, ...roles)
export function requireRoleLevel(event, minRole)
export function requirePermission(event, action, resource)
export function isAdminUser()
export function getQueryParams(event, params = {})
```

**Usage in +page.js:**
```javascript
import { requireRoleLevel, getQueryParams } from '$lib/utils/routeGuard';

export async function load(event) {
  // Protect route - redirects if unauthorized
  const user = requireRoleLevel(event, 'manager');
  
  // Get query params with tenant filter
  const params = getQueryParams(event, {
    page: event.url.searchParams.get('page') || '1',
    search: event.url.searchParams.get('search') || ''
  });
  
  // Fetch data
  const response = await event.fetch(`/api/admin/products/?${params}`);
  const data = await response.json();
  
  return { products: data, user };
}
```

**Function Details:**

#### requireAuth(event)
Ensures user is authenticated. Redirects to login with return URL.

#### requireRole(event, ...roles)
Ensures user has one of the specified roles. Redirects to `/unauthorized`.

```javascript
// Allow only admins
requireRole(event, 'admin', 'super_admin');
```

#### requireRoleLevel(event, minRole)
Ensures user meets minimum role level. Redirects to `/unauthorized`.

```javascript
// Require manager level or above
requireRoleLevel(event, 'manager');
```

#### requirePermission(event, action, resource)
Ensures user has specific permission. Redirects to `/unauthorized`.

```javascript
// Require delete permission on products
requirePermission(event, 'delete', 'products');
```

#### isAdminUser()
Boolean check without redirect. Useful for conditional logic.

```javascript
const user = get(authUser);
if (isAdminUser()) {
  // Load all tenants
} else {
  // Load only user's tenant
}
```

#### getQueryParams(event, params)
Builds query params with automatic tenant filter for admin users.

```javascript
const params = getQueryParams(event, {
  page: '1',
  search: 'pizza'
});
// Admin: ?page=1&search=pizza&tenant=5
// User: ?page=1&search=pizza
```

---

### 6. **admin/src/routes/unauthorized/+page.svelte** ✅
Friendly error page for unauthorized access.

**Features:**
- Clear error message
- Shows current user info and role
- "Back to Dashboard" button
- "Go Back" browser history button
- Help text for contacting admin
- Responsive design
- Icon-based visual feedback

**User Experience:**
1. User tries to access restricted page
2. Route guard redirects to `/unauthorized`
3. Page shows:
   - Warning icon
   - "Access Denied" message
   - User's current role
   - Navigation options
   - Help text

---

### 7. **admin/src/routes/+layout.svelte** ✅
Updated root layout with tenant selector and role-based navigation.

**Changes:**
```svelte
<script>
  import RoleGuard from '$lib/components/RoleGuard.svelte';
  import TenantSelector from '$lib/components/TenantSelector.svelte';
  import { user, isAdmin } from '$lib/stores/auth';
  
  let selectedTenant = null;
  
  function handleTenantChange(tenantId) {
    selectedTenant = tenantId;
    // Reload current page data
    invalidateAll();
  }
</script>

<!-- Sidebar -->
<aside>
  <!-- Tenant Selector (Admin only) -->
  <RoleGuard roles={['admin', 'super_admin']}>
    <TenantSelector
      selectedTenant={selectedTenant}
      onChange={handleTenantChange}
    />
  </RoleGuard>
  
  <!-- User info with role badge -->
  <div class="user-info">
    <p>{$user.username}</p>
    <span class="role-badge">{$user.role}</span>
    {#if $user.is_superuser}
      <span class="superuser-badge">Superuser</span>
    {/if}
  </div>
  
  <!-- Navigation items -->
  <nav>
    <a href="/dashboard">Dashboard</a>
    
    <RoleGuard minRole="cashier">
      <a href="/products">Products</a>
      <a href="/categories">Categories</a>
      <a href="/orders">Orders</a>
    </RoleGuard>
    
    <RoleGuard minRole="manager">
      <a href="/customers">Customers</a>
      <a href="/promotions">Promotions</a>
    </RoleGuard>
    
    <RoleGuard roles={['admin', 'super_admin']}>
      <a href="/users">Users</a>
      <a href="/tenants">Tenants</a>
      <a href="/outlets">Outlets</a>
    </RoleGuard>
  </nav>
</aside>
```

---

## 📖 Implementation Examples

### Example 1: Protected Products Page

#### admin/src/routes/products/+page.js
```javascript
import { requireRoleLevel, getQueryParams } from '$lib/utils/routeGuard';

export async function load(event) {
  // Protect route: Require manager level or above
  const user = requireRoleLevel(event, 'manager');
  
  // Get query params with tenant filter
  const params = getQueryParams(event, {
    page: event.url.searchParams.get('page') || '1',
    category: event.url.searchParams.get('category') || '',
    search: event.url.searchParams.get('search') || ''
  });
  
  // Fetch products
  const response = await event.fetch(
    `/api/admin/products/?${params.toString()}`,
    {
      headers: {
        'Authorization': `Bearer ${user.token}`
      }
    }
  );
  
  const data = await response.json();
  
  return {
    products: data.results || [],
    pagination: {
      count: data.count,
      next: data.next,
      previous: data.previous
    },
    user
  };
}
```

#### admin/src/routes/products/+page.svelte
```svelte
<script>
  import RoleGuard from '$lib/components/RoleGuard.svelte';
  import PermissionButton from '$lib/components/PermissionButton.svelte';
  
  export let data;
  $: ({ products, user } = data);
  
  function handleCreate() {
    goto('/products/create');
  }
  
  async function handleDelete(id) {
    if (!confirm('Delete this product?')) return;
    await fetch(`/api/admin/products/${id}/`, { method: 'DELETE' });
    invalidate('/products');
  }
</script>

<div class="page-header">
  <h1>Products</h1>
  
  <!-- Create button - auto-hides for users without permission -->
  <PermissionButton
    action="create"
    resource="products"
    on:click={handleCreate}
  >
    Add Product
  </PermissionButton>
</div>

<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Price</th>
      <th>Stock</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {#each products as product}
      <tr>
        <td>{product.name}</td>
        <td>Rp {product.price.toLocaleString()}</td>
        <td>{product.stock_quantity}</td>
        <td>
          <!-- Edit always visible -->
          <button on:click={() => goto(`/products/${product.id}/edit`)}>
            Edit
          </button>
          
          <!-- Delete only for authorized users -->
          <RoleGuard action="delete" resource="products">
            <button on:click={() => handleDelete(product.id)}>
              Delete
            </button>
          </RoleGuard>
        </td>
      </tr>
    {/each}
  </tbody>
</table>
```

---

### Example 2: Orders Page with Kitchen Staff Access

#### admin/src/routes/orders/+page.js
```javascript
import { requireRoleLevel } from '$lib/utils/routeGuard';

export async function load(event) {
  // Kitchen staff can access orders (minimum role level)
  const user = requireRoleLevel(event, 'kitchen');
  
  // Kitchen staff: only show their tenant's orders
  // Manager+: can see all tenants if selected
  const params = new URLSearchParams({
    status: event.url.searchParams.get('status') || 'pending'
  });
  
  if (!user.is_superuser && user.role !== 'admin') {
    params.set('tenant', user.tenant.id);
  }
  
  const response = await event.fetch(`/api/admin/orders/?${params}`);
  const data = await response.json();
  
  return { orders: data.results, user };
}
```

#### admin/src/routes/orders/+page.svelte
```svelte
<script>
  import RoleGuard from '$lib/components/RoleGuard.svelte';
  import { hasRole } from '$lib/stores/auth';
  
  export let data;
  $: ({ orders, user } = data);
  
  // Kitchen staff can only update status
  // Cashier+ can create/update
  // Manager+ can delete
</script>

<div>
  <h1>Orders</h1>
  
  {#each orders as order}
    <div class="order-card">
      <h3>Order #{order.id}</h3>
      
      <!-- Status update (kitchen staff and above) -->
      {#if hasRole('kitchen', 'cashier', 'manager', 'admin')}
        <select bind:value={order.status}>
          <option value="pending">Pending</option>
          <option value="preparing">Preparing</option>
          <option value="ready">Ready</option>
          <option value="completed">Completed</option>
        </select>
      {/if}
      
      <!-- Edit button (cashier and above) -->
      <RoleGuard minRole="cashier">
        <button>Edit Order</button>
      </RoleGuard>
      
      <!-- Delete button (manager and above) -->
      <RoleGuard minRole="manager">
        <button class="btn-danger">Delete</button>
      </RoleGuard>
    </div>
  {/each}
</div>
```

---

### Example 3: Admin-Only Users Page

#### admin/src/routes/users/+page.js
```javascript
import { requireRole } from '$lib/utils/routeGuard';

export async function load(event) {
  // Only admin and super_admin can access
  const user = requireRole(event, 'admin', 'super_admin');
  
  const response = await event.fetch('/api/admin/users/');
  const data = await response.json();
  
  return { users: data, user };
}
```

---

## 🎨 UI/UX Patterns

### Navigation Visibility
```svelte
<!-- Always visible -->
<a href="/dashboard">Dashboard</a>

<!-- Cashier and above -->
<RoleGuard minRole="cashier">
  <a href="/products">Products</a>
  <a href="/orders">Orders</a>
</RoleGuard>

<!-- Manager and above -->
<RoleGuard minRole="manager">
  <a href="/promotions">Promotions</a>
</RoleGuard>

<!-- Admin only -->
<RoleGuard roles={['admin', 'super_admin']}>
  <a href="/users">Users</a>
  <a href="/tenants">Tenants</a>
</RoleGuard>
```

### Button Visibility
```svelte
<!-- Auto-hiding create button -->
<PermissionButton action="create" resource="products">
  Add Product
</PermissionButton>

<!-- Manual guard with custom styling -->
<RoleGuard action="delete" resource="orders">
  <button class="custom-delete-btn">Delete</button>
</RoleGuard>
```

### Conditional Features
```svelte
{#if $isAdmin}
  <TenantSelector bind:selectedTenant />
{/if}

{#if $canCreate('products')}
  <div class="create-form">...</div>
{/if}

{#if $hasRoleLevel('manager')}
  <div class="analytics-panel">...</div>
{/if}
```

---

## 🔄 Data Flow Patterns

### Page Load with Permissions
```
User navigates to page
        ↓
+page.js: requireRoleLevel('manager')
        ↓
User role checked (stored in cookie/localStorage)
        ↓
Role insufficient → Redirect to /unauthorized
        ↓
Role sufficient → Load page data
        ↓
+page.svelte renders with RoleGuard/PermissionButton
        ↓
Components check permissions again (defense in depth)
        ↓
Final UI rendered with appropriate controls
```

### Tenant Switching (Admin)
```
Admin selects tenant from TenantSelector
        ↓
onChange(tenantId) callback
        ↓
Update selectedTenant state
        ↓
Call invalidateAll() or reload data
        ↓
+page.js re-runs with new tenant context
        ↓
API calls include ?tenant=X
        ↓
Backend filters data by selected tenant
        ↓
UI re-renders with tenant-filtered data
```

---

## 🧪 Testing Checklist

### Role-Based Access
- [ ] Super Admin can access all pages
- [ ] Admin can access all pages except superuser-only features
- [ ] Manager can access products, orders, customers, promotions
- [ ] Cashier can access products, orders (read-only for most)
- [ ] Kitchen can only access orders with status updates

### Permission-Based UI
- [ ] Create buttons hidden for users without create permission
- [ ] Delete buttons hidden for users without delete permission
- [ ] Edit buttons visible to users with update permission
- [ ] Tenant selector visible only to admin users

### Route Protection
- [ ] Accessing /users as manager redirects to /unauthorized
- [ ] Accessing /products as kitchen staff redirects to /unauthorized
- [ ] Accessing /orders as cashier succeeds
- [ ] Unauthenticated access redirects to /login with return URL

### Tenant Filtering
- [ ] Admin can switch tenants and see filtered data
- [ ] Regular users see only their tenant's data
- [ ] "All Tenants" option works for admin
- [ ] Query params include ?tenant=X for admin

---

## 📊 Implementation Coverage

| Component | Status | File |
|-----------|--------|------|
| Auth Store Enhancement | ✅ Complete | admin/src/lib/stores/auth.js |
| RoleGuard Component | ✅ Complete | admin/src/lib/components/RoleGuard.svelte |
| PermissionButton | ✅ Complete | admin/src/lib/components/PermissionButton.svelte |
| TenantSelector | ✅ Complete | admin/src/lib/components/TenantSelector.svelte |
| Route Guards | ✅ Complete | admin/src/lib/utils/routeGuard.js |
| Unauthorized Page | ✅ Complete | admin/src/routes/unauthorized/+page.svelte |
| Layout Updates | ✅ Complete | admin/src/routes/+layout.svelte |
| Example Implementation | ✅ Complete | EXAMPLE_PAGE_*.md |

---

## 📝 Migration Guide for Existing Pages

### Step 1: Add Route Protection
```javascript
// Before
export async function load(event) {
  const response = await event.fetch('/api/admin/products/');
  return await response.json();
}

// After
import { requireRoleLevel } from '$lib/utils/routeGuard';

export async function load(event) {
  const user = requireRoleLevel(event, 'manager');
  const response = await event.fetch('/api/admin/products/');
  return { products: await response.json(), user };
}
```

### Step 2: Wrap Sensitive UI Elements
```svelte
<!-- Before -->
<button on:click={handleDelete}>Delete</button>

<!-- After -->
<RoleGuard action="delete" resource="products">
  <button on:click={handleDelete}>Delete</button>
</RoleGuard>
```

### Step 3: Use Permission Buttons
```svelte
<!-- Before -->
<button on:click={handleCreate}>Add Product</button>

<!-- After -->
<PermissionButton action="create" resource="products" on:click={handleCreate}>
  Add Product
</PermissionButton>
```

---

## 🚀 Next Steps (Phase 3)

Phase 2 provides the foundation. Next phase should:

1. **Apply to All Pages**: Update products, orders, customers, promotions, users, tenants pages
2. **Audit Logging**: Track who accessed what, when
3. **Permission Management UI**: Allow admins to customize role permissions
4. **Tenant Isolation Testing**: Ensure no data leakage between tenants
5. **Performance Optimization**: Cache permission checks, optimize role queries

---

## 📚 Related Documentation

- [PHASE1_RBAC.md](./PHASE1_RBAC.md) - Backend Foundation
- [EXAMPLE_PAGE_JS.md](../admin/EXAMPLE_PAGE_JS.md) - Route protection example
- [EXAMPLE_PAGE_SVELTE.md](../admin/EXAMPLE_PAGE_SVELTE.md) - Component usage example

---

## ✅ Completion Criteria

All Phase 2 objectives completed:

- [x] Enhanced auth store with role helpers
- [x] Created RoleGuard component
- [x] Created PermissionButton component
- [x] Created TenantSelector component
- [x] Implemented route protection utilities
- [x] Updated root layout with role-based navigation
- [x] Created unauthorized access page
- [x] Provided implementation examples
- [x] Documented all patterns and usage

**Phase 2 Status: COMPLETE ✅**

Ready to proceed with Phase 3: Apply RBAC to all admin pages.

---

## 🚀 Extension: Multi-Outlet Support

**Phase 2 frontend components will be enhanced for multi-outlet:**

- **OutletSelector Component:** Similar to TenantSelector, allows switching outlets
- **Enhanced Auth Store:** Tracks current_outlet in auth state
- **Outlet Context:** Frontend reads X-Outlet-ID from localStorage
- **Permission Guards:** Extended to check outlet access

See [MULTI_OUTLET_ROADMAP.md](../MULTI_OUTLET_ROADMAP.md) for complete implementation details.
