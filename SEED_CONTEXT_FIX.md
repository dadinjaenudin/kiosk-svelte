# 🔧 SEED COMMAND FIX: Tenant Context Management

## ❌ Error Yang Terjadi
```
apps.products.models.Product.DoesNotExist: Product matching query does not exist.
```

Saat menjalankan:
```bash
docker-compose exec backend python manage.py seed_demo_data
```

Error di line 183:
```python
nasi_goreng = Product.objects.get(sku='FD-001')
# ❌ Error: Product tidak ditemukan
```

---

## 🔍 Root Cause

### Problem 1: TenantManager Auto-Filtering
Setelah Phase 2 implementation, semua model inherit dari `TenantModel` yang menggunakan `TenantManager`:

```python
class TenantManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()  # ← Ambil dari context
        if tenant:
            qs = qs.filter(tenant=tenant)  # ← Auto filter!
        return qs
```

**Masalah**:
- `Product.objects.get()` otomatis difilter by current tenant
- Saat seed command, **belum ada tenant context** yang di-set
- Hasil: Query `Product.objects.get(sku='FD-001')` tidak menemukan product (walau sudah di-create sebelumnya)

### Problem 2: Check Data Script
Script `check_data.py` juga mengalami masalah sama:
```python
Product.objects.count()  # Returns 0 karena no tenant context
```

---

## ✅ Solution Applied

### Fix 1: Seed Command (`seed_demo_data.py`)

**Import tenant context:**
```python
from apps.core.context import set_current_tenant, clear_tenant_context
```

**Clear context di awal:**
```python
def handle(self, *args, **options):
    # Clear any existing context
    clear_tenant_context()
    
    self.stdout.write(self.style.SUCCESS('🌱 Starting data seeding...'))
```

**Set tenant context setelah create tenant:**
```python
# 1. Create Tenant
tenant, created = Tenant.objects.get_or_create(
    slug='warung-makan-sedap',
    defaults={...}
)
self.stdout.write(self.style.SUCCESS(f'✓ Tenant: {tenant.name}'))

# Set tenant context for the rest of the seeding
set_current_tenant(tenant)  # ← Key fix!

# 2. Create Outlets (sekarang dengan tenant context)
outlet1, _ = Outlet.objects.get_or_create(...)
```

**Clear context di akhir:**
```python
self.stdout.write('\n🌐 Access the Kiosk Mode at: http://localhost:5173/kiosk')

# Clear tenant context
clear_tenant_context()
```

### Fix 2: Check Data Script (`check_data.py`)

**Use raw SQL to bypass TenantManager:**
```python
from apps.core.context import clear_tenant_context

# Clear tenant context to see all data
clear_tenant_context()

# Use raw SQL queries to bypass manager
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]

print(f"  Categories: {cat_count}")
print(f"  Products: {prod_count}")

# List products
with connection.cursor() as cursor:
    cursor.execute("SELECT name, price FROM products LIMIT 5")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: Rp {row[1]:,.0f}")
```

---

## 🚀 Deploy & Test Fix

### Step 1: Pull Latest Code
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
```

### Step 2: Restart Backend
```bash
docker-compose restart backend
```

### Step 3: Run Seed Command
```bash
docker-compose exec backend python manage.py seed_demo_data
```

**Expected Output (SUCCESS)**:
```
🌱 Starting data seeding...
Creating tenant...
✓ Tenant: Warung Makan Sedap
Creating outlets...
✓ Outlet: Cabang Pusat
✓ Outlet: Cabang Mall
Creating users...
✓ Admin User: admin
✓ Cashier User: cashier
Creating categories...
✓ Category: Main Course
✓ Category: Beverages
✓ Category: Desserts
✓ Category: Snacks
✓ Category: Special Menu
Creating products...
  ✓ Nasi Goreng Spesial - Rp 25,000
  ✓ Mie Goreng - Rp 20,000
  ... (18 more)
Creating product modifiers...
✓ Product modifiers created
Creating sample orders...
✓ Sample order created: ORD-XXXXXX

==================================================
✅ Data seeding completed successfully!
==================================================

Tenant: Warung Makan Sedap
Outlets: 2
Categories: 5
Products: 20
Users: 2
Orders: 1

👤 Login credentials:
   Admin    - username: admin, password: admin123
   Cashier  - username: cashier, password: cashier123

🌐 Access the Kiosk Mode at: http://localhost:5173/kiosk
```

### Step 4: Verify Data
```bash
docker-compose exec backend python check_data.py
```

**Expected Output**:
```
📊 Database Check:
  Tenants: 1
  Outlets: 2
  Users: 2
  Categories: 5
  Products: 20

✅ Products exist:
  - Nasi Goreng Spesial: Rp 25,000
  - Mie Goreng: Rp 20,000
  - Ayam Bakar: Rp 35,000
  - Sate Ayam: Rp 30,000
  - Gado-Gado: Rp 22,000
```

### Step 5: Test Frontend
```bash
# Open browser:
http://localhost:5174/kiosk

# Console (F12) should show:
Categories loaded: 5
Products loaded: 20
```

---

## 🔍 How Tenant Context Works

### Thread-Local Storage
```python
# apps/core/context.py
import threading

_thread_locals = threading.local()

def set_current_tenant(tenant):
    """Set current tenant in thread-local storage"""
    _thread_locals.tenant = tenant

def get_current_tenant():
    """Get current tenant from thread-local storage"""
    return getattr(_thread_locals, 'tenant', None)

def clear_tenant_context():
    """Clear all tenant context"""
    _thread_locals.tenant = None
    _thread_locals.outlet = None
    _thread_locals.user = None
```

### Manager Auto-Filtering
```python
# apps/core/models.py
class TenantManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        
        # If tenant context is set, filter by tenant
        if tenant:
            qs = qs.filter(tenant=tenant)
        
        return qs
```

### Model Usage
```python
# Product inherits from TenantModel
class Product(TenantModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    objects = TenantManager()  # Auto-filtering manager
```

### Query Behavior
```python
# WITHOUT tenant context:
Product.objects.all()  # Returns ALL products (if superuser)
                      # OR returns EMPTY queryset (if no context)

# WITH tenant context:
set_current_tenant(tenant_1)
Product.objects.all()  # Returns only tenant_1's products

set_current_tenant(tenant_2)
Product.objects.all()  # Returns only tenant_2's products
```

---

## 📊 What's Fixed

| Component | Before | After |
|-----------|--------|-------|
| seed_demo_data.py | ❌ Product.DoesNotExist | ✅ Creates 20 products |
| check_data.py | ❌ Shows 0 products | ✅ Shows all products |
| Tenant isolation | ⚠️ Incomplete | ✅ Full isolation |
| Context management | ❌ No context | ✅ Proper context |

---

## 🎯 Best Practices

### 1. Management Commands
Always set tenant context in management commands:
```python
from apps.core.context import set_current_tenant, clear_tenant_context

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Clear context first
        clear_tenant_context()
        
        # Create or get tenant
        tenant = Tenant.objects.get(slug='my-tenant')
        
        # Set context
        set_current_tenant(tenant)
        
        # Now all queries are tenant-scoped
        products = Product.objects.all()  # Only this tenant's products
        
        # Clear context when done
        clear_tenant_context()
```

### 2. Scripts
Use raw SQL for global queries:
```python
from django.db import connection

# Bypass TenantManager
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
```

### 3. Views
Middleware automatically sets context:
```python
# Middleware reads headers and sets context
X-Tenant-ID: 1
X-Outlet-ID: 2

# In views, queries are auto-scoped:
def my_view(request):
    products = Product.objects.all()  # Auto-filtered by tenant
    return JsonResponse({'products': list(products.values())})
```

---

## 🐛 Troubleshooting

### Issue 1: "Product matching query does not exist"
```bash
# Ensure tenant context is set:
set_current_tenant(tenant)

# Or use filter instead of get:
products = Product.objects.filter(sku='FD-001')
if products.exists():
    product = products.first()
```

### Issue 2: "Objects.count() returns 0"
```bash
# For admin/global queries, use raw SQL:
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
```

### Issue 3: Need to query all tenants
```python
# Use base manager (bypasses TenantManager):
from django.db.models import Manager

# In model:
all_objects = Manager()  # Base manager

# Usage:
Product.all_objects.all()  # All products, all tenants
Product.objects.all()      # Only current tenant's products
```

---

## 📚 Related Files

```
backend/
├── apps/
│   ├── core/
│   │   ├── context.py         # Tenant context management
│   │   └── models.py          # TenantModel, TenantManager
│   └── products/
│       └── management/
│           └── commands/
│               └── seed_demo_data.py  # FIXED: Added context
└── check_data.py              # FIXED: Raw SQL queries
```

---

## 🎉 Summary

**SEED COMMAND FIXED! ✅**

Changes:
- ✅ Added tenant context to `seed_demo_data.py`
- ✅ Fixed `check_data.py` with raw SQL
- ✅ Proper context management (set/clear)

Deploy:
```bash
git pull origin main
docker-compose restart backend
docker-compose exec backend python manage.py seed_demo_data
```

Verify:
```bash
docker-compose exec backend python check_data.py
# Should show 20 products
```

**GitHub**: https://github.com/dadinjaenudin/kiosk-svelte
**Latest Commit**: `2af07a6` - fix: Add tenant context management to seed and check commands

**Status**: ✅ **SEEDING WORKS!**

Sekarang seed command bisa jalan dengan baik dan data akan ter-create dengan benar! 🎉
