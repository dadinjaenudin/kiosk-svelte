# Phase 1: Database Schema & Models - Multi-Outlet Extension

**Status:** ✅ COMPLETED  
**Date:** January 1, 2026  
**Duration:** ~1 hour

---

## 📋 Overview

Phase 1 menambahkan database schema untuk multi-outlet support pada sistem RBAC yang sudah ada. Perubahan ini memungkinkan:
- **Tenant Owner**: Role baru untuk franchise owner yang bisa manage semua outlet
- **Multi-outlet Access**: User dapat akses ke multiple outlets (ManyToMany)
- **Outlet-specific Products**: Produk bisa dibuat untuk outlet tertentu atau shared
- **Outlet-specific Orders**: Orders sudah terikat ke outlet tertentu

---

## ✅ Completed Tasks

### 1. Outlet Model (Already Exists) ✅

**File:** `backend/apps/tenants/models.py`

Model Outlet sudah ada dengan struktur lengkap:

```python
class Outlet(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='outlets')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    
    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Operating hours
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Features:**
- ✅ Unique constraint: `tenant + slug`
- ✅ Address and location info
- ✅ Operating hours
- ✅ Active status

---

### 2. User Model Updates ✅

**File:** `backend/apps/users/models.py`

#### Added:

**1. New Role: `tenant_owner`**
```python
ROLE_CHOICES = (
    ('super_admin', 'Super Admin'),
    ('admin', 'Admin'),
    ('tenant_owner', 'Tenant Owner'),  # NEW
    ('manager', 'Manager'),
    ('cashier', 'Cashier'),
    ('kitchen', 'Kitchen Staff'),
)
```

**2. ManyToMany Field: `accessible_outlets`**
```python
accessible_outlets = models.ManyToManyField(
    'tenants.Outlet', 
    blank=True, 
    related_name='accessible_users',
    help_text='Outlets this user can access (for managers)'
)
```

**3. Updated `outlet` Field**
```python
outlet = models.ForeignKey(
    'tenants.Outlet', 
    on_delete=models.SET_NULL, 
    null=True, blank=True, 
    related_name='users', 
    help_text='Primary/default outlet for this user'
)
```

**Changes:**
- ✅ Added `tenant_owner` role (level 80)
- ✅ Added `accessible_outlets` ManyToMany field
- ✅ Updated `outlet` field with help text

---

### 3. Product Model Updates ✅

**File:** `backend/apps/products/models.py`

#### Added Outlet Field:

```python
class Product(TenantModel):
    """
    Product/Menu item
    Multi-outlet: Products can be outlet-specific or shared across all outlets
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='products')
    outlet = models.ForeignKey(
        Outlet, 
        on_delete=models.CASCADE, 
        null=True, blank=True, 
        related_name='products',
        help_text='If set, product is only available at this outlet. Leave blank for all outlets.'
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    # ... rest of fields
```

**Features:**
- ✅ Optional outlet field (nullable)
- ✅ If outlet=null: Product available at all tenant outlets
- ✅ If outlet set: Product only available at that outlet

---

### 4. Order Model (Already Has Outlet) ✅

**File:** `backend/apps/orders/models.py`

Order model sudah memiliki outlet field:

```python
class Order(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='orders')
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='orders')
    # ... rest of fields
```

**Features:**
- ✅ Orders already tied to specific outlet
- ✅ Required field (not nullable)

---

### 5. Permission System Updates ✅

**File:** `backend/apps/core/permissions.py`

Updated role hierarchy:

```python
ROLE_HIERARCHY = {
    'super_admin': 100,  # Platform superadmin - all access
    'admin': 90,         # Multi-tenant admin - all access
    'tenant_owner': 80,  # Tenant owner - all outlets in tenant [NEW]
    'manager': 50,       # Tenant manager - full tenant access
    'cashier': 30,       # Cashier - create orders, process payments
    'kitchen': 20,       # Kitchen staff - view & update order status
}
```

**Changes:**
- ✅ Added `tenant_owner` with level 80 (between admin and manager)

---

### 6. Migrations Created & Applied ✅

Generated migrations:
- **users.0004_user_accessible_outlets_alter_user_outlet_and_more**
  - Add accessible_outlets ManyToMany field
  - Update outlet field with help text
  - Add tenant_owner to role choices

- **products.0004_product_outlet**
  - Add outlet ForeignKey to Product model

Applied successfully:
```bash
docker-compose exec backend python manage.py migrate
# Operations to perform:
#   Apply all migrations: users, products, ...
# Running migrations:
#   Applying products.0004_product_outlet... OK
#   Applying users.0004_user_accessible_outlets_alter_user_outlet_and_more... OK
```

---

### 7. Admin Interface Updates ✅

#### Updated User Admin:
**File:** `backend/apps/users/admin.py`

```python
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'tenant', 'outlet', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'tenant', 'outlet')
    filter_horizontal = ('accessible_outlets',)  # For ManyToMany field
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'phone_number', 'tenant', 'outlet', 'accessible_outlets')
        }),
    )
```

#### Updated Product Admin:
**File:** `backend/apps/products/admin.py`

```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'outlet', 'price', 'is_available', 'created_at')
    list_filter = ('category', 'outlet', 'is_available', 'created_at')
    raw_id_fields = ('tenant', 'outlet', 'category')
```

**Changes:**
- ✅ Added `accessible_outlets` to User admin with horizontal filter
- ✅ Added `outlet` filter to User admin
- ✅ Added `outlet` display and filter to Product admin
- ✅ Added `raw_id_fields` for better performance

---

## 📊 Database Schema Changes

### New Fields Summary:

| Model | Field | Type | Purpose |
|-------|-------|------|---------|
| **User** | `accessible_outlets` | ManyToMany | Outlets user can access |
| **User** | `role` | CharField | Added `tenant_owner` choice |
| **Product** | `outlet` | ForeignKey | Outlet-specific products |

### Relationships:

```
User → accessible_outlets → Outlet (M:N)
User → outlet → Outlet (M:1) [Primary outlet]
Product → outlet → Outlet (M:1) [Optional, for outlet-specific items]
Order → outlet → Outlet (M:1) [Required, already exists]
```

---

## 🎯 Role Access Matrix

| Role | Level | Tenant Access | Outlet Access | Use Case |
|------|-------|---------------|---------------|----------|
| super_admin | 100 | ALL | ALL | Platform admin |
| admin | 90 | ALL | ALL | Multi-tenant admin |
| **tenant_owner** | **80** | **1 Tenant** | **ALL Outlets** | **Franchise owner** |
| manager | 50 | 1 Tenant | Multiple (via accessible_outlets) | Outlet manager |
| cashier | 30 | 1 Tenant | 1 Outlet | Cashier staff |
| kitchen | 20 | 1 Tenant | 1 Outlet | Kitchen staff |

---

## 📝 Usage Examples

### Creating a Tenant Owner:

```python
from apps.users.models import User
from apps.tenants.models import Tenant

tenant = Tenant.objects.get(slug='pizza-paradise')

owner = User.objects.create_user(
    username='john_owner',
    password='password123',
    email='john@pizza.com',
    role='tenant_owner',
    tenant=tenant,
    outlet=None  # No primary outlet, can access all
)
```

### Creating a Manager with Multiple Outlets:

```python
from apps.tenants.models import Outlet

outlet1 = Outlet.objects.get(slug='outlet-jakarta')
outlet2 = Outlet.objects.get(slug='outlet-bandung')

manager = User.objects.create_user(
    username='manager_jkt_bdg',
    password='password123',
    role='manager',
    tenant=tenant,
    outlet=outlet1  # Primary outlet
)

# Grant access to multiple outlets
manager.accessible_outlets.add(outlet1, outlet2)
```

### Creating Outlet-Specific Product:

```python
from apps.products.models import Product

# Product available at ALL outlets (outlet=None)
global_product = Product.objects.create(
    tenant=tenant,
    outlet=None,  # Available everywhere
    name='Classic Margherita',
    sku='PIZZA-MARG-001',
    price=85000
)

# Product available at ONE outlet only
outlet_product = Product.objects.create(
    tenant=tenant,
    outlet=outlet1,  # Only at Jakarta outlet
    name='Jakarta Special Pizza',
    sku='PIZZA-JKT-001',
    price=95000
)
```

---

## 🧪 Testing

### 1. Verify User Roles:

```bash
docker-compose exec backend python manage.py shell
```

```python
from apps.users.models import User

# Check role choices
print(User.ROLE_CHOICES)
# Should include ('tenant_owner', 'Tenant Owner')

# Create test tenant owner
tenant_owner = User.objects.create_user(
    username='test_owner',
    password='test123',
    role='tenant_owner'
)
print(tenant_owner.get_role_display())  # Should print: Tenant Owner
```

### 2. Verify accessible_outlets:

```python
from apps.tenants.models import Outlet

# Get some outlets
outlets = Outlet.objects.all()[:3]

# Assign outlets to manager
manager = User.objects.get(username='manager_test')
manager.accessible_outlets.set(outlets)

# Verify
print(f"Manager can access {manager.accessible_outlets.count()} outlets")
for outlet in manager.accessible_outlets.all():
    print(f"  - {outlet.name}")
```

### 3. Verify Product Outlets:

```python
from apps.products.models import Product

# Create outlet-specific product
product = Product.objects.create(
    tenant=tenant,
    outlet=outlets[0],
    name='Test Product',
    sku='TEST-001',
    price=50000
)

print(f"Product: {product.name}")
print(f"Available at: {product.outlet.name if product.outlet else 'All outlets'}")
```

---

## 🔄 Next Steps: Phase 2

Database schema is ready! Next phase will add:

1. **Outlet Context Management**
   - Middleware to set current outlet
   - Session-based outlet tracking
   - Helper functions to get current outlet

2. **Enhanced Middleware**
   - Outlet filtering in queries
   - Automatic outlet assignment for new records
   - Outlet switching for admin/tenant_owner

3. **API Endpoints**
   - GET /api/outlets/ - List outlets for current tenant
   - POST /api/auth/set-outlet/ - Set current outlet
   - GET /api/auth/me/ - Include accessible outlets

See [MULTI_OUTLET_ROADMAP.md](../MULTI_OUTLET_ROADMAP.md) for complete plan.

---

## 📚 Files Modified

### Models:
- ✅ `backend/apps/users/models.py` - Added accessible_outlets, tenant_owner role
- ✅ `backend/apps/products/models.py` - Added outlet field
- ✅ `backend/apps/tenants/models.py` - Outlet model (already exists)
- ✅ `backend/apps/orders/models.py` - Has outlet field (already exists)

### Permissions:
- ✅ `backend/apps/core/permissions.py` - Added tenant_owner to ROLE_HIERARCHY

### Admin:
- ✅ `backend/apps/users/admin.py` - Added accessible_outlets field
- ✅ `backend/apps/products/admin.py` - Added outlet filter

### Migrations:
- ✅ `backend/apps/users/migrations/0004_*.py` - User model changes
- ✅ `backend/apps/products/migrations/0004_*.py` - Product outlet field

---

**Phase 1 Status: COMPLETE ✅**

Database schema ready for multi-outlet system. All models updated, migrations applied, and admin interface configured.

**Ready for Phase 2: Backend Context & Middleware**

---

**Completed By:** AI Assistant (GitHub Copilot)  
**Reviewed By:** -  
**Deployed To:** Development (localhost:8001)

---

*Last Updated: January 1, 2026*
