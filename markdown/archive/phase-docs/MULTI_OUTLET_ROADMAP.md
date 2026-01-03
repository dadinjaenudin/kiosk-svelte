# Multi-Tenant Multi-Outlet System - Implementation Roadmap

**Status:** Planning Phase  
**Target:** Complete multi-tenant architecture with outlet management  
**Estimated Duration:** 4-6 weeks

---

## 📋 Overview

Transform the current single-tenant-per-user system into a robust multi-tenant, multi-outlet platform where:
- Platform supports multiple tenant brands
- Each tenant can have multiple outlets/stores
- Users can be assigned to specific outlets
- Tenant owners can manage all their outlets
- Clear data isolation and access control


✅ Benefits:
✅ Tenant isolation - Data tidak bocor antar tenant
✅ Outlet flexibility - Manager bisa handle multiple outlets
✅ Clear hierarchy - Role structure jelas
✅ Scalable - Bisa tambah tenant/outlet tanpa ubah code
✅ Audit trail - Jelas siapa akses outlet mana

Recommended Architecture:

Platform (Kiosk System)
├── Tenant 1 (Pizza Paradise - Franchise)
│   ├── Outlet A (Mall Yogya)
│   ├── Outlet B (Mall Malioboro)
│   └── Outlet C (Mall Hartono)
├── Tenant 2 (Burger Station - Franchise)
│   ├── Outlet A (Food Court 1)
│   └── Outlet B (Food Court 2)
└── Tenant 3 (Noodle House - Single Brand)
    └── Outlet A (Main Store)

tolong update juga 🎯 User Access Matrix: 

---

## 🎯 Current State vs Target State

### Current Architecture
```
User → Tenant (1:1)
Product → Tenant
Order → Tenant
```

### Target Architecture
```
User → Tenant (1:1) + accessible_outlets (M:N)
Tenant → Outlets (1:M)
Product → Outlet (outlet-specific inventory)
Order → Outlet (outlet-specific sales)
Category → Tenant (shared across outlets)
Promotion → Tenant or Outlet (can be tenant-wide or outlet-specific)
```

---

## 🗺️ Implementation Phases

---

## **Phase 1: Database Schema & Models** (Week 1)

**Status:** ✅ COMPLETED  
**Documentation:** [markdown/PHASE1_MULTI_OUTLET.md](markdown/PHASE1_MULTI_OUTLET.md)

### Completed Tasks ✅

#### ✅ 1.1 User Model Enhancement
- Added `tenant_owner` role to ROLE_CHOICES
- Added `accessible_outlets` ManyToMany field
- Updated `outlet` field with help text (primary/default outlet)

#### ✅ 1.2 Product Model Updates
- Added `outlet` ForeignKey (nullable)
- Products can be outlet-specific or shared across all outlets

#### ✅ 1.3 Order Model
- Already has `outlet` field (no changes needed)

#### ✅ 1.4 Outlet Model
- Already exists with complete structure (address, location, operating hours)

#### ✅ 1.5 Permission System
- Updated `ROLE_HIERARCHY` with `tenant_owner` (level 80)

#### ✅ 1.6 Migrations
- Created and applied:
  - `users.0004_user_accessible_outlets_alter_user_outlet_and_more`
  - `products.0004_product_outlet`

#### ✅ 1.7 Admin Interface
- Updated User admin with `accessible_outlets` horizontal filter
- Updated Product admin with outlet display and filter

### Key Features Implemented:
- ✅ Multi-outlet user access via ManyToMany relationship
- ✅ Outlet-specific products (outlet=null means all outlets)
- ✅ New `tenant_owner` role for franchise owners
- ✅ Database schema ready for outlet filtering

---

## **Phase 2: Backend Context & Middleware** (Week 2)

**Status:** ✅ COMPLETED  
**Documentation:** [markdown/PHASE2_MULTI_OUTLET.md](markdown/PHASE2_MULTI_OUTLET.md)

### Completed Tasks ✅

#### ✅ 2.1 Outlet Context Management
- Outlet context helpers already existed in `apps/core/context.py`
- Functions: `set_current_outlet()`, `get_current_outlet()`, `clear_tenant_context()`

#### ✅ 2.2 SetOutletContextMiddleware
- Created comprehensive outlet context middleware
- Priority: Query param → Session → User outlet → First accessible
- Role-based outlet access control
- Session persistence for outlet selection

#### ✅ 2.3 Middleware Configuration
- Added `SetOutletContextMiddleware` to settings.py
- Proper middleware ordering after authentication

#### ✅ 2.4 Outlet ViewSet Enhancement
- Enhanced OutletViewSet with multi-outlet support
- Added `/api/outlets/accessible/` endpoint
- Added `/api/outlets/{id}/set_current/` for switching
- Role-based CRUD permissions (tenant_owner only)

#### ✅ 2.5 User Serializer Enhancement
- Added `accessible_outlets` field to UserSerializer
- Returns outlet list based on user role
- Integrated with OutletSerializer for nested data

### Key Features Implemented:
- ✅ Automatic outlet selection based on user role
- ✅ Session-based outlet context persistence
- ✅ Query parameter override for outlet switching
- ✅ Accessible outlets API endpoint
- ✅ Set current outlet endpoint

---

## **Phase 3: Backend Permissions & Filtering** (Week 2-3)

**Status:** ✅ COMPLETED  
**Documentation:** [markdown/PHASE3_MULTI_OUTLET.md](markdown/PHASE3_MULTI_OUTLET.md)

### Completed Tasks ✅

#### ✅ 3.1 ProductViewSet Outlet Filtering
- Updated `get_queryset()` with outlet filtering
- Q objects for current outlet OR shared products (outlet=null)
- Auto-assignment of outlet in `perform_create()`

#### ✅ 3.2 OrderViewSet Outlet Filtering
- Role-based order filtering (manager, cashier, kitchen)
- Current outlet context integration
- Accessible outlets support for managers

#### ✅ 3.3 Public Checkout Enhancement
- Outlet selection via X-Outlet-ID header
- Outlet selection via outlet_id query parameter
- Fallback to first active outlet

### Key Features Implemented:
- ✅ Outlet-aware product filtering (shared + outlet-specific)
- ✅ Role-based order access control
- ✅ Automatic outlet assignment for new records
- ✅ Django check passed (no errors)

---

## **Phase 4: Frontend Components** (Week 3-4)

**Status:** 🚧 IN PROGRESS

### Objectives
- Update auth store with outlet tracking
- Create OutletSelector component
- Update API utils with outlet context
        help_text="User's primary outlet"
    )
    
    # NEW: Helper methods
    def can_access_outlet(self, outlet):
        """Check if user can access specific outlet"""
        if self.role in ['super_admin', 'admin']:
            return True
        if self.role == 'tenant_owner':
            return outlet.tenant == self.tenant
        return self.accessible_outlets.filter(id=outlet.id).exists()
    
    def get_accessible_outlets(self):
        """Get all outlets user can access"""
        if self.role in ['super_admin', 'admin']:
            return Outlet.objects.all()
        if self.role == 'tenant_owner':
            return Outlet.objects.filter(tenant=self.tenant)
        return self.accessible_outlets.all()
```

**Migration:** `0001_add_outlet_access_to_users.py`

#### 1.2 Update Role Choices
**File:** `backend/apps/users/models.py`

```python
ROLE_CHOICES = [
    ('super_admin', 'Super Admin'),
    ('admin', 'Admin'),
    ('tenant_owner', 'Tenant Owner'),  # NEW
    ('manager', 'Manager'),
    ('cashier', 'Cashier'),
    ('kitchen', 'Kitchen Staff'),
]
```

**Migration:** `0002_add_tenant_owner_role.py`

#### 1.3 Product Model Enhancement
**File:** `backend/apps/products/models.py`

```python
class Product(TenantModel):
    # Existing fields
    tenant = models.ForeignKey('tenants.Tenant', ...)
    
    # NEW: Outlet-specific products
    outlet = models.ForeignKey(
        'tenants.Outlet',
        on_delete=models.CASCADE,
        related_name='products',
        null=True,  # Null = available at all outlets
        blank=True,
        help_text="Specific outlet (null = all outlets)"
    )
    
    # Update manager to consider outlet
    objects = TenantOutletManager()  # NEW custom manager
    all_objects = models.Manager()
```

**Migration:** `0003_add_outlet_to_products.py`

#### 1.4 Order Model Enhancement
**File:** `backend/apps/orders/models.py`

```python
class Order(models.Model):
    # Existing fields
    tenant = models.ForeignKey('tenants.Tenant', ...)
    
    # NEW: Mandatory outlet field
    outlet = models.ForeignKey(
        'tenants.Outlet',
        on_delete=models.PROTECT,
        related_name='orders',
        help_text="Outlet where order was placed"
    )
    
    # NEW: Staff who processed order
    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_orders'
    )
```

**Migration:** `0004_add_outlet_to_orders.py`

#### 1.5 Promotion Enhancement
**File:** `backend/apps/promotions/models.py`

```python
class Promotion(models.Model):
    # Existing fields
    tenant = models.ForeignKey('tenants.Tenant', ...)
    
    # NEW: Outlet-specific or tenant-wide
    outlets = models.ManyToManyField(
        'tenants.Outlet',
        blank=True,
        related_name='promotions',
        help_text="Specific outlets (empty = all outlets)"
    )
    
    is_tenant_wide = models.BooleanField(
        default=True,
        help_text="Apply to all outlets in tenant"
    )
```

**Migration:** `0005_add_outlets_to_promotions.py`

#### 1.6 Custom Manager for Outlet Filtering
**File:** `backend/apps/core/managers.py`

```python
class TenantOutletManager(models.Manager):
    """Manager that filters by tenant and outlet context"""
    
    def get_queryset(self):
        from apps.core.context import get_current_tenant, get_current_outlet
        
        qs = super().get_queryset()
        tenant = get_current_tenant()
        outlet = get_current_outlet()
        
        if tenant:
            qs = qs.filter(tenant=tenant)
        
        if outlet:
            # Show products for specific outlet OR available to all outlets
            qs = qs.filter(
                models.Q(outlet=outlet) | models.Q(outlet__isnull=True)
            )
        
        return qs
```

**New File:** Create this manager

---

## **Phase 2: Backend Context & Middleware** (Week 2)

### Objectives
- Add outlet context to request handling
- Update middleware for outlet filtering
- Implement outlet selection mechanism

### Tasks

#### 2.1 Context Management
**File:** `backend/apps/core/context.py`

```python
import threading

_thread_locals = threading.local()

def set_current_tenant(tenant):
    _thread_locals.tenant = tenant

def get_current_tenant():
    return getattr(_thread_locals, 'tenant', None)

def clear_current_tenant():
    if hasattr(_thread_locals, 'tenant'):
        delattr(_thread_locals, 'tenant')

# NEW: Outlet context
def set_current_outlet(outlet):
    _thread_locals.outlet = outlet

def get_current_outlet():
    return getattr(_thread_locals, 'outlet', None)

def clear_current_outlet():
    if hasattr(_thread_locals, 'outlet'):
        delattr(_thread_locals, 'outlet')

def clear_context():
    clear_current_tenant()
    clear_current_outlet()
```

#### 2.2 Enhanced Middleware
**File:** `backend/apps/core/middleware.py`

```python
class SetTenantOutletContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        from apps.core.context import set_current_tenant, set_current_outlet, clear_context
        
        clear_context()
        
        if request.user.is_authenticated:
            # Set tenant
            tenant = self._get_tenant_for_user(request)
            if tenant:
                set_current_tenant(tenant)
            
            # Set outlet
            outlet = self._get_outlet_for_user(request)
            if outlet:
                set_current_outlet(outlet)
        
        response = self.get_response(request)
        clear_context()
        return response
    
    def _get_tenant_for_user(self, request):
        """Get tenant from query param or user's tenant"""
        user = request.user
        
        # Admin can switch tenants via ?tenant=<id>
        if user.role in ['super_admin', 'admin']:
            tenant_id = request.GET.get('tenant')
            if tenant_id:
                return Tenant.objects.filter(id=tenant_id).first()
        
        return user.tenant
    
    def _get_outlet_for_user(self, request):
        """Get outlet from query param, session, or user's default"""
        user = request.user
        
        # Check query parameter first (highest priority)
        outlet_id = request.GET.get('outlet')
        if outlet_id:
            outlet = Outlet.objects.filter(id=outlet_id).first()
            if outlet and user.can_access_outlet(outlet):
                # Store in session for persistence
                request.session['selected_outlet'] = outlet_id
                return outlet
        
        # Check session
        session_outlet_id = request.session.get('selected_outlet')
        if session_outlet_id:
            outlet = Outlet.objects.filter(id=session_outlet_id).first()
            if outlet and user.can_access_outlet(outlet):
                return outlet
        
        # Fall back to user's default outlet
        if user.default_outlet and user.can_access_outlet(user.default_outlet):
            return user.default_outlet
        
        # If no default, get first accessible outlet
        accessible = user.get_accessible_outlets().first()
        return accessible
```

---

## **Phase 3: Backend Permissions & API** (Week 2-3)

### Objectives
- Update permission classes for outlet access
- Add outlet filtering to all ViewSets
- Create outlet management endpoints

### Tasks

#### 3.1 Enhanced Permission Classes
**File:** `backend/apps/core/permissions.py`

```python
# Update role hierarchy
ROLE_HIERARCHY = {
    'super_admin': 100,
    'admin': 90,
    'tenant_owner': 80,  # NEW
    'manager': 50,
    'cashier': 30,
    'kitchen': 20
}

class CanAccessOutlet(permissions.BasePermission):
    """Check if user can access the outlet in context"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        from apps.core.context import get_current_outlet
        outlet = get_current_outlet()
        
        if not outlet:
            # No outlet context = allow (will be filtered by manager)
            return True
        
        return request.user.can_access_outlet(outlet)

class IsTenantOwner(permissions.BasePermission):
    """Check if user is tenant owner"""
    
    def has_permission(self, request, view):
        return request.user.role in ['tenant_owner', 'super_admin', 'admin']

# Update existing permission classes
class CanManageProducts(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        role_level = get_role_level(user.role)
        
        if request.method == 'GET':
            return role_level >= 30  # Cashier+
        elif request.method in ['POST', 'PUT', 'PATCH']:
            return role_level >= 50  # Manager+
        elif request.method == 'DELETE':
            return role_level >= 80  # Tenant Owner+
        
        return False
```

#### 3.2 Update ViewSets with Outlet Filtering
**File:** `backend/apps/products/views_admin.py`

```python
class ProductAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CanManageProducts, CanAccessOutlet]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role in ['super_admin', 'admin']:
            # See all products
            return Product.all_objects.all()
        
        elif user.role == 'tenant_owner':
            # See all products in their tenant
            return Product.all_objects.filter(tenant=user.tenant)
        
        else:
            # See only products in accessible outlets
            outlets = user.get_accessible_outlets()
            return Product.objects.filter(
                models.Q(outlet__in=outlets) | 
                models.Q(outlet__isnull=True, tenant=user.tenant)
            )
    
    def perform_create(self, serializer):
        user = self.request.user
        outlet = get_current_outlet()
        
        if user.role in ['super_admin', 'admin']:
            # Admin must specify outlet or tenant
            serializer.save()
        else:
            # Auto-assign to current outlet or tenant
            serializer.save(
                tenant=user.tenant,
                outlet=outlet
            )
```

#### 3.3 Outlet Management API
**File:** `backend/apps/users/views.py`

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accessible_outlets(request):
    """Get outlets accessible by current user"""
    outlets = request.user.get_accessible_outlets()
    
    serializer = OutletSerializer(outlets, many=True)
    return Response({
        'outlets': serializer.data,
        'default_outlet': OutletSerializer(request.user.default_outlet).data if request.user.default_outlet else None,
        'current_outlet': OutletSerializer(get_current_outlet()).data if get_current_outlet() else None
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_outlet(request):
    """Switch to different outlet"""
    outlet_id = request.data.get('outlet_id')
    
    try:
        outlet = Outlet.objects.get(id=outlet_id)
        
        if not request.user.can_access_outlet(outlet):
            return Response(
                {'error': 'You do not have access to this outlet'},
                status=403
            )
        
        # Store in session
        request.session['selected_outlet'] = outlet_id
        
        return Response({
            'success': True,
            'outlet': OutletSerializer(outlet).data
        })
    
    except Outlet.DoesNotExist:
        return Response({'error': 'Outlet not found'}, status=404)
```

**URLs:** Add to `backend/apps/users/urls.py`

---

## **Phase 4: Frontend Components** (Week 3-4)

### Objectives
- Create outlet selector component
- Update auth store with outlet context
- Add outlet filtering to all pages

### Tasks

#### 4.1 Enhanced Auth Store
**File:** `admin/src/lib/stores/auth.js`

```javascript
export const ROLE_HIERARCHY = {
    super_admin: 100,
    admin: 90,
    tenant_owner: 80,  // NEW
    manager: 50,
    cashier: 30,
    kitchen: 20
};

// NEW: Outlet store
export const currentOutlet = writable(null);
export const accessibleOutlets = writable([]);

// NEW: Helper functions
export async function loadAccessibleOutlets() {
    try {
        const response = await authFetch('/api/users/accessible-outlets/');
        const data = await response.json();
        
        accessibleOutlets.set(data.outlets);
        currentOutlet.set(data.current_outlet);
        
        return data;
    } catch (error) {
        console.error('Failed to load outlets:', error);
        return { outlets: [], current_outlet: null };
    }
}

export async function switchOutlet(outletId) {
    try {
        const response = await authFetch('/api/users/switch-outlet/', {
            method: 'POST',
            body: JSON.stringify({ outlet_id: outletId })
        });
        
        const data = await response.json();
        currentOutlet.set(data.outlet);
        
        // Reload page data to reflect new outlet
        goto($page.url.pathname);
        
        return data;
    } catch (error) {
        console.error('Failed to switch outlet:', error);
        throw error;
    }
}

export function canAccessOutlet(outlet) {
    const user = get(authUser);
    
    if (!user || !outlet) return false;
    
    if (user.role === 'super_admin' || user.role === 'admin') {
        return true;
    }
    
    if (user.role === 'tenant_owner') {
        return outlet.tenant === user.tenant.id;
    }
    
    const outlets = get(accessibleOutlets);
    return outlets.some(o => o.id === outlet.id);
}

export function isTenantOwner() {
    const user = get(authUser);
    return user && (user.role === 'tenant_owner' || user.role === 'super_admin' || user.role === 'admin');
}
```

#### 4.2 Outlet Selector Component
**File:** `admin/src/lib/components/OutletSelector.svelte`

```svelte
<script>
    import { onMount } from 'svelte';
    import { currentOutlet, accessibleOutlets, switchOutlet } from '$lib/stores/auth';
    
    export let showLabel = true;
    export let compact = false;
    
    let loading = false;
    let selectedId = null;
    
    $: if ($currentOutlet) {
        selectedId = $currentOutlet.id;
    }
    
    async function handleChange(event) {
        const outletId = parseInt(event.target.value);
        
        if (outletId === selectedId) return;
        
        loading = true;
        try {
            await switchOutlet(outletId);
        } catch (error) {
            alert('Failed to switch outlet');
        } finally {
            loading = false;
        }
    }
</script>

{#if $accessibleOutlets.length > 0}
    <div class="outlet-selector" class:compact>
        {#if showLabel}
            <label class="text-sm font-medium text-gray-700">
                Current Outlet
            </label>
        {/if}
        
        <select
            bind:value={selectedId}
            on:change={handleChange}
            disabled={loading || $accessibleOutlets.length === 1}
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        >
            {#each $accessibleOutlets as outlet}
                <option value={outlet.id}>
                    {outlet.name}
                    {#if outlet.address}
                        - {outlet.address}
                    {/if}
                </option>
            {/each}
        </select>
        
        {#if loading}
            <div class="text-xs text-gray-500 mt-1">
                Switching outlet...
            </div>
        {/if}
    </div>
{/if}

<style>
    .outlet-selector.compact {
        display: inline-block;
        width: auto;
    }
</style>
```

#### 4.3 Update Layout with Outlet Selector
**File:** `admin/src/routes/+layout.svelte`

```svelte
<script>
    import TenantSelector from '$lib/components/TenantSelector.svelte';
    import OutletSelector from '$lib/components/OutletSelector.svelte';
    import RoleGuard from '$lib/components/RoleGuard.svelte';
    import { user, isAdmin, loadAccessibleOutlets } from '$lib/stores/auth';
    
    onMount(async () => {
        if ($user) {
            await loadAccessibleOutlets();
        }
    });
</script>

<aside class="sidebar">
    <!-- User Info -->
    <div class="user-info">
        <p>{$user.username}</p>
        <span class="role-badge">{$user.role}</span>
    </div>
    
    <!-- Tenant Selector (Admin only) -->
    <RoleGuard roles={['admin', 'super_admin']}>
        <TenantSelector />
    </RoleGuard>
    
    <!-- Outlet Selector (Multi-outlet users) -->
    <RoleGuard roles={['tenant_owner', 'manager', 'cashier', 'kitchen']}>
        <OutletSelector />
    </RoleGuard>
    
    <!-- Navigation -->
    <nav>
        <!-- ... existing nav items ... -->
    </nav>
</aside>
```

#### 4.4 Update Route Guards
**File:** `admin/src/lib/utils/routeGuard.js`

```javascript
export function getQueryParams(event, params = {}) {
    const user = get(authUser);
    const searchParams = new URLSearchParams(params);
    
    // Add tenant filter for admin
    if (isAdminUser()) {
        const tenantId = event.url.searchParams.get('tenant');
        if (tenantId) {
            searchParams.set('tenant', tenantId);
        }
    }
    
    // NEW: Add outlet filter
    const outlet = get(currentOutlet);
    if (outlet && !isAdminUser()) {
        searchParams.set('outlet', outlet.id);
    }
    
    return searchParams;
}
```

---

## **Phase 5: Data Migration & Testing** (Week 4-5)

### Objectives
- Migrate existing data to new schema
- Update test data script
- Comprehensive testing

### Tasks

#### 5.1 Data Migration Script
**File:** `backend/migrate_to_outlet_system.py`

```python
"""
Migration script to add outlet relationships to existing data
"""
def migrate_existing_data():
    print("🔄 Migrating existing data to outlet system...")
    
    # For each tenant, ensure they have at least one outlet
    for tenant in Tenant.objects.all():
        outlets = tenant.outlets.all()
        
        if not outlets.exists():
            # Create default outlet
            outlet = Outlet.objects.create(
                name=f"{tenant.name} - Main Outlet",
                tenant=tenant,
                is_main=True
            )
            print(f"  ✓ Created default outlet for {tenant.name}")
        else:
            outlet = outlets.first()
        
        # Assign all products to default outlet
        products = Product.all_objects.filter(tenant=tenant, outlet__isnull=True)
        products.update(outlet=outlet)
        
        # Assign all orders to default outlet
        orders = Order.objects.filter(tenant=tenant, outlet__isnull=True)
        orders.update(outlet=outlet)
        
        # Assign all users to default outlet
        users = User.objects.filter(tenant=tenant)
        for user in users:
            if not user.accessible_outlets.exists():
                user.accessible_outlets.add(outlet)
                user.default_outlet = outlet
                user.save()
    
    print("✅ Migration complete!")
```

#### 5.2 Enhanced Test Data Script
**File:** `backend/setup_rbac_test_data.py`

Update to create multiple outlets per tenant:

```python
def create_outlets(tenants):
    """Create outlets for each tenant"""
    print("\n🏪 Creating outlets...")
    
    outlets = {}
    
    # Pizza Paradise - 3 outlets
    pizza_outlets = [
        ('Pizza Paradise - Yogya Mall', 'Jl. Malioboro No. 100'),
        ('Pizza Paradise - Hartono Mall', 'Jl. Ring Road Utara'),
        ('Pizza Paradise - Ambarukmo Plaza', 'Jl. Laksda Adisucipto')
    ]
    outlets['pizza'] = []
    for name, address in pizza_outlets:
        outlet = Outlet.objects.create(
            name=name,
            tenant=tenants[0],
            address=address,
            is_active=True,
            is_main=(name == pizza_outlets[0][0])
        )
        outlets['pizza'].append(outlet)
        print(f"  ✓ {outlet.name}")
    
    # Similar for burger and noodle...
    
    return outlets
```

#### 5.3 Testing Checklist

**Outlet Access Tests:**
- [ ] Super admin can see all outlets
- [ ] Admin can see all outlets
- [ ] Tenant owner can see all outlets in their tenant
- [ ] Manager can see only assigned outlets
- [ ] Cashier can see only assigned outlet
- [ ] Kitchen can see only assigned outlet

**Data Filtering Tests:**
- [ ] Products filtered by outlet correctly
- [ ] Orders filtered by outlet correctly
- [ ] Analytics per outlet accurate
- [ ] Cross-outlet data isolation

**Outlet Switching Tests:**
- [ ] Tenant owner can switch between their outlets
- [ ] Manager can switch between assigned outlets
- [ ] Data refreshes after outlet switch
- [ ] Session persists outlet selection

---

## **Phase 6: Analytics & Reporting** (Week 5-6)

### Objectives
- Add outlet-level analytics
- Create comparison reports
- Dashboard enhancements

### Tasks

#### 6.1 Outlet Analytics API
**File:** `backend/apps/analytics/views.py`

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTenantOwner])
def outlet_performance(request):
    """Get performance metrics per outlet"""
    user = request.user
    outlets = user.get_accessible_outlets()
    
    data = []
    for outlet in outlets:
        metrics = {
            'outlet': OutletSerializer(outlet).data,
            'total_orders': Order.objects.filter(outlet=outlet).count(),
            'total_revenue': Order.objects.filter(
                outlet=outlet,
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            'avg_order_value': Order.objects.filter(
                outlet=outlet,
                status='completed'
            ).aggregate(avg=Avg('total_amount'))['avg'] or 0,
            'top_products': get_top_products(outlet, limit=5)
        }
        data.append(metrics)
    
    return Response(data)
```

#### 6.2 Outlet Comparison Dashboard
**File:** `admin/src/routes/analytics/outlets/+page.svelte`

```svelte
<script>
    import { onMount } from 'svelte';
    import { isTenantOwner } from '$lib/stores/auth';
    
    let outletsData = [];
    
    async function loadData() {
        const response = await authFetch('/api/analytics/outlet-performance/');
        outletsData = await response.json();
    }
    
    onMount(loadData);
</script>

{#if $isTenantOwner}
    <div class="outlet-analytics">
        <h1>Outlet Performance Comparison</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            {#each outletsData as data}
                <div class="outlet-card">
                    <h3>{data.outlet.name}</h3>
                    <div class="metrics">
                        <div class="metric">
                            <span>Total Orders</span>
                            <strong>{data.total_orders}</strong>
                        </div>
                        <div class="metric">
                            <span>Revenue</span>
                            <strong>Rp {data.total_revenue.toLocaleString()}</strong>
                        </div>
                        <div class="metric">
                            <span>Avg Order</span>
                            <strong>Rp {data.avg_order_value.toLocaleString()}</strong>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    </div>
{/if}
```

---

## **Phase 7: Documentation & Training** (Week 6)

### Objectives
- Complete documentation
- User guides per role
- Training materials

### Tasks

#### 7.1 Documentation Files
- [ ] `MULTI_OUTLET_ARCHITECTURE.md` - System overview
- [ ] `OUTLET_MANAGEMENT_GUIDE.md` - How to manage outlets
- [ ] `TENANT_OWNER_GUIDE.md` - Guide for franchise owners
- [ ] `OUTLET_MIGRATION_GUIDE.md` - How to migrate existing data
- [ ] `API_OUTLET_ENDPOINTS.md` - API documentation

#### 7.2 User Training Materials
- [ ] Video: "Setting up your first outlet"
- [ ] Video: "Managing multiple outlets"
- [ ] Guide: "Understanding outlet-level permissions"
- [ ] FAQ: Common questions about multi-outlet

---

## 📊 Success Metrics

### Technical Metrics
- [ ] All migrations run successfully
- [ ] 100% test coverage for outlet features
- [ ] API response time < 200ms
- [ ] Zero data leakage between outlets

### Business Metrics
- [ ] Tenant owners can manage all their outlets
- [ ] Staff can only access assigned outlets
- [ ] Clear audit trail per outlet
- [ ] Analytics available per outlet

---

## 🚧 Potential Challenges

### Challenge 1: Data Migration Complexity
**Risk:** Existing data doesn't have outlet relationships  
**Solution:** Create default outlet per tenant, assign all existing data

### Challenge 2: Performance with Large Datasets
**Risk:** Queries become slow with outlet filtering  
**Solution:** Add database indexes on outlet foreign keys

### Challenge 3: Session Management
**Risk:** Outlet selection lost on page refresh  
**Solution:** Store in session and backend context

### Challenge 4: Mobile App Compatibility
**Risk:** Mobile apps need to support outlet selection  
**Solution:** Add outlet parameter to all mobile API calls

---

## 🎯 Go-Live Checklist

### Pre-Launch
- [ ] All migrations tested in staging
- [ ] Data backup created
- [ ] Rollback plan prepared
- [ ] Performance benchmarks met
- [ ] Security audit completed

### Launch Day
- [ ] Run migrations on production
- [ ] Verify data integrity
- [ ] Test critical flows
- [ ] Monitor error logs
- [ ] Support team ready

### Post-Launch
- [ ] Monitor system performance
- [ ] Gather user feedback
- [ ] Address any issues
- [ ] Create case studies
- [ ] Plan next features

---

## 📚 Related Documentation

- [RBAC_ROADMAP.md](./RBAC_ROADMAP.md) - Original RBAC implementation
- [PHASE1_RBAC.md](./markdown/PHASE1_RBAC.md) - Backend foundation
- [PHASE2_RBAC.md](./markdown/PHASE2_RBAC.md) - Frontend components
- [PHASE3_RBAC.md](./markdown/PHASE3_RBAC.md) - Page-level implementation

---

## 🤝 Team Responsibilities

### Backend Developer
- Database migrations
- API endpoints
- Permission classes
- Testing

### Frontend Developer
- UI components
- Outlet selector
- State management
- Testing

### DevOps
- Database backups
- Migration execution
- Performance monitoring
- Rollback procedures

### QA
- Test scenarios
- Data validation
- User acceptance testing
- Bug reporting

---

## 📞 Support & Questions

For questions during implementation:
1. Check this roadmap first
2. Review related documentation
3. Check migration scripts
4. Contact tech lead

---

**Ready to start implementation? Let's build a robust multi-outlet system! 🚀**
