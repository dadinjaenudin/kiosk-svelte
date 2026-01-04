# 03 - RBAC & MULTI-TENANT ARCHITECTURE

## Introduction

Sistem Kiosk POS dibangun dengan **Multi-Tenant Architecture** dan **Role-Based Access Control (RBAC)** sebagai fondasi utama. Dokumen ini menjelaskan secara mendalam bagaimana kedua konsep ini diimplementasikan dan bekerja bersama.

---

## Multi-Tenancy Explained

### What is Multi-Tenancy?

**Multi-Tenancy** adalah arsitektur di mana satu instance aplikasi melayani multiple customers (tenants) dengan data yang terisolasi satu sama lain.

```
┌─────────────────────────────────────────────────────────────┐
│                    KIOSK POS APPLICATION                     │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Tenant 1   │   Tenant 2   │   Tenant 3   │   Tenant N     │
│  Pizza Hut   │    KFC       │  McDonald's  │   Starbucks    │
├──────────────┼──────────────┼──────────────┼────────────────┤
│  - Products  │  - Products  │  - Products  │  - Products    │
│  - Orders    │  - Orders    │  - Orders    │  - Orders      │
│  - Users     │  - Users     │  - Users     │  - Users       │
│  - Outlets   │  - Outlets   │  - Outlets   │  - Outlets     │
└──────────────┴──────────────┴──────────────┴────────────────┘
        ↓              ↓              ↓              ↓
┌─────────────────────────────────────────────────────────────┐
│              SHARED DATABASE (PostgreSQL)                    │
│  All tenant data in same tables, isolated by tenant_id      │
└─────────────────────────────────────────────────────────────┘
```

---

### Multi-Tenancy Patterns

#### Pattern Comparison

| Pattern | Description | Pros | Cons | Our Choice |
|---------|-------------|------|------|------------|
| **Database per Tenant** | Setiap tenant punya database terpisah | ✅ Strong isolation<br>✅ Easy scaling per tenant<br>✅ Independent backups | ❌ High cost<br>❌ Complex management<br>❌ Difficult migrations | ❌ |
| **Schema per Tenant** | Setiap tenant punya schema terpisah dalam satu database | ✅ Good isolation<br>✅ Medium cost | ❌ Complex queries<br>❌ Schema management | ❌ |
| **Row-Level Tenancy** | Semua tenant dalam satu schema, isolated by tenant_id | ✅ Low cost<br>✅ Easy management<br>✅ Simple migrations | ❌ Need careful filtering<br>❌ Shared resources | ✅ **CHOSEN** |

---

### Our Implementation: Row-Level Multi-Tenancy

#### Core Concept
Setiap row data memiliki `tenant_id` foreign key yang mengidentifikasi kepemilikan data.

```sql
-- Example: products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    name VARCHAR(200),
    price DECIMAL(10, 2),
    -- other fields
);

-- Query hanya akan return products dari tenant tertentu
SELECT * FROM products WHERE tenant_id = 67;
```

---

## Tenant Model

### Database Schema

```python
# backend/apps/tenants/models.py
class Tenant(models.Model):
    """
    Represents a restaurant brand/franchise
    Example: "Pizza Hut", "KFC", "Starbucks"
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='tenants/logos/', null=True, blank=True)
    
    # Branding
    primary_color = models.CharField(max_length=7, default='#FF6B35')
    secondary_color = models.CharField(max_length=7, default='#F7931E')
    
    # Business info
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Tax settings
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    service_charge_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Example Data**:
```json
{
  "id": 67,
  "name": "Pizza Palace",
  "slug": "pizza-palace",
  "primary_color": "#FF6B35",
  "secondary_color": "#F7931E",
  "tax_rate": "10.00",
  "service_charge_rate": "5.00",
  "is_active": true
}
```

---

### Outlet Model (Multi-Outlet Support)

```python
class Outlet(models.Model):
    """
    Physical location/store of a tenant
    One tenant can have multiple outlets
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='outlets')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Operating hours
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    # Network Configuration
    websocket_url = models.CharField(
        max_length=255, 
        blank=True, 
        default='ws://localhost:3001',
        help_text='WebSocket URL for Kitchen Sync Server'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['tenant', 'slug']]
```

**Relationship**:
```
Tenant (1) ──has──> Outlets (N)
  │
  └─> Pizza Palace
      ├─> Outlet 1: Mall Yogya
      ├─> Outlet 2: Malioboro
      └─> Outlet 3: Hartono Mall
```

---

## TenantModel Base Class

### Implementation

```python
# backend/apps/core/models.py
from django.db import models
from apps.core.context import get_current_tenant

class TenantManager(models.Manager):
    """
    Manager that automatically filters queries by current tenant
    """
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant:
            return qs.filter(tenant=tenant)
        
        # If no tenant in context, return empty for safety
        return qs.none()


class TenantModel(models.Model):
    """
    Base model for all tenant-specific data
    
    Usage:
        class Product(TenantModel):
            name = models.CharField(max_length=200)
            # tenant field automatically added
    """
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )
    
    objects = TenantManager()      # Auto-filtered by tenant
    all_objects = models.Manager()  # Bypass filter (admin only)
    
    class Meta:
        abstract = True
```

---

### How It Works

#### Example: Product Model

```python
# backend/apps/products/models.py
class Product(TenantModel):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # tenant field inherited from TenantModel
```

#### Automatic Tenant Filtering

```python
# In a view with tenant context set
products = Product.objects.all()
# SQL: SELECT * FROM products WHERE tenant_id = 67

# Get specific product
product = Product.objects.get(id=123)
# SQL: SELECT * FROM products WHERE id = 123 AND tenant_id = 67
# This prevents accessing products from other tenants!

# Admin bypass (super admin only)
all_products = Product.all_objects.all()
# SQL: SELECT * FROM products
# Returns products from ALL tenants
```

---

## Tenant Context Management

### Thread-Local Storage

```python
# backend/apps/core/context.py
import threading

_thread_local = threading.local()

def set_current_tenant(tenant):
    """Set tenant for current request thread"""
    _thread_local.tenant = tenant

def get_current_tenant():
    """Get tenant from current request thread"""
    return getattr(_thread_local, 'tenant', None)

def set_current_outlet(outlet):
    """Set outlet for current request thread"""
    _thread_local.outlet = outlet

def get_current_outlet():
    """Get outlet from current request thread"""
    return getattr(_thread_local, 'outlet', None)

def clear_tenant_context():
    """Clear tenant context (called at request end)"""
    if hasattr(_thread_local, 'tenant'):
        del _thread_local.tenant
    if hasattr(_thread_local, 'outlet'):
        del _thread_local.outlet
```

---

### Tenant Middleware

```python
# backend/apps/tenants/middleware.py
class TenantMiddleware(MiddlewareMixin):
    """
    Extract tenant from request and set in thread-local storage
    
    Sources (in order of priority):
    1. X-Tenant-ID header
    2. User's tenant (from JWT/authentication)
    3. URL parameter (?tenant_id=67)
    """
    
    EXCLUDE_URLS = [
        '/api/auth/',
        '/api/health/',
        '/api/public/',
        '/admin/',
    ]
    
    def process_request(self, request):
        # Clear previous context
        clear_tenant_context()
        
        # Skip excluded URLs
        if any(request.path.startswith(url) for url in self.EXCLUDE_URLS):
            return None
        
        # Get tenant from header
        tenant_id = request.headers.get('X-Tenant-ID')
        
        # Or get from authenticated user
        if not tenant_id and hasattr(request, 'user') and request.user.is_authenticated:
            tenant_id = request.user.tenant_id
        
        # Load tenant
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
                set_current_tenant(tenant)
                request.tenant = tenant
            except Tenant.DoesNotExist:
                return JsonResponse({'error': 'Invalid tenant'}, status=400)
        
        # Get outlet if provided
        outlet_id = request.headers.get('X-Outlet-ID')
        if outlet_id:
            try:
                outlet = Outlet.objects.get(id=outlet_id, tenant=tenant)
                set_current_outlet(outlet)
                request.outlet = outlet
            except Outlet.DoesNotExist:
                pass
        
        return None
```

---

## Role-Based Access Control (RBAC)

### User Roles

```python
# backend/apps/users/models.py
class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('tenant_owner', 'Tenant Owner'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('kitchen', 'Kitchen Staff'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True, blank=True)
    outlet = models.ForeignKey('tenants.Outlet', on_delete=models.SET_NULL, null=True, blank=True)
    accessible_outlets = models.ManyToManyField('tenants.Outlet', blank=True, related_name='accessible_users')
```

---

### Role Hierarchy

```
┌──────────────────────────────────────────────────────────┐
│                      SUPER ADMIN                          │
│  ✅ Access ALL tenants                                   │
│  ✅ Manage tenants & outlets                             │
│  ✅ System configuration                                 │
│  ✅ View global analytics                                │
└───────────────────┬──────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    ┌────▼─────────┐   ┌──────▼─────────┐
    │    ADMIN     │   │  TENANT OWNER  │
    │ (IT/Support) │   │  (Franchise    │
    │              │   │   Owner)       │
    │ ✅ Technical │   │ ✅ All outlets │
    │   support    │   │   in tenant    │
    │ ✅ Multi-    │   │ ✅ Business    │
    │   tenant     │   │   reports      │
    │   access     │   │ ✅ Manage      │
    └──────────────┘   │   managers     │
                       └────────┬───────┘
                                │
                        ┌───────▼────────┐
                        │    MANAGER     │
                        │  (Store Mgr)   │
                        │ ✅ Assigned    │
                        │   outlet(s)    │
                        │ ✅ Products    │
                        │ ✅ Promotions  │
                        │ ✅ Staff       │
                        │ ✅ Reports     │
                        └────────┬───────┘
                                 │
                     ┌───────────┴───────────┐
                     │                       │
              ┌──────▼────────┐    ┌────────▼────────┐
              │    CASHIER    │    │  KITCHEN STAFF  │
              │ ✅ Process    │    │ ✅ View orders  │
              │   orders      │    │ ✅ Update       │
              │ ✅ Payments   │    │   status        │
              │ ✅ View       │    │ ✅ Mark         │
              │   products    │    │   complete      │
              └───────────────┘    └─────────────────┘
```

---

### Permission Matrix

| Feature | Super Admin | Admin | Tenant Owner | Manager | Cashier | Kitchen |
|---------|-------------|-------|--------------|---------|---------|---------|
| **Tenants** |
| View all tenants | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create tenant | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Edit tenant | ✅ | ❌ | ✅ (own) | ❌ | ❌ | ❌ |
| Delete tenant | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Outlets** |
| View all outlets | ✅ | ✅ | ✅ (own) | ✅ (assigned) | ✅ (assigned) | ✅ (assigned) |
| Create outlet | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit outlet | ✅ | ✅ | ✅ | ✅ (own) | ❌ | ❌ |
| Delete outlet | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Users** |
| View users | ✅ | ✅ | ✅ (tenant) | ✅ (outlet) | ❌ | ❌ |
| Create user | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit user | ✅ | ✅ | ✅ | ✅ (outlet) | ❌ | ❌ |
| Delete user | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Products** |
| View products | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create product | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit product | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Delete product | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| View cost price | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Orders** |
| View all orders | ✅ | ✅ | ✅ (tenant) | ✅ (outlet) | ✅ (outlet) | ✅ (outlet) |
| Create order | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit order | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Cancel order | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Update status | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Promotions** |
| View promotions | ✅ | ✅ | ✅ | ✅ | ✅ (read) | ❌ |
| Create promotion | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit promotion | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Delete promotion | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Reports** |
| View tenant reports | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| View outlet reports | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Export data | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Settings** |
| System settings | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Tenant settings | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Outlet settings | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |

---

### Permission Implementation

#### Custom Permission Classes

```python
# backend/apps/core/permissions.py
from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """Only super admins can access"""
    def has_permission(self, request, view):
        return request.user and request.user.role == 'super_admin'


class IsTenantUser(permissions.BasePermission):
    """User must belong to the request's tenant"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admin can access all tenants
        if request.user.role == 'super_admin':
            return True
        
        # Check if user belongs to request tenant
        return request.user.tenant_id == getattr(request, 'tenant_id', None)


class IsOwnerOrManager(permissions.BasePermission):
    """Only tenant owner or manager can access"""
    def has_permission(self, request, view):
        return request.user and request.user.role in ['tenant_owner', 'manager']


class CanManageOutlet(permissions.BasePermission):
    """User can manage the outlet (owner, manager of that outlet)"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.role in ['super_admin', 'admin']:
            return True
        
        if user.role == 'tenant_owner':
            return obj.tenant_id == user.tenant_id
        
        if user.role == 'manager':
            return obj.id in user.accessible_outlets.values_list('id', flat=True)
        
        return False
```

---

#### Usage in ViewSets

```python
# backend/apps/products/views.py
from rest_framework import viewsets
from apps.core.permissions import IsTenantUser, IsOwnerOrManager

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsTenantUser]  # Must belong to tenant
    
    def get_permissions(self):
        """Different permissions for different actions"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOwnerOrManager()]  # Only owner/manager can modify
        return [IsTenantUser()]  # Anyone in tenant can view
    
    def perform_create(self, serializer):
        """Automatically set tenant when creating"""
        serializer.save(tenant=self.request.tenant)
```

---

## Security Patterns

### 1. Tenant Isolation Enforcement

#### Database Level
```python
# Always filter by tenant
products = Product.objects.filter(tenant=request.tenant)

# Never use:
products = Product.all_objects.all()  # Unless you're super_admin!
```

#### View Level
```python
class OrderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        """Filter orders by user's access level"""
        user = self.request.user
        
        if user.role == 'super_admin':
            return Order.all_objects.all()
        
        if user.role == 'tenant_owner':
            return Order.objects.filter(tenant=user.tenant)
        
        if user.role == 'manager':
            return Order.objects.filter(outlet__in=user.accessible_outlets.all())
        
        if user.role in ['cashier', 'kitchen']:
            return Order.objects.filter(outlet=user.outlet)
        
        return Order.objects.none()
```

---

### 2. Cross-Tenant Data Prevention

#### Problem Scenario
```python
# ❌ BAD: Cashier could theoretically access other tenant's data
product_id = 123  # From other tenant
product = Product.objects.get(id=product_id)  # If no tenant filter!
```

#### Solution with TenantModel
```python
# ✅ GOOD: TenantModel automatically filters
product_id = 123
try:
    product = Product.objects.get(id=product_id)
    # Only returns if product belongs to current tenant
except Product.DoesNotExist:
    return Response({'error': 'Product not found'}, status=404)
```

---

### 3. Admin Bypass Pattern

```python
# For super admin who needs to access all tenants
from apps.core.permissions import IsSuperAdmin

class TenantAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdmin]
    queryset = Tenant.objects.all()  # No tenant filter
    
    def get_queryset(self):
        # Super admin sees all tenants
        return Tenant.objects.all()
```

---

## Multi-Outlet Scenarios

### Scenario 1: Single Outlet User (Cashier)

```python
user = User.objects.get(username='john_cashier')
# user.role = 'cashier'
# user.tenant_id = 67
# user.outlet_id = 45

# Cashier can only see their outlet's data
orders = Order.objects.filter(outlet=user.outlet)
# Returns only outlet 45's orders
```

### Scenario 2: Multi-Outlet User (Manager)

```python
user = User.objects.get(username='jane_manager')
# user.role = 'manager'
# user.tenant_id = 67
# user.accessible_outlets = [45, 46, 47]  # 3 outlets

# Manager can see multiple outlets
orders = Order.objects.filter(outlet__in=user.accessible_outlets.all())
# Returns orders from outlets 45, 46, 47
```

### Scenario 3: Tenant-Wide Access (Owner)

```python
user = User.objects.get(username='owner_smith')
# user.role = 'tenant_owner'
# user.tenant_id = 67

# Owner sees all outlets in their tenant
orders = Order.objects.filter(tenant=user.tenant)
# Returns all orders from tenant 67, all outlets
```

---

## Common Patterns & Examples

### Pattern 1: Create with Tenant
```python
# Auto-assign tenant to new object
def create_product(request, product_data):
    product = Product.objects.create(
        **product_data,
        tenant=request.tenant  # From middleware
    )
    return product
```

### Pattern 2: Update with Permission Check
```python
def update_product(request, product_id, updates):
    product = Product.objects.get(id=product_id)
    # TenantModel ensures product belongs to request.tenant
    
    # Check if user can modify
    if request.user.role not in ['tenant_owner', 'manager']:
        raise PermissionDenied("You cannot modify products")
    
    for key, value in updates.items():
        setattr(product, key, value)
    product.save()
    return product
```

### Pattern 3: Bulk Operations with Tenant
```python
# Update all products in current tenant
Product.objects.filter(category_id=5).update(is_available=False)
# Only affects current tenant's products due to TenantManager
```

---

## Testing Multi-Tenancy

### Test Isolation
```python
# backend/apps/products/tests.py
from django.test import TestCase
from apps.tenants.models import Tenant
from apps.products.models import Product
from apps.core.context import set_current_tenant

class ProductTestCase(TestCase):
    def setUp(self):
        self.tenant1 = Tenant.objects.create(name="Tenant 1")
        self.tenant2 = Tenant.objects.create(name="Tenant 2")
        
        # Set context to tenant1
        set_current_tenant(self.tenant1)
        
        self.product1 = Product.objects.create(
            name="Product 1",
            price=10.00,
            tenant=self.tenant1
        )
        
        # Switch to tenant2
        set_current_tenant(self.tenant2)
        
        self.product2 = Product.objects.create(
            name="Product 2",
            price=20.00,
            tenant=self.tenant2
        )
    
    def test_tenant_isolation(self):
        """Products should be isolated by tenant"""
        set_current_tenant(self.tenant1)
        products = Product.objects.all()
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first(), self.product1)
        
        set_current_tenant(self.tenant2)
        products = Product.objects.all()
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first(), self.product2)
```

---

## Best Practices

### ✅ DO's

1. **Always use TenantModel** for tenant-specific data
```python
class MyModel(TenantModel):  # ✅ Good
    name = models.CharField(max_length=200)
```

2. **Set tenant in middleware**, not in views
```python
# ✅ Middleware handles this
set_current_tenant(tenant)
```

3. **Use all_objects sparingly** (only for super_admin)
```python
if user.role == 'super_admin':
    products = Product.all_objects.all()  # ✅ OK for admin
```

4. **Test tenant isolation** thoroughly
```python
# ✅ Write tests for cross-tenant access
def test_cannot_access_other_tenant_data(self):
    # ...
```

---

### ❌ DON'Ts

1. **Don't bypass tenant filter** without permission check
```python
products = Product.all_objects.all()  # ❌ Dangerous!
```

2. **Don't trust client-sent tenant_id** without validation
```python
# ❌ Bad
tenant_id = request.data.get('tenant_id')
product.tenant_id = tenant_id  # Could be forged!

# ✅ Good
product.tenant = request.tenant  # From authenticated context
```

3. **Don't forget tenant in manual queries**
```python
# ❌ Bad
cursor.execute("SELECT * FROM products")

# ✅ Good
cursor.execute("SELECT * FROM products WHERE tenant_id = %s", [tenant.id])
```

4. **Don't share objects across tenants** without explicit design
```python
# ❌ Anti-pattern
shared_category = Category.objects.create(name="Beverages")
# This category would be in ONE tenant, not shared
```

---

## Troubleshooting

### Issue 1: "Object not found" but it exists
**Cause**: Object belongs to different tenant

**Debug**:
```python
# Check current tenant
print(f"Current tenant: {get_current_tenant()}")

# Try with all_objects
product = Product.all_objects.get(id=123)
print(f"Product tenant: {product.tenant}")
```

### Issue 2: Empty queryset for super_admin
**Cause**: Middleware didn't bypass tenant filter

**Fix**:
```python
# In view for super_admin
if request.user.role == 'super_admin':
    return Product.all_objects.all()
else:
    return Product.objects.all()
```

### Issue 3: Cross-tenant reference error
**Cause**: Trying to associate objects from different tenants

**Fix**:
```python
# ❌ This will fail if product and promotion are from different tenants
promotion.products.add(product)

# ✅ Validate first
if product.tenant_id != promotion.tenant_id:
    raise ValidationError("Cannot mix tenants")
```

---

## Migration Considerations

### Adding Tenant to Existing Model
```python
# migrations/0002_add_tenant_to_model.py
from django.db import migrations

def set_default_tenant(apps, schema_editor):
    """Set all existing records to default tenant"""
    MyModel = apps.get_model('myapp', 'MyModel')
    Tenant = apps.get_model('tenants', 'Tenant')
    
    default_tenant = Tenant.objects.first()
    MyModel.objects.filter(tenant__isnull=True).update(tenant=default_tenant)

class Migration(migrations.Migration):
    dependencies = [...]
    
    operations = [
        migrations.AddField('mymodel', 'tenant', ...),
        migrations.RunPython(set_default_tenant),
    ]
```

---

## Future Enhancements

### Planned Features
- [ ] Row-level security in PostgreSQL
- [ ] Tenant-specific database sharding
- [ ] Automated tenant provisioning API
- [ ] Tenant usage analytics
- [ ] Tenant-specific feature flags

---

**Last Updated**: January 4, 2026  
**Version**: 2.0  
**Critical Document**: Review any changes to multi-tenancy carefully!
