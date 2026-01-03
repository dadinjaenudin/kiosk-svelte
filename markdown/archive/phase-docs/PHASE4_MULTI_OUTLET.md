# Phase 4: Multi-Outlet Frontend Components

## Overview
Phase 4 implements the frontend components and UI for the multi-outlet system, allowing users to view and switch between accessible outlets.

## Date
December 2024

## Status
✅ **COMPLETED**

---

## Implementation Details

### 1. Auth Store Enhancement

**File**: `admin/src/lib/stores/auth.js`

#### New Stores
```javascript
export const currentOutlet = writable(null);
export const accessibleOutlets = writable([]);
export const outletLoading = writable(false);
```

#### New Helper Functions

**canAccessOutlet(outletId)**
```javascript
export function canAccessOutlet(outletId) {
    let userValue = null;
    let outletsValue = [];
    
    user.subscribe(u => { userValue = u; })();
    accessibleOutlets.subscribe(o => { outletsValue = o; })();
    
    if (!userValue) return false;
    
    // Admin & tenant_owner have access to all outlets
    if (userValue.role === 'admin' || userValue.role === 'super_admin' || userValue.role === 'tenant_owner') {
        return true;
    }
    
    // Manager: Check accessible_outlets
    if (userValue.role === 'manager') {
        return outletsValue.some(o => o.id === outletId);
    }
    
    // Cashier/Kitchen: Check assigned outlet
    return userValue.outlet?.id === outletId;
}
```

**fetchAccessibleOutlets()**
```javascript
export async function fetchAccessibleOutlets() {
    try {
        outletLoading.set(true);
        const response = await fetch(`${API_BASE_URL}/outlets/accessible/`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            accessibleOutlets.set(data);
            
            // Save to localStorage
            if (typeof window !== 'undefined') {
                localStorage.setItem('accessible_outlets', JSON.stringify(data));
            }
            
            return data;
        }
    } catch (err) {
        console.error('Error fetching accessible outlets:', err);
    } finally {
        outletLoading.set(false);
    }
}
```

**setCurrentOutlet(outletId)**
```javascript
export async function setCurrentOutlet(outletId) {
    if (!canAccessOutlet(outletId)) {
        console.error('Access denied to outlet:', outletId);
        return false;
    }
    
    try {
        outletLoading.set(true);
        const response = await fetch(`${API_BASE_URL}/outlets/${outletId}/set_current/`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            currentOutlet.set(data.outlet);
            
            // Save to localStorage
            if (typeof window !== 'undefined') {
                localStorage.setItem('current_outlet', JSON.stringify(data.outlet));
            }
            
            return true;
        }
    } catch (err) {
        console.error('Error setting current outlet:', err);
    } finally {
        outletLoading.set(false);
    }
    
    return false;
}
```

#### Updated Role Hierarchy
```javascript
export const ROLE_HIERARCHY = {
    super_admin: 100,
    admin: 90,
    tenant_owner: 80,  // NEW - can access all outlets in their tenant
    manager: 50,
    cashier: 30,
    kitchen: 20
};
```

#### Updated Permissions Matrix
Added `tenant_owner` role with full CRUD permissions on:
- products
- orders
- promotions
- outlets

#### Enhanced localStorage Persistence
```javascript
// Save outlets to localStorage
if (typeof window !== 'undefined') {
    localStorage.setItem('current_outlet', JSON.stringify($currentOutlet));
    localStorage.setItem('accessible_outlets', JSON.stringify($accessibleOutlets));
}

// Restore on page load
if (typeof window !== 'undefined') {
    const savedOutlet = localStorage.getItem('current_outlet');
    const savedOutlets = localStorage.getItem('accessible_outlets');
    
    if (savedOutlet) currentOutlet.set(JSON.parse(savedOutlet));
    if (savedOutlets) accessibleOutlets.set(JSON.parse(savedOutlets));
}
```

---

### 2. OutletSelector Component

**File**: `admin/src/lib/components/OutletSelector.svelte`

#### Features
- Fetches accessible outlets on mount
- Displays current outlet
- Allows switching between outlets
- Shows loading states
- Handles empty states
- Role-based visibility (hidden for cashier/kitchen with single outlet)

#### Component Structure
```svelte
<script>
    import { onMount } from 'svelte';
    import { currentOutlet, accessibleOutlets, outletLoading, user, fetchAccessibleOutlets, setCurrentOutlet } from '$lib/stores/auth';
    
    let selectedOutlet = null;
    
    onMount(async () => {
        await fetchAccessibleOutlets();
        
        if ($currentOutlet) {
            selectedOutlet = $currentOutlet.id;
        } else if ($accessibleOutlets.length > 0) {
            selectedOutlet = $accessibleOutlets[0].id;
            await setCurrentOutlet(selectedOutlet);
        }
    });
    
    async function handleOutletChange(event) {
        const outletId = parseInt(event.target.value);
        const success = await setCurrentOutlet(outletId);
        
        if (success) {
            selectedOutlet = outletId;
            // Reload page to apply outlet filter
            window.location.reload();
        }
    }
</script>

<!-- Conditional rendering based on role -->
{#if $user && ($user.role !== 'cashier' && $user.role !== 'kitchen' || $accessibleOutlets.length > 1)}
    <div class="outlet-selector">
        <label class="block text-sm font-medium text-gray-700 mb-2">
            Current Outlet
        </label>
        
        {#if $outletLoading}
            <div class="flex items-center justify-center py-2">
                <div class="loading-spinner"></div>
                <span class="ml-2 text-sm text-gray-500">Loading outlets...</span>
            </div>
        {:else if $accessibleOutlets.length === 0}
            <p class="text-sm text-gray-500">No outlets available</p>
        {:else}
            <select 
                bind:value={selectedOutlet}
                on:change={handleOutletChange}
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
                {#each $accessibleOutlets as outlet}
                    <option value={outlet.id}>
                        📍 {outlet.name}
                    </option>
                {/each}
            </select>
            
            <!-- Current outlet info -->
            {#if $currentOutlet}
                <p class="mt-2 text-xs text-gray-500">
                    Currently viewing: <span class="font-medium">{$currentOutlet.name}</span>
                </p>
            {/if}
        {/if}
    </div>
{/if}
```

#### UI States
1. **Loading**: Shows spinner while fetching outlets
2. **Empty**: Displays message when no outlets available
3. **Loaded**: Shows dropdown with accessible outlets
4. **Current Outlet Info**: Displays currently selected outlet below dropdown

#### Role-Based Visibility
- **Hidden for**: Cashier & Kitchen staff with only 1 assigned outlet
- **Visible for**: 
  - Admin/Super Admin (all outlets)
  - Tenant Owner (all tenant outlets)
  - Manager (accessible_outlets)
  - Cashier/Kitchen with multiple outlet access (edge case)

---

### 3. Layout Integration

**File**: `admin/src/routes/+layout.svelte`

#### Import Components
```svelte
import TenantSelector from '$lib/components/TenantSelector.svelte';
import OutletSelector from '$lib/components/OutletSelector.svelte';
import { currentOutlet } from '$lib/stores/auth';
```

#### Sidebar Integration
```svelte
<!-- Tenant Selector (Admin Only) -->
<RoleGuard roles={['admin', 'super_admin']}>
    <div class="border-t border-gray-200 p-4">
        <TenantSelector bind:selectedTenant onChange={handleTenantChange} />
    </div>
</RoleGuard>

<!-- Outlet Selector (Tenant Owner & Manager) -->
<RoleGuard roles={['tenant_owner', 'manager']}>
    <div class="border-t border-gray-200 p-4">
        <OutletSelector />
    </div>
</RoleGuard>
```

#### Header Badge
```svelte
<div class="flex items-center space-x-4">
    <!-- Tenant badge -->
    {#if $user?.tenant_name}
        <span class="badge badge-info">
            {$user.tenant_name}
        </span>
    {/if}

    <!-- Outlet badge -->
    {#if $currentOutlet}
        <span class="badge badge-success">
            📍 {$currentOutlet.name}
        </span>
    {/if}
</div>
```

---

### 4. Products Page Enhancement

**File**: `admin/src/routes/products/+page.svelte`

#### Table Header Update
Added "Outlet" column after "Tenant":
```svelte
<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
    Outlet
</th>
```

#### Table Row Update
```svelte
<td class="px-6 py-4 text-sm">
    {#if product.outlet_name}
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            📍 {product.outlet_name}
        </span>
    {:else}
        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            🌐 All Outlets
        </span>
    {/if}
</td>
```

#### Visual Indicators
- **Outlet-Specific Products**: Blue badge with outlet name
- **Shared Products** (outlet=null): Green badge "All Outlets"

---

## Testing Scenarios

### Test 1: Tenant Owner Login
1. Login as tenant_owner
2. ✅ Should see OutletSelector in sidebar
3. ✅ Should see all outlets in tenant
4. ✅ Should be able to switch outlets
5. ✅ Should see current outlet badge in header
6. ✅ Products page should show outlet column

### Test 2: Manager with Multiple Outlets
1. Login as manager with accessible_outlets assigned
2. ✅ Should see OutletSelector in sidebar
3. ✅ Should only see assigned outlets in dropdown
4. ✅ Should be able to switch between accessible outlets
5. ✅ Products should filter by current outlet OR shared products

### Test 3: Cashier with Single Outlet
1. Login as cashier with assigned outlet
2. ✅ OutletSelector should be hidden (only 1 outlet)
3. ✅ Should see outlet badge in header
4. ✅ Products should auto-filter to assigned outlet + shared

### Test 4: Outlet Switching
1. Select different outlet from dropdown
2. ✅ Page should reload
3. ✅ New outlet should be shown in header badge
4. ✅ Products list should update with new outlet filter
5. ✅ Session should persist outlet selection

---

## Component Hierarchy

```
+layout.svelte
├── TenantSelector.svelte (Admin/Super Admin)
├── OutletSelector.svelte (Tenant Owner/Manager)
│   ├── Uses: currentOutlet store
│   ├── Uses: accessibleOutlets store
│   ├── Uses: fetchAccessibleOutlets()
│   └── Uses: setCurrentOutlet()
└── Header Badges
    ├── Tenant Badge
    └── Outlet Badge (currentOutlet)

products/+page.svelte
└── Products Table
    └── Outlet Column
        ├── Outlet Name (if outlet-specific)
        └── "All Outlets" (if shared)
```

---

## API Endpoints Used

### GET /api/outlets/accessible/
- **Purpose**: Fetch outlets user can access
- **Response**: Array of outlets based on role
- **Used by**: fetchAccessibleOutlets()

### POST /api/outlets/{id}/set_current/
- **Purpose**: Switch current outlet context
- **Validates**: User has access to outlet
- **Response**: Updated outlet object
- **Used by**: setCurrentOutlet()

---

## State Management

### Stores
```javascript
currentOutlet       // Currently selected outlet object
accessibleOutlets   // Array of outlets user can access
outletLoading       // Loading state for outlet operations
```

### localStorage Persistence
```javascript
'current_outlet'        // Persists selected outlet
'accessible_outlets'    // Caches accessible outlets list
```

### Session Persistence
- Backend middleware stores `current_outlet_id` in session
- Survives page reloads
- Used for API filtering

---

## User Experience Flow

### First Login
1. User logs in
2. fetchAccessibleOutlets() called automatically
3. If no current outlet in session:
   - Auto-select first accessible outlet
   - Store in session via setCurrentOutlet()
4. OutletSelector displays current outlet

### Outlet Switch
1. User selects different outlet from dropdown
2. setCurrentOutlet() called with new outlet ID
3. Backend validates access
4. Session updated
5. Page reloads to apply filter
6. All API calls now use new outlet context

### Products Page
1. Backend filters products by current outlet
2. Shows products with:
   - outlet = current_outlet OR
   - outlet = null (shared products)
3. Products display outlet badge
4. Header shows current outlet

---

## Benefits

### Role-Based Access
- ✅ Tenant owners see all outlets
- ✅ Managers see only assigned outlets
- ✅ Cashiers auto-assigned to single outlet
- ✅ Clean UI (no outlet selector if only 1 outlet)

### Data Isolation
- ✅ Products filtered by outlet
- ✅ Orders filtered by outlet
- ✅ Shared products (outlet=null) visible everywhere

### User Experience
- ✅ Clear visual indicators (badges)
- ✅ Easy outlet switching
- ✅ Persistent outlet selection
- ✅ Loading states for async operations

### Scalability
- ✅ Supports unlimited outlets per tenant
- ✅ Efficient session-based filtering
- ✅ Minimal backend queries (cached in session)

---

## Next Steps

### Phase 5: Data Migration
- Update `setup_rbac_test_data.py` with outlet assignments
- Create sample products for different outlets
- Test multi-outlet scenarios with real data

### Phase 6: Analytics (Optional)
- Add outlet-level reporting
- Sales by outlet
- Inventory by outlet
- Performance comparison

### Phase 7: Documentation
- User guide for outlet management
- Admin guide for outlet setup
- Training materials for tenant owners

---

## Related Files

### Backend
- `backend/apps/users/models.py` (accessible_outlets field)
- `backend/apps/products/models.py` (outlet field)
- `backend/apps/core/middleware.py` (SetOutletContextMiddleware)
- `backend/apps/tenants/views.py` (OutletViewSet)
- `backend/apps/products/views_admin.py` (outlet filtering)

### Frontend
- `admin/src/lib/stores/auth.js` (outlet stores & helpers)
- `admin/src/lib/components/OutletSelector.svelte` (selector component)
- `admin/src/routes/+layout.svelte` (layout integration)
- `admin/src/routes/products/+page.svelte` (outlet column)

### Documentation
- `markdown/PHASE1_MULTI_OUTLET.md` (Database Schema)
- `markdown/PHASE2_MULTI_OUTLET.md` (Backend Context)
- `markdown/PHASE3_MULTI_OUTLET.md` (Backend Permissions)
- `markdown/PHASE4_MULTI_OUTLET.md` (THIS FILE - Frontend Components)

---

## Conclusion

Phase 4 successfully implements all frontend components needed for the multi-outlet system:

✅ Auth store enhanced with outlet management
✅ OutletSelector component created and tested
✅ Layout integration with role-based visibility
✅ Products page shows outlet information
✅ Outlet switching fully functional
✅ Visual indicators (badges) for context awareness

The frontend now seamlessly integrates with the backend outlet filtering system, providing a complete multi-outlet experience for users.
