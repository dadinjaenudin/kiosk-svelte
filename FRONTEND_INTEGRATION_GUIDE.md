# Frontend Integration Guide - Tenant Selector

## Changes to `frontend/src/routes/kiosk/+page.svelte`

### 1. Add Imports (Top of <script>)

```javascript
import TenantSelector from '$lib/components/TenantSelector.svelte';
import OutletSelector from '$lib/components/OutletSelector.svelte';
```

### 2. Add State Variables (After existing state)

```javascript
// Tenant/Outlet selection state
let tenants = [];
let selectedTenant = null;
let selectedOutlet = null;
let outlets = [];
let showTenantSelector = true;
let showOutletSelector = false;
let tenantLoading = false;
```

### 3. Add Functions (After existing functions)

```javascript
/**
 * Load tenants from API
 */
async function loadTenants() {
	try {
		tenantLoading = true;
		const response = await fetch(`${apiUrl}/public/tenants/`);
		
		if (response.ok) {
			const data = await response.json();
			tenants = data.results || data || [];
			console.log('Tenants loaded:', tenants.length);
			
			// Try to restore saved tenant
			if (browser) {
				const savedTenantId = localStorage.getItem('kiosk_tenant_id');
				if (savedTenantId && tenants.length > 0) {
					const tenant = tenants.find(t => t.id == savedTenantId);
					if (tenant) {
						await handleTenantSelect(tenant);
						return;
					}
				}
			}
			
			// Auto-select if only one tenant
			if (tenants.length === 1) {
				await handleTenantSelect(tenants[0]);
			}
		} else {
			console.error('Failed to load tenants:', response.status);
		}
	} catch (err) {
		console.error('Error loading tenants:', err);
	} finally {
		tenantLoading = false;
	}
}

/**
 * Handle tenant selection
 */
async function handleTenantSelect(tenant) {
	selectedTenant = tenant;
	showTenantSelector = false;
	
	// Save to localStorage
	if (browser) {
		localStorage.setItem('kiosk_tenant_id', tenant.id);
	}
	
	// Load outlets for this tenant
	await loadOutlets(tenant.id);
}

/**
 * Load outlets for selected tenant
 */
async function loadOutlets(tenantId) {
	try {
		tenantLoading = true;
		const response = await fetch(`${apiUrl}/public/tenants/${tenantId}/outlets/`);
		
		if (response.ok) {
			outlets = await response.json();
			console.log('Outlets loaded:', outlets.length);
			
			// Try to restore saved outlet
			if (browser) {
				const savedOutletId = localStorage.getItem('kiosk_outlet_id');
				if (savedOutletId && outlets.length > 0) {
					const outlet = outlets.find(o => o.id == savedOutletId);
					if (outlet) {
						handleOutletSelect(outlet);
						return;
					}
				}
			}
			
			// Auto-select if only one outlet
			if (outlets.length === 1) {
				handleOutletSelect(outlets[0]);
			} else if (outlets.length > 1) {
				showOutletSelector = true;
			} else {
				// No outlets, proceed anyway
				await loadKioskData();
			}
		} else {
			console.error('Failed to load outlets:', response.status);
			// Proceed anyway
			await loadKioskData();
		}
	} catch (err) {
		console.error('Error loading outlets:', err);
		// Proceed anyway
		await loadKioskData();
	} finally {
		tenantLoading = false;
	}
}

/**
 * Handle outlet selection
 */
async function handleOutletSelect(outlet) {
	selectedOutlet = outlet;
	showOutletSelector = false;
	
	// Save to localStorage
	if (browser) {
		localStorage.setItem('kiosk_outlet_id', outlet.id);
	}
	
	// Load kiosk data
	await loadKioskData();
}

/**
 * Handle back from outlet selector
 */
function handleOutletBack() {
	showOutletSelector = false;
	showTenantSelector = true;
	selectedTenant = null;
	outlets = [];
}

/**
 * Change location (reset tenant/outlet)
 */
function changeLocation() {
	selectedTenant = null;
	selectedOutlet = null;
	outlets = [];
	showTenantSelector = true;
	showOutletSelector = false;
	
	if (browser) {
		localStorage.removeItem('kiosk_tenant_id');
		localStorage.removeItem('kiosk_outlet_id');
	}
}
```

### 4. Update syncWithServer Function

Add headers to API calls:

```javascript
async function syncWithServer() {
	try {
		console.log('Syncing with server...');
		
		// Build headers with tenant/outlet context
		const headers = {};
		if (selectedTenant) {
			headers['X-Tenant-ID'] = selectedTenant.id;
		}
		if (selectedOutlet) {
			headers['X-Outlet-ID'] = selectedOutlet.id;
		}
		
		// Fetch categories
		const categoriesRes = await fetch(`${apiUrl}/products/categories/`, { headers });
		
		// ... rest of existing code
	} catch (err) {
		console.error('Error syncing with server:', err);
	}
}
```

### 5. Update onMount

```javascript
onMount(async () => {
	if (browser) {
		// Load tenants first
		await loadTenants();
		
		// Rest of existing onMount code...
		window.addEventListener('online', handleOnline);
		window.addEventListener('offline', handleOffline);
		window.addEventListener('keydown', handleKeyboard);
		
		return () => {
			window.removeEventListener('online', handleOnline);
			window.removeEventListener('offline', handleOffline);
			window.removeEventListener('keydown', handleKeyboard);
		};
	}
});
```

### 6. Update Template (Replace existing template structure)

```svelte
<!-- Show Tenant Selector -->
{#if showTenantSelector}
	<TenantSelector 
		{tenants} 
		loading={tenantLoading}
		on:select={(e) => handleTenantSelect(e.detail)}
	/>

<!-- Show Outlet Selector -->
{:else if showOutletSelector}
	<OutletSelector 
		tenant={selectedTenant}
		{outlets}
		loading={tenantLoading}
		on:select={(e) => handleOutletSelect(e.detail)}
		on:back={handleOutletBack}
	/>

<!-- Show Main Kiosk (existing UI) -->
{:else}
	<div class="kiosk-container">
		<!-- Add header with tenant/outlet info and change button -->
		<div class="kiosk-header">
			<div class="header-content">
				<div class="location-info">
					<h1>{selectedTenant?.name || 'Kiosk'}</h1>
					{#if selectedOutlet}
						<p class="outlet-name">📍 {selectedOutlet.name}</p>
					{/if}
				</div>
				<button class="change-location-btn" on:click={changeLocation}>
					🔄 Change Location
				</button>
			</div>
		</div>
		
		<!-- Rest of existing kiosk UI (categories, products, cart, etc.) -->
		<!-- Keep all existing HTML -->
	</div>
{/if}
```

### 7. Add CSS for Header

```css
.kiosk-header {
	background: white;
	border-bottom: 1px solid #e2e8f0;
	padding: 1rem 2rem;
	box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.header-content {
	max-width: 1400px;
	margin: 0 auto;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.location-info h1 {
	font-size: 1.5rem;
	font-weight: 700;
	color: #1a202c;
	margin-bottom: 0.25rem;
}

.outlet-name {
	color: #718096;
	font-size: 0.875rem;
}

.change-location-btn {
	padding: 0.75rem 1.5rem;
	border-radius: 0.75rem;
	border: 2px solid #e2e8f0;
	background: white;
	cursor: pointer;
	font-size: 0.875rem;
	font-weight: 600;
	color: #4a5568;
	transition: all 0.2s;
}

.change-location-btn:hover {
	border-color: #667eea;
	color: #667eea;
	background: #f7fafc;
}
```

---

## Summary of Changes

1. ✅ Import TenantSelector and OutletSelector components
2. ✅ Add tenant/outlet state variables
3. ✅ Add loadTenants(), handleTenantSelect(), loadOutlets(), handleOutletSelect() functions
4. ✅ Update syncWithServer() to send X-Tenant-ID and X-Outlet-ID headers
5. ✅ Update onMount() to load tenants first
6. ✅ Add conditional rendering for tenant selector, outlet selector, and main kiosk
7. ✅ Add header with tenant info and "Change Location" button
8. ✅ Add CSS for new header

---

## Testing

After implementing:

1. **First Load**: Should show tenant selector
2. **Select Tenant**: Should show outlet selector (if multiple outlets)
3. **Select Outlet**: Should show kiosk with filtered products
4. **Reload Page**: Should restore saved tenant/outlet
5. **Change Location**: Should reset to tenant selector

---

## Alternative: Quick Test Script

If you want to test backend first:

```bash
# Test tenant API
curl http://localhost:8001/api/public/tenants/

# Test outlets API
curl http://localhost:8001/api/public/tenants/1/outlets/

# Test products with tenant filter
curl -H "X-Tenant-ID: 1" http://localhost:8001/api/products/products/
```

---

Would you like me to:
1. Create a complete new kiosk page file with all changes?
2. Or just deploy backend first and test the API?
