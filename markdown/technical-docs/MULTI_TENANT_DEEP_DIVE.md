# 🏢 Multi-Tenant Deep Dive - Implementation Details

## Table of Contents
- [Multi-Tenant Strategy](#multi-tenant-strategy)
- [Database Design](#database-design)
- [Backend Implementation](#backend-implementation)
- [Frontend Implementation](#frontend-implementation)
- [Multi-Outlet System](#multi-outlet-system)
- [Data Isolation](#data-isolation)
- [Tenant Context Management](#tenant-context-management)
- [Best Practices](#best-practices)

---

## Multi-Tenant Strategy

### Approach: Shared Database with Row-Level Isolation

Sistem ini menggunakan **shared database** approach dimana semua tenant berbagi database yang sama, tapi data di-isolate menggunakan `tenant_id` foreign key.

### Strategy Comparison

| Strategy | Pros | Cons | Our Choice |
|----------|------|------|------------|
| **Separate DB per Tenant** | Complete isolation, easier backup | High cost, maintenance overhead | ❌ |
| **Shared DB, Separate Schema** | Good isolation, moderate cost | Schema migration complexity | ❌ |
| **Shared DB, Shared Schema** | Low cost, easy scaling | Requires careful isolation | ✅ **Selected** |

### Why Shared DB?

1. **Cost Effective**: Satu database untuk semua tenant
2. **Easy Maintenance**: Single migration, single backup
3. **Scalability**: Horizontal scaling dengan read replicas
4. **Multi-Brand Support**: Perfect untuk food court scenario
5. **Cross-Tenant Reporting**: Dapat analytics across tenants

---

## Database Design

### Tenant Model

```python
# apps/tenants/models.py
class Tenant(models.Model):
    """
    Represents a restaurant brand/franchise
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)  # "Ayam Geprek Bensu"
    slug = models.SlugField(unique=True)     # "ayam-geprek-bensu"
    
    # Branding
    logo = models.ImageField(upload_to='tenants/logos/')
    primary_color = models.CharField(max_length=7, default='#FF6B35')
    secondary_color = models.CharField(max_length=7, default='#F7931E')
    
    # Business settings
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    service_charge_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['name']
```

### Outlet Model (Multi-Location)

```python
class Outlet(models.Model):
    """
    Physical store location for a tenant
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='outlets')
    
    name = models.CharField(max_length=200)  # "Mall Tunjungan Plaza"
    code = models.CharField(max_length=20)   # "TP-001"
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    
    # Contact
    phone = models.CharField(max_length=20)
    manager = models.CharField(max_length=200, blank=True)
    
    # Operational
    is_active = models.BooleanField(default=True)
    operating_hours = models.JSONField(default=dict)  # {mon: "08:00-22:00", ...}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'outlets'
        unique_together = ['tenant', 'code']
```

### Tenant-Aware Models

**Base Model untuk Multi-Tenant**:

```python
# apps/core/models.py
from django.db import models

class TenantModel(models.Model):
    """
    Abstract base model for tenant-aware models
    Automatically filters by current tenant
    """
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        # Validate tenant before saving
        if hasattr(self, 'tenant') and not self.tenant:
            from apps.core.context import get_current_tenant
            tenant = get_current_tenant()
            if tenant:
                self.tenant = tenant
        super().save(*args, **kwargs)
```

**Example: Product Model**:

```python
# apps/products/models.py
class Product(TenantModel):
    """
    Product with tenant and optional outlet isolation
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    outlet = models.ForeignKey(
        Outlet, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text='If set, product only available at this outlet'
    )
    
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # ... other fields
```

### Database Tables with tenant_id

```sql
-- All major tables have tenant_id
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES tenants(id),
    outlet_id INT REFERENCES outlets(id),  -- Optional
    name VARCHAR(200),
    price DECIMAL(10,2),
    -- ...
    INDEX idx_tenant_outlet (tenant_id, outlet_id)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES tenants(id),
    outlet_id INT NOT NULL REFERENCES outlets(id),
    order_number VARCHAR(50) UNIQUE,
    -- ...
    INDEX idx_tenant_orders (tenant_id, created_at DESC)
);

CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE,
    tenant_id INT REFERENCES tenants(id),
    outlet_id INT REFERENCES outlets(id),
    role VARCHAR(20),
    -- ...
);
```

---

## Backend Implementation

### Middleware: Tenant Extraction

```python
# apps/tenants/middleware.py
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from apps.tenants.models import Tenant, Outlet
from apps.core.context import set_current_tenant, set_current_outlet, clear_tenant_context

logger = logging.getLogger(__name__)

class TenantMiddleware(MiddlewareMixin):
    """
    Extract tenant & outlet from request headers
    """
    
    # URLs that don't require tenant context
    EXCLUDE_URLS = [
        '/api/auth/login/',
        '/api/auth/register/',
        '/api/health/',
        '/admin/',
    ]
    
    def process_request(self, request):
        # Skip for excluded URLs
        if any(request.path.startswith(url) for url in self.EXCLUDE_URLS):
            return None
        
        # Extract from headers
        tenant_id = request.headers.get('X-Tenant-ID')
        outlet_id = request.headers.get('X-Outlet-ID')
        
        # Validate and set tenant
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
                set_current_tenant(tenant)
                logger.debug(f"Tenant set: {tenant.name} (ID: {tenant.id})")
            except Tenant.DoesNotExist:
                logger.warning(f"Invalid tenant ID: {tenant_id}")
                return JsonResponse({
                    'error': 'Invalid tenant',
                    'detail': f'Tenant {tenant_id} not found or inactive'
                }, status=400)
        
        # Validate and set outlet
        if outlet_id:
            try:
                outlet = Outlet.objects.get(id=outlet_id, is_active=True)
                
                # Verify outlet belongs to tenant
                if tenant_id and outlet.tenant_id != int(tenant_id):
                    logger.warning(f"Outlet {outlet_id} doesn't belong to tenant {tenant_id}")
                    return JsonResponse({
                        'error': 'Invalid outlet',
                        'detail': 'Outlet does not belong to specified tenant'
                    }, status=400)
                
                set_current_outlet(outlet)
                logger.debug(f"Outlet set: {outlet.name} (ID: {outlet.id})")
            except Outlet.DoesNotExist:
                logger.warning(f"Invalid outlet ID: {outlet_id}")
                return JsonResponse({
                    'error': 'Invalid outlet',
                    'detail': f'Outlet {outlet_id} not found or inactive'
                }, status=400)
        
        return None
    
    def process_response(self, request, response):
        # Clear context after request
        clear_tenant_context()
        return response
```

### Thread-Local Context Storage

```python
# apps/core/context.py
import threading

# Thread-local storage for request-scoped tenant/outlet context
_thread_locals = threading.local()

def set_current_tenant(tenant):
    """Set current tenant for this request thread"""
    _thread_locals.tenant = tenant

def get_current_tenant():
    """Get current tenant for this request thread"""
    return getattr(_thread_locals, 'tenant', None)

def set_current_outlet(outlet):
    """Set current outlet for this request thread"""
    _thread_locals.outlet = outlet

def get_current_outlet():
    """Get current outlet for this request thread"""
    return getattr(_thread_locals, 'outlet', None)

def clear_tenant_context():
    """Clear tenant context after request"""
    _thread_locals.tenant = None
    _thread_locals.outlet = None

def get_tenant_id():
    """Get current tenant ID or None"""
    tenant = get_current_tenant()
    return tenant.id if tenant else None

def get_outlet_id():
    """Get current outlet ID or None"""
    outlet = get_current_outlet()
    return outlet.id if outlet else None
```

### Auto-Filtering QuerySets

```python
# apps/products/views.py
from rest_framework import viewsets
from apps.core.context import get_current_tenant, get_current_outlet
from apps.products.models import Product
from apps.products.serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    Product API with automatic tenant filtering
    """
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        # Base queryset
        qs = Product.objects.all()
        
        # Filter by tenant (required)
        tenant = get_current_tenant()
        if tenant:
            qs = qs.filter(tenant=tenant)
        else:
            # No tenant context - return empty
            return Product.objects.none()
        
        # Filter by outlet (optional)
        outlet = get_current_outlet()
        if outlet:
            # Include outlet-specific + shared products
            qs = qs.filter(
                models.Q(outlet=outlet) | 
                models.Q(outlet__isnull=True)
            )
        
        # Only active products
        qs = qs.filter(is_active=True, is_available=True)
        
        return qs
    
    def perform_create(self, serializer):
        """Auto-set tenant when creating"""
        tenant = get_current_tenant()
        outlet = get_current_outlet()
        
        serializer.save(
            tenant=tenant,
            outlet=outlet if outlet else None
        )
```

### User-Based Tenant Context (Admin)

```python
# apps/core/middleware.py
class SetTenantContextMiddleware:
    """
    Set tenant context based on authenticated user
    Used for admin panel where user belongs to a tenant
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user = request.user
        
        # If user is authenticated and has tenant
        if user.is_authenticated and hasattr(user, 'tenant') and user.tenant:
            from apps.core.context import set_current_tenant
            set_current_tenant(user.tenant)
            
            # Also set outlet if user has default outlet
            if user.outlet:
                from apps.core.context import set_current_outlet
                set_current_outlet(user.outlet)
        
        response = self.get_response(request)
        
        # Clear after request
        from apps.core.context import clear_tenant_context
        clear_tenant_context()
        
        return response
```

---

## Frontend Implementation

### Tenant Selection (Kiosk)

```svelte
<!-- routes/+page.svelte - Tenant selection -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { apiClient } from '$api/client.js';
  
  let tenants = [];
  let loading = true;
  
  onMount(async () => {
    try {
      // Fetch all active tenants (public endpoint)
      const response = await apiClient.get('/api/public/tenants/');
      tenants = response.data;
    } catch (error) {
      console.error('Failed to load tenants:', error);
    } finally {
      loading = false;
    }
  });
  
  function selectTenant(tenant) {
    // Save tenant to localStorage
    localStorage.setItem('tenant_id', tenant.id);
    localStorage.setItem('tenant_name', tenant.name);
    localStorage.setItem('tenant_color', tenant.primary_color);
    
    // Navigate to kiosk with tenant context
    goto('/kiosk');
  }
</script>

<div class="tenant-selection">
  <h1>Select Restaurant</h1>
  
  {#if loading}
    <p>Loading...</p>
  {:else}
    <div class="grid">
      {#each tenants as tenant}
        <button 
          class="tenant-card"
          style="border-color: {tenant.primary_color}"
          on:click={() => selectTenant(tenant)}
        >
          <img src={tenant.logo} alt={tenant.name} />
          <h2>{tenant.name}</h2>
          <p>{tenant.description}</p>
        </button>
      {/each}
    </div>
  {/if}
</div>
```

### API Client with Tenant Headers

```javascript
// lib/api/client.js
export class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    // Add tenant context from localStorage
    const tenantId = localStorage.getItem('tenant_id');
    const outletId = localStorage.getItem('outlet_id');
    
    if (tenantId) {
      headers['X-Tenant-ID'] = tenantId;
    }
    
    if (outletId) {
      headers['X-Outlet-ID'] = outletId;
    }
    
    // Add auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    return await response.json();
  }
}
```

### Tenant-Scoped IndexedDB

```javascript
// lib/db/index.js
import Dexie from 'dexie';

export class TenantDatabase {
  constructor(tenantId) {
    this.tenantId = tenantId;
    this.db = new Dexie(`POS_Tenant_${tenantId}`);
    
    this.db.version(1).stores({
      products: '++id, sku, name, category_id, price',
      cart: '++id, product_id, quantity, created_at',
      orders: '++id, order_number, status, total, created_at'
    });
  }
  
  async getProducts(categoryId = null) {
    if (categoryId) {
      return await this.db.products
        .where('category_id')
        .equals(categoryId)
        .toArray();
    }
    return await this.db.products.toArray();
  }
  
  // ... other methods
}

// Singleton instance per tenant
let currentDB = null;

export function getTenantDB() {
  const tenantId = localStorage.getItem('tenant_id');
  
  if (!tenantId) {
    throw new Error('No tenant context set');
  }
  
  if (!currentDB || currentDB.tenantId !== tenantId) {
    currentDB = new TenantDatabase(tenantId);
  }
  
  return currentDB;
}

// Convenience exports
export async function getProducts(categoryId) {
  return await getTenantDB().getProducts(categoryId);
}

export async function addToCart(product, quantity) {
  return await getTenantDB().addToCart(product, quantity);
}
```

---

## Multi-Outlet System

### Outlet Selection for Staff

```svelte
<!-- lib/components/OutletSelector.svelte -->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$api/client.js';
  import { currentOutlet } from '$stores/settings.js';
  
  let outlets = [];
  let loading = true;
  
  onMount(async () => {
    // Fetch accessible outlets for current user
    const response = await apiClient.get('/api/outlets/accessible/');
    outlets = response.data;
    
    // Set default outlet if saved
    const savedOutletId = localStorage.getItem('outlet_id');
    if (savedOutletId) {
      const outlet = outlets.find(o => o.id === parseInt(savedOutletId));
      if (outlet) {
        currentOutlet.set(outlet);
      }
    }
    
    loading = false;
  });
  
  function selectOutlet(outlet) {
    currentOutlet.set(outlet);
    localStorage.setItem('outlet_id', outlet.id);
    localStorage.setItem('outlet_name', outlet.name);
  }
</script>

{#if !loading}
  <select on:change={(e) => {
    const outlet = outlets.find(o => o.id === parseInt(e.target.value));
    selectOutlet(outlet);
  }}>
    <option value="">Select Outlet</option>
    {#each outlets as outlet}
      <option value={outlet.id}>{outlet.name}</option>
    {/each}
  </select>
{/if}
```

### Outlet-Specific Products

```python
# Backend: Filter products by outlet
class ProductViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        tenant = get_current_tenant()
        outlet = get_current_outlet()
        
        qs = Product.objects.filter(tenant=tenant, is_active=True)
        
        if outlet:
            # Products specific to outlet OR shared (outlet=null)
            qs = qs.filter(
                models.Q(outlet=outlet) | 
                models.Q(outlet__isnull=True)
            )
        
        return qs
```

---

## Data Isolation

### Validation Checks

```python
# apps/core/permissions.py
from rest_framework import permissions
from apps.core.context import get_current_tenant

class IsSameTenant(permissions.BasePermission):
    """
    Ensure object belongs to current tenant
    """
    def has_object_permission(self, request, view, obj):
        tenant = get_current_tenant()
        
        # Object must have tenant attribute
        if not hasattr(obj, 'tenant'):
            return False
        
        # Must match current tenant
        return obj.tenant == tenant

# Usage in ViewSet
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSameTenant]
```

### Database Constraints

```sql
-- Foreign key constraints ensure referential integrity
ALTER TABLE orders 
    ADD CONSTRAINT fk_orders_tenant 
    FOREIGN KEY (tenant_id) REFERENCES tenants(id);

-- Check constraint (optional paranoid mode)
ALTER TABLE orders 
    ADD CONSTRAINT check_tenant_outlet 
    CHECK (
        outlet_id IN (
            SELECT id FROM outlets WHERE tenant_id = orders.tenant_id
        )
    );
```

### Query Auditing

```python
# apps/core/middleware.py
class QueryAuditMiddleware:
    """
    Log all queries to ensure tenant filtering
    """
    def __call__(self, request):
        from django.db import connection
        from apps.core.context import get_tenant_id
        
        # Enable query logging
        from django.conf import settings
        if settings.DEBUG:
            queries_before = len(connection.queries)
        
        response = self.get_response(request)
        
        if settings.DEBUG:
            tenant_id = get_tenant_id()
            queries_after = len(connection.queries)
            
            # Check if tenant filtering was applied
            for query in connection.queries[queries_before:queries_after]:
                sql = query['sql'].lower()
                
                # Warn if query doesn't filter by tenant
                if 'from products' in sql or 'from orders' in sql:
                    if f'tenant_id = {tenant_id}' not in sql:
                        logger.warning(f"Query without tenant filter: {sql}")
        
        return response
```

---

## Tenant Context Management

### Context Flow

```
1. Request arrives with X-Tenant-ID header
   ↓
2. TenantMiddleware extracts & validates
   ↓
3. Sets thread-local context
   ↓
4. View uses get_current_tenant()
   ↓
5. QuerySet auto-filtered by tenant
   ↓
6. Response sent
   ↓
7. Context cleared (process_response)
```

### Example: Order Creation

```python
# apps/orders/views.py
from apps.core.context import get_current_tenant, get_current_outlet

class OrderViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Create order with tenant context
        """
        tenant = get_current_tenant()
        outlet = get_current_outlet()
        
        # Validate tenant context exists
        if not tenant or not outlet:
            return Response({
                'error': 'Tenant and outlet context required'
            }, status=400)
        
        # Extract cart items
        cart_items = request.data.get('items', [])
        
        # Validate all products belong to this tenant
        product_ids = [item['product_id'] for item in cart_items]
        products = Product.objects.filter(
            id__in=product_ids,
            tenant=tenant  # Ensure same tenant
        )
        
        if products.count() != len(product_ids):
            return Response({
                'error': 'Some products not found or don\'t belong to this tenant'
            }, status=400)
        
        # Create order
        order = Order.objects.create(
            tenant=tenant,
            outlet=outlet,
            cashier=request.user,
            # ... other fields
        )
        
        # Create order items
        for item in cart_items:
            product = products.get(id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                unit_price=product.price,
                # ...
            )
        
        # Calculate totals
        order.calculate_totals()
        
        return Response({
            'success': True,
            'order': OrderSerializer(order).data
        })
```

---

## Best Practices

### ✅ DO

1. **Always filter by tenant** in QuerySets
2. **Validate tenant ownership** before operations
3. **Use context helpers** (`get_current_tenant()`)
4. **Test with multiple tenants** to catch isolation bugs
5. **Index tenant_id columns** for performance
6. **Clear context** after each request
7. **Log tenant context** in error logs

### ❌ DON'T

1. **Don't skip tenant filtering** - risk data leakage
2. **Don't hardcode tenant IDs** - use context
3. **Don't trust client headers** without validation
4. **Don't share tenant data** in serializers
5. **Don't forget outlet filtering** when needed
6. **Don't allow cross-tenant references**

### Security Checklist

- [ ] All models have tenant foreign key
- [ ] All views filter by tenant
- [ ] Middleware validates tenant on every request
- [ ] No raw SQL without tenant filter
- [ ] Unit tests cover tenant isolation
- [ ] Admin panel respects tenant boundaries
- [ ] API responses don't leak tenant data

---

## Next Steps

- **[SECURITY_IMPLEMENTATION.md](SECURITY_IMPLEMENTATION.md)** - Security & RBAC details
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Complete database schema
- **[BACKEND_API_REFERENCE.md](BACKEND_API_REFERENCE.md)** - API documentation

---

**Last Updated**: January 3, 2026
