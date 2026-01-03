# Phase 3: Backend Permissions & Filtering - Multi-Outlet Extension

**Status:** ✅ COMPLETED  
**Date:** January 1, 2026  
**Duration:** ~30 minutes

---

## 📋 Overview

Phase 3 mengintegrasikan outlet filtering ke dalam ViewSets untuk Products dan Orders. Perubahan ini memastikan:
- **Outlet-aware Product Filtering**: Products filtered by current outlet context
- **Outlet-aware Order Filtering**: Orders filtered by user's outlet access
- **Automatic Outlet Assignment**: New products/orders automatically assigned to current outlet
- **Role-based Outlet Access**: Different roles see different outlet data

---

## ✅ Completed Tasks

### 1. ProductManagementViewSet Enhancement ✅

**File:** `backend/apps/products/views_admin.py`

#### Updated `get_queryset()` Method:

```python
def get_queryset(self):
    """
    Filter products based on user role and outlet context.
    
    - Admin: All products from all tenants
    - Tenant Owner: All products in their tenant
    - Manager: Products in accessible outlets + shared products (outlet=null)
    - Others: Products in their tenant
    """
    from apps.core.context import get_current_tenant, get_current_outlet
    
    user = self.request.user
    
    if is_admin_user(user):
        # Admin sees all products from all tenants
        queryset = Product.all_objects.all()
    elif user.tenant:
        # Start with tenant-scoped products
        queryset = Product.objects.filter(tenant=user.tenant)
        
        # Apply outlet filtering based on role
        current_outlet = get_current_outlet()
        
        if current_outlet and user.role in ['manager', 'cashier', 'kitchen']:
            # Filter by current outlet OR products available at all outlets
            queryset = queryset.filter(
                models.Q(outlet=current_outlet) | models.Q(outlet__isnull=True)
            )
    else:
        queryset = Product.objects.none()
    
    return queryset.select_related('tenant', 'category', 'outlet').prefetch_related('modifiers')
```

**Key Features:**
- ✅ Admin bypass: Admins see all products across tenants
- ✅ Tenant filtering: Non-admins see only their tenant's products
- ✅ **Outlet filtering**: Managers/cashiers/kitchen see current outlet + shared products
- ✅ **Shared products**: Products with `outlet=null` visible to all outlets in tenant
- ✅ Optimized queries with `select_related` and `prefetch_related`

**Filtering Logic:**

| User Role | Products Shown |
|-----------|----------------|
| super_admin/admin | ALL products from ALL tenants |
| tenant_owner | ALL products in their tenant (all outlets) |
| manager | Current outlet products + Shared products (outlet=null) |
| cashier | Current outlet products + Shared products (outlet=null) |
| kitchen | Current outlet products + Shared products (outlet=null) |

---

#### Updated `perform_create()` Method:

```python
def perform_create(self, serializer):
    """
    Auto-assign tenant and outlet based on user role and context
    """
    from apps.core.context import get_current_tenant, get_current_outlet
    
    user = self.request.user
    
    if is_admin_user(user):
        # Admin can specify tenant and outlet in request
        serializer.save()
    elif user.tenant:
        # For tenant users, auto-assign their tenant
        current_outlet = get_current_outlet()
        
        # Auto-assign outlet if user has outlet context
        # Product without outlet = available at all outlets
        if current_outlet and user.role in ['manager', 'cashier']:
            serializer.save(tenant=user.tenant, outlet=current_outlet)
        else:
            # Tenant owner or no outlet context = available at all outlets
            serializer.save(tenant=user.tenant)
    else:
        serializer.save()
```

**Key Features:**
- ✅ Auto-assign tenant from user context
- ✅ Auto-assign outlet for managers/cashiers (outlet-specific products)
- ✅ Tenant owners create shared products (outlet=null) by default
- ✅ Admin can manually specify tenant and outlet

**Creation Logic:**

| User Role | Tenant Assignment | Outlet Assignment |
|-----------|-------------------|-------------------|
| super_admin/admin | From request | From request (optional) |
| tenant_owner | Auto: user.tenant | null (shared by default) |
| manager | Auto: user.tenant | Auto: current_outlet |
| cashier | Auto: user.tenant | Auto: current_outlet |

**Example Scenarios:**

**Scenario 1: Manager creates product in Jakarta outlet**
```python
# User: manager_jakarta
# Current outlet: Jakarta
# Result: Product created with outlet=Jakarta

POST /api/admin/products/
{
  "name": "Jakarta Special Pizza",
  "sku": "PIZZA-JKT-001",
  "price": 95000
}
# Automatically assigned:
# - tenant: Pizza Paradise (from user.tenant)
# - outlet: Jakarta (from current_outlet)
```

**Scenario 2: Tenant owner creates shared product**
```python
# User: tenant_owner
# Current outlet: None (owner has no specific outlet)
# Result: Product created with outlet=null (available at all outlets)

POST /api/admin/products/
{
  "name": "Classic Margherita",
  "sku": "PIZZA-MARG-001",
  "price": 85000
}
# Automatically assigned:
# - tenant: Pizza Paradise (from user.tenant)
# - outlet: null (available everywhere)
```

---

### 2. OrderManagementViewSet Enhancement ✅

**File:** `backend/apps/orders/views_admin.py`

#### Updated `get_queryset()` Method:

```python
def get_queryset(self):
    """
    Get orders based on user role and outlet context:
    - Admin/Superuser: all orders
    - Tenant Owner: all orders in their tenant
    - Manager: orders from accessible outlets
    - Cashier/Kitchen: orders from their assigned outlet
    """
    from apps.core.context import get_current_tenant, get_current_outlet
    
    user = self.request.user
    queryset = Order.objects.select_related('tenant', 'outlet', 'cashier').prefetch_related('items')
    
    # Filter by user role
    if is_admin_user(user):
        # Admin sees all orders
        pass
    elif user.role == 'tenant_owner':
        # Tenant owner sees only their tenant's orders
        queryset = queryset.filter(tenant=user.tenant)
    elif user.role == 'manager':
        # Manager sees orders from accessible outlets
        if user.tenant:
            queryset = queryset.filter(tenant=user.tenant)
            # Further filter by accessible outlets
            current_outlet = get_current_outlet()
            if current_outlet:
                queryset = queryset.filter(outlet=current_outlet)
            elif user.accessible_outlets.exists():
                # If no current outlet, show all accessible outlets
                queryset = queryset.filter(outlet__in=user.accessible_outlets.all())
        else:
            queryset = queryset.none()
    elif user.role in ['cashier', 'kitchen']:
        # Cashier/Kitchen see only their outlet's orders
        if user.outlet:
            queryset = queryset.filter(outlet=user.outlet)
        else:
            queryset = queryset.none()
    else:
        # Other roles see nothing
        queryset = queryset.none()
    
    # ... (existing date range, status, search filters)
    
    return queryset
```

**Key Features:**
- ✅ Admin bypass: Admins see all orders
- ✅ Tenant owner: All orders in tenant
- ✅ **Manager outlet filtering**: Orders from current outlet or all accessible outlets
- ✅ **Cashier/Kitchen**: Only their assigned outlet orders
- ✅ Session-based outlet context integration

**Filtering Logic:**

| User Role | Orders Shown | Outlet Context |
|-----------|--------------|----------------|
| super_admin/admin | ALL orders from ALL tenants | N/A |
| tenant_owner | ALL orders in their tenant | All outlets |
| manager | Orders from **current outlet** | From session/context |
| manager (no context) | Orders from **all accessible outlets** | All accessible |
| cashier | Orders from **assigned outlet only** | user.outlet |
| kitchen | Orders from **assigned outlet only** | user.outlet |

**Example Scenarios:**

**Scenario 1: Manager viewing Jakarta outlet orders**
```bash
# Manager switches to Jakarta outlet
POST /api/outlets/1/set_current/

# Then requests orders
GET /api/admin/orders/

# Result: Only orders from Jakarta outlet
# Orders with outlet_id=1
```

**Scenario 2: Cashier viewing their orders**
```bash
# Cashier assigned to Bandung outlet
GET /api/admin/orders/

# Result: Only orders from Bandung outlet (user.outlet)
# Cannot see orders from other outlets
```

**Scenario 3: Tenant owner viewing all orders**
```bash
# Tenant owner requests orders
GET /api/admin/orders/

# Result: ALL orders from ALL outlets in their tenant
# Orders from Jakarta, Bandung, Surabaya, etc.
```

---

### 3. Public Checkout Enhancement ✅

**File:** `backend/apps/orders/views.py`

#### Updated Checkout Outlet Selection:

```python
def checkout(self, request):
    """
    Multi-tenant checkout with outlet support
    """
    serializer = CheckoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Get outlet from X-Outlet-ID header or query param
    outlet_id = request.headers.get('X-Outlet-ID') or request.query_params.get('outlet_id')
    
    if outlet_id:
        try:
            outlet = Outlet.objects.get(id=outlet_id, is_active=True)
        except Outlet.DoesNotExist:
            return Response(
                {'error': f'Outlet with ID {outlet_id} not found or inactive'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        # Fallback to first outlet if no outlet specified
        outlet = Outlet.objects.filter(is_active=True).first()
    
    if not outlet:
        return Response(
            {'error': 'No outlet configured'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # ... create orders with outlet ...
```

**Key Features:**
- ✅ Outlet selection via `X-Outlet-ID` header
- ✅ Outlet selection via `outlet_id` query parameter
- ✅ Fallback to first active outlet
- ✅ Validation for inactive outlets
- ✅ Clear error messages

**Usage Examples:**

**Option 1: Header-based outlet selection**
```bash
POST /api/orders/checkout/
X-Outlet-ID: 1
Content-Type: application/json

{
  "items": [...],
  "payment_method": "cash"
}
```

**Option 2: Query parameter**
```bash
POST /api/orders/checkout/?outlet_id=1
Content-Type: application/json

{
  "items": [...],
  "payment_method": "cash"
}
```

**Option 3: Automatic fallback**
```bash
# No outlet specified
POST /api/orders/checkout/

# Uses first active outlet automatically
```

---

## 📊 Outlet Filtering Summary

### Products Filtering

**Query Logic:**
```sql
-- Admin: All products
SELECT * FROM products;

-- Tenant Owner: All in tenant
SELECT * FROM products WHERE tenant_id = :tenant_id;

-- Manager/Cashier/Kitchen: Current outlet + shared
SELECT * FROM products 
WHERE tenant_id = :tenant_id 
  AND (outlet_id = :current_outlet_id OR outlet_id IS NULL);
```

**Python Implementation:**
```python
# Shared products (outlet=null)
shared_products = Product.objects.filter(tenant=tenant, outlet__isnull=True)

# Outlet-specific products
outlet_products = Product.objects.filter(tenant=tenant, outlet=current_outlet)

# Combined (what managers/cashiers see)
visible_products = Product.objects.filter(
    tenant=tenant
).filter(
    models.Q(outlet=current_outlet) | models.Q(outlet__isnull=True)
)
```

### Orders Filtering

**Query Logic:**
```sql
-- Admin: All orders
SELECT * FROM orders;

-- Tenant Owner: All in tenant
SELECT * FROM orders WHERE tenant_id = :tenant_id;

-- Manager: Current outlet or accessible outlets
SELECT * FROM orders 
WHERE tenant_id = :tenant_id 
  AND outlet_id IN (:accessible_outlet_ids);

-- Cashier/Kitchen: Assigned outlet only
SELECT * FROM orders 
WHERE outlet_id = :user_outlet_id;
```

**Python Implementation:**
```python
# Manager with current outlet
orders = Order.objects.filter(tenant=tenant, outlet=current_outlet)

# Manager without current outlet (show all accessible)
orders = Order.objects.filter(
    tenant=tenant, 
    outlet__in=user.accessible_outlets.all()
)

# Cashier/Kitchen
orders = Order.objects.filter(outlet=user.outlet)
```

---

## 🧪 Testing

### 1. Test Product Filtering

```bash
# Login as manager
POST /api/auth/login/
{
  "username": "manager_jakarta",
  "password": "password123"
}

# Set current outlet to Jakarta
POST /api/outlets/1/set_current/

# Get products
GET /api/admin/products/

# Expected: Products with outlet_id=1 OR outlet_id=null
# Should NOT see products with outlet_id=2 (Bandung)
```

### 2. Test Order Filtering

```bash
# Login as cashier assigned to Bandung outlet
POST /api/auth/login/
{
  "username": "cashier_bandung",
  "password": "password123"
}

# Get orders
GET /api/admin/orders/

# Expected: Only orders with outlet_id=2 (Bandung)
# Should NOT see orders from Jakarta or other outlets
```

### 3. Test Product Creation

```bash
# Login as manager in Jakarta outlet
POST /api/auth/login/
{
  "username": "manager_jakarta",
  "password": "password123"
}

# Set outlet
POST /api/outlets/1/set_current/

# Create product
POST /api/admin/products/
{
  "name": "Jakarta Spicy Pizza",
  "sku": "PIZZA-JKT-SPICY-001",
  "price": 95000,
  "category": 1
}

# Expected: Product automatically created with:
# - tenant_id from user.tenant
# - outlet_id=1 (from current outlet)
```

### 4. Test Shared Product (Tenant Owner)

```bash
# Login as tenant owner
POST /api/auth/login/
{
  "username": "owner_pizza",
  "password": "password123"
}

# Create product (no outlet context)
POST /api/admin/products/
{
  "name": "Margherita Classic",
  "sku": "PIZZA-MARG-001",
  "price": 75000,
  "category": 1
}

# Expected: Product created with:
# - tenant_id from user.tenant
# - outlet_id=null (available at all outlets)
```

---

## 🔄 Integration Points

### 1. Middleware Integration

Outlet filtering relies on `SetOutletContextMiddleware` to set current outlet:

```python
# Middleware sets outlet in thread-local storage
set_current_outlet(outlet)

# ViewSets retrieve outlet for filtering
current_outlet = get_current_outlet()

# Filtering applied automatically
queryset = queryset.filter(outlet=current_outlet)
```

### 2. Session Integration

Outlet selection persists across requests via session:

```python
# User sets outlet
POST /api/outlets/1/set_current/
# Stores outlet_id in session

# Subsequent requests use session outlet
GET /api/admin/products/
# Middleware reads outlet from session
# ViewSet uses outlet for filtering
```

### 3. Context Helpers

All ViewSets use consistent context helpers:

```python
from apps.core.context import get_current_tenant, get_current_outlet

# Always available in request lifecycle
tenant = get_current_tenant()
outlet = get_current_outlet()
```

---

## 📝 Best Practices

### 1. Shared vs Outlet-Specific Products

**Use Shared Products (outlet=null) for:**
- ✅ Standard menu items available everywhere
- ✅ Brand-wide products
- ✅ Core menu offerings

**Use Outlet-Specific Products for:**
- ✅ Location-specific items (e.g., "Jakarta Special")
- ✅ Outlet-limited stock items
- ✅ Test products for specific outlets

### 2. Outlet Context Best Practices

**Always check for outlet context:**
```python
current_outlet = get_current_outlet()
if current_outlet:
    # Apply outlet filtering
    queryset = queryset.filter(outlet=current_outlet)
else:
    # Handle no outlet context (show all or error)
    pass
```

**Use Q objects for shared product inclusion:**
```python
from django.db.models import Q

queryset = queryset.filter(
    Q(outlet=current_outlet) | Q(outlet__isnull=True)
)
```

### 3. Performance Optimization

**Always use select_related for outlet:**
```python
queryset = queryset.select_related('tenant', 'outlet', 'category')
```

**Index outlet_id for faster queries:**
```python
class Product(models.Model):
    outlet = models.ForeignKey(Outlet, db_index=True, ...)
```

---

## 🔄 Next Steps: Phase 4

Backend filtering is complete! Next phase will add frontend components:

1. **OutletSelector Component**
   - Dropdown for outlet switching
   - Similar to TenantSelector
   - Shows accessible outlets only

2. **Enhanced Auth Store**
   - Track current_outlet in Svelte store
   - Include accessible_outlets from user data
   - Update API calls with outlet context

3. **Outlet Context UI**
   - Show current outlet in navbar
   - Outlet badge on product/order lists
   - Filter dropdowns for outlet selection

See [MULTI_OUTLET_ROADMAP.md](../MULTI_OUTLET_ROADMAP.md) for complete plan.

---

## 📚 Files Modified

### ViewSets:
- ✅ `backend/apps/products/views_admin.py` - Product outlet filtering and auto-assignment
- ✅ `backend/apps/orders/views_admin.py` - Order outlet filtering by role
- ✅ `backend/apps/orders/views.py` - Checkout outlet selection from header/param

### Integration:
- ✅ Uses `apps/core/context.py` - get_current_outlet(), get_current_tenant()
- ✅ Uses `apps/core/middleware.py` - SetOutletContextMiddleware
- ✅ Uses Django models.Q for OR queries

---

**Phase 3 Status: COMPLETE ✅**

Backend outlet filtering fully implemented. Products and orders now respect outlet context based on user role. Automatic outlet assignment for new records.

**Ready for Phase 4: Frontend Components**

---

**Completed By:** AI Assistant (GitHub Copilot)  
**Reviewed By:** -  
**Deployed To:** Development (localhost:8001)

---

*Last Updated: January 1, 2026*
