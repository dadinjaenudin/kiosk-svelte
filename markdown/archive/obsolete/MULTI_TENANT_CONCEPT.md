# Multi-Tenant POS System - Complete Concept & Architecture

## Date: 2025-12-25
## Status: 🏗️ DESIGN DOCUMENT

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Multi-Tenant Architecture](#multi-tenant-architecture)
3. [Database Schema](#database-schema)
4. [Tenant Isolation](#tenant-isolation)
5. [User Roles & Permissions](#user-roles--permissions)
6. [API Design](#api-design)
7. [Frontend Architecture](#frontend-architecture)
8. [Security Considerations](#security-considerations)
9. [Deployment Strategy](#deployment-strategy)
10. [Scalability & Performance](#scalability--performance)

---

## 1. Overview

### What is Multi-Tenant POS?

**Multi-tenant** = Satu aplikasi melayani **banyak tenant** (bisnis/restoran) yang berbeda.

**Example Use Cases**:
- 🍔 **Restoran Chain**: McDonald's dengan 100+ cabang
- ☕ **Franchise**: Kopi Kenangan, Janji Jiwa (independen tapi satu sistem)
- 🏪 **SaaS POS**: Satu platform untuk 1000+ usaha kecil berbeda

### Key Requirements

1. **Data Isolation** - Tenant A tidak bisa lihat data Tenant B
2. **Customization** - Setiap tenant bisa punya branding/menu sendiri
3. **Scalability** - Bisa handle 1000+ tenants dalam satu database
4. **Performance** - Query cepat meskipun banyak tenant
5. **Cost Efficiency** - Shared infrastructure (hemat resource)

---

## 2. Multi-Tenant Architecture

### Architecture Patterns

Ada 3 pola utama multi-tenancy:

#### Pattern 1: Shared Database + Shared Schema ✅ (DIPILIH)

```
┌─────────────────────────────────────┐
│         Single Database             │
├─────────────────────────────────────┤
│  Table: products                    │
│  ┌────┬──────────┬───────┬────────┐│
│  │ id │tenant_id │ name  │ price  ││
│  ├────┼──────────┼───────┼────────┤│
│  │ 1  │    1     │ Nasi  │ 25000  ││ ← Tenant 1
│  │ 2  │    1     │ Mie   │ 20000  ││ ← Tenant 1
│  │ 3  │    2     │ Pizza │ 50000  ││ ← Tenant 2
│  │ 4  │    2     │ Pasta │ 45000  ││ ← Tenant 2
│  └────┴──────────┴───────┴────────┘│
└─────────────────────────────────────┘
```

**Pros**:
- ✅ Paling cost-efficient (satu database untuk semua)
- ✅ Easy maintenance (satu migration untuk semua tenant)
- ✅ Scalable hingga 10,000+ tenants
- ✅ Backup & restore simple

**Cons**:
- ⚠️ Harus hati-hati query filtering (pastikan selalu ada `tenant_id`)
- ⚠️ Risk: Bug bisa expose data tenant lain (butuh testing ketat)

#### Pattern 2: Shared Database + Separate Schema

```
┌─────────────────────────────────────┐
│         Single Database             │
├─────────────────────────────────────┤
│  Schema: tenant_1                   │
│  ├─ products                        │
│  ├─ orders                          │
│  └─ payments                        │
│                                     │
│  Schema: tenant_2                   │
│  ├─ products                        │
│  ├─ orders                          │
│  └─ payments                        │
└─────────────────────────────────────┘
```

**Pros**:
- ✅ Better isolation (separate schemas)
- ✅ Easier to migrate single tenant

**Cons**:
- ❌ Complex migrations (run untuk setiap schema)
- ❌ Harder to do cross-tenant analytics

#### Pattern 3: Separate Database per Tenant

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   DB: T1     │  │   DB: T2     │  │   DB: T3     │
│ - products   │  │ - products   │  │ - products   │
│ - orders     │  │ - orders     │  │ - orders     │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Pros**:
- ✅ Complete isolation
- ✅ Can have different DB versions per tenant
- ✅ Easy to backup/restore single tenant

**Cons**:
- ❌ Very expensive (butuh banyak database servers)
- ❌ Hard to maintain (migrations manual per tenant)
- ❌ Not scalable untuk banyak tenant

### Our Choice: Pattern 1 ✅

**Reason**: 
- Cost-effective untuk POS kecil-menengah
- Already implemented di current codebase
- Django has excellent multi-tenant support

---

## 3. Database Schema

### Core Tables

#### 3.1 Tenants Table

```sql
CREATE TABLE tenants_tenant (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Contact Info
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    
    -- Billing
    subscription_plan VARCHAR(50),  -- 'free', 'basic', 'premium', 'enterprise'
    subscription_status VARCHAR(20), -- 'active', 'suspended', 'cancelled'
    trial_ends_at TIMESTAMP,
    
    -- Tax & Service Charge
    tax_rate DECIMAL(5,2) DEFAULT 10.00,
    service_charge_rate DECIMAL(5,2) DEFAULT 5.00,
    
    -- Settings (JSON)
    settings JSONB DEFAULT '{}',
    
    -- Branding
    logo_url VARCHAR(500),
    primary_color VARCHAR(7),
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast lookup
CREATE INDEX idx_tenants_slug ON tenants_tenant(slug);
CREATE INDEX idx_tenants_active ON tenants_tenant(is_active);
```

**Example Data**:
```json
{
  "id": 1,
  "slug": "warung-makan-sedap",
  "name": "Warung Makan Sedap",
  "phone": "021-12345678",
  "email": "owner@warungedap.com",
  "subscription_plan": "premium",
  "tax_rate": 10.00,
  "service_charge_rate": 5.00,
  "settings": {
    "currency": "IDR",
    "timezone": "Asia/Jakarta",
    "language": "id",
    "receipt_footer": "Terima kasih!"
  }
}
```

#### 3.2 Outlets Table (Multi-Location)

```sql
CREATE TABLE tenants_outlet (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants_tenant(id) ON DELETE CASCADE,
    slug VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    
    -- Address
    address TEXT NOT NULL,
    city VARCHAR(100),
    province VARCHAR(100),
    postal_code VARCHAR(10),
    country VARCHAR(2) DEFAULT 'ID',
    
    -- Contact
    phone VARCHAR(20),
    email VARCHAR(255),
    
    -- Geolocation
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Operating Hours (JSON)
    operating_hours JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, slug)
);

CREATE INDEX idx_outlets_tenant ON tenants_outlet(tenant_id);
CREATE INDEX idx_outlets_active ON tenants_outlet(tenant_id, is_active);
```

**Example Data**:
```json
{
  "id": 1,
  "tenant_id": 1,
  "slug": "cabang-pusat",
  "name": "Cabang Pusat - Sudirman",
  "address": "Jl. Sudirman No. 123",
  "city": "Jakarta Pusat",
  "latitude": -6.208763,
  "longitude": 106.845599,
  "operating_hours": {
    "monday": {"open": "08:00", "close": "22:00"},
    "tuesday": {"open": "08:00", "close": "22:00"},
    "sunday": {"open": "10:00", "close": "20:00"}
  }
}
```

#### 3.3 Users Table (Multi-Tenant Users)

```sql
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    
    -- Tenant Association
    tenant_id INTEGER REFERENCES tenants_tenant(id) ON DELETE CASCADE,
    default_outlet_id INTEGER REFERENCES tenants_outlet(id),
    
    -- Role
    role VARCHAR(20) NOT NULL, -- 'owner', 'admin', 'cashier', 'kitchen', 'waiter'
    
    -- Profile
    full_name VARCHAR(200),
    phone_number VARCHAR(20),
    
    -- Permissions (JSON)
    permissions JSONB DEFAULT '[]',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_tenant ON users_user(tenant_id);
CREATE INDEX idx_users_outlet ON users_user(default_outlet_id);
CREATE INDEX idx_users_role ON users_user(tenant_id, role);
```

#### 3.4 Products Table (Tenant-Specific)

```sql
CREATE TABLE products_product (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants_tenant(id) ON DELETE CASCADE,
    
    -- Product Info
    sku VARCHAR(100),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES products_category(id),
    
    -- Pricing
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),  -- For profit calculation
    
    -- Stock
    track_stock BOOLEAN DEFAULT FALSE,
    stock_quantity INTEGER DEFAULT 0,
    low_stock_alert INTEGER DEFAULT 5,
    
    -- Media
    image VARCHAR(500),
    
    -- Status
    is_available BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    preparation_time INTEGER,  -- in minutes
    calories INTEGER,
    tags JSONB DEFAULT '[]',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, sku)
);

CREATE INDEX idx_products_tenant ON products_product(tenant_id);
CREATE INDEX idx_products_category ON products_product(tenant_id, category_id);
CREATE INDEX idx_products_available ON products_product(tenant_id, is_available);
```

#### 3.5 Orders Table (Multi-Outlet)

```sql
CREATE TABLE orders_order (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants_tenant(id) ON DELETE CASCADE,
    outlet_id INTEGER NOT NULL REFERENCES tenants_outlet(id),
    
    -- Order Info
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_type VARCHAR(20), -- 'dine_in', 'takeaway', 'delivery', 'kiosk'
    table_number VARCHAR(20),
    
    -- Customer (optional)
    customer_name VARCHAR(200),
    customer_phone VARCHAR(20),
    customer_notes TEXT,
    
    -- Pricing
    subtotal DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) DEFAULT 0,
    service_charge DECIMAL(10, 2) DEFAULT 0,
    discount DECIMAL(10, 2) DEFAULT 0,
    total DECIMAL(10, 2) NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', 
    -- 'pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled'
    
    payment_status VARCHAR(20) DEFAULT 'unpaid',
    -- 'unpaid', 'partial', 'paid', 'refunded'
    
    -- Staff
    cashier_id INTEGER REFERENCES users_user(id),
    waiter_id INTEGER REFERENCES users_user(id),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_orders_tenant ON orders_order(tenant_id);
CREATE INDEX idx_orders_outlet ON orders_order(outlet_id);
CREATE INDEX idx_orders_number ON orders_order(order_number);
CREATE INDEX idx_orders_status ON orders_order(tenant_id, status);
CREATE INDEX idx_orders_date ON orders_order(tenant_id, created_at);
```

#### 3.6 Order Items Table

```sql
CREATE TABLE orders_orderitem (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products_product(id),
    
    -- Item Details
    product_name VARCHAR(200) NOT NULL,  -- Snapshot at order time
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    
    -- Modifiers (JSON)
    modifiers JSONB DEFAULT '[]',
    -- Example: [{"name": "Extra Pedas", "price": 0}, {"name": "Extra Telur", "price": 5000}]
    
    -- Special Instructions
    notes TEXT,
    
    -- Kitchen Status
    kitchen_status VARCHAR(20) DEFAULT 'pending',
    -- 'pending', 'preparing', 'ready', 'served'
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_order_items_order ON orders_orderitem(order_id);
CREATE INDEX idx_order_items_product ON orders_orderitem(product_id);
```

#### 3.7 Payments Table

```sql
CREATE TABLE payments_payment (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants_tenant(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL REFERENCES orders_order(id),
    
    -- Payment Info
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    external_id VARCHAR(200),  -- From payment gateway
    
    -- Method & Provider
    payment_method VARCHAR(50), -- 'cash', 'qris', 'gopay', 'ovo', 'card'
    payment_provider VARCHAR(50), -- 'midtrans', 'xendit', 'stripe', NULL (for cash)
    
    -- Amount
    amount DECIMAL(10, 2) NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    -- 'pending', 'processing', 'success', 'failed', 'expired', 'refunded'
    
    -- Gateway Response
    gateway_response JSONB,
    
    -- QR Code / Payment URL (for digital payments)
    qr_code_url VARCHAR(500),
    payment_url VARCHAR(500),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP,
    expired_at TIMESTAMP
);

CREATE INDEX idx_payments_tenant ON payments_payment(tenant_id);
CREATE INDEX idx_payments_order ON payments_payment(order_id);
CREATE INDEX idx_payments_transaction ON payments_payment(transaction_id);
CREATE INDEX idx_payments_status ON payments_payment(tenant_id, status);
```

### Key Multi-Tenant Patterns

#### Pattern 1: Every Table Has `tenant_id`

```sql
-- ✅ GOOD: All tenant-specific tables have tenant_id
CREATE TABLE products_product (
    tenant_id INTEGER NOT NULL REFERENCES tenants_tenant(id),
    ...
);

CREATE TABLE orders_order (
    tenant_id INTEGER NOT NULL REFERENCES tenants_tenant(id),
    ...
);
```

#### Pattern 2: Foreign Keys Still Reference Main IDs

```sql
-- ✅ GOOD: Reference by ID, but always filter by tenant_id
CREATE TABLE orders_orderitem (
    order_id INTEGER REFERENCES orders_order(id),
    product_id INTEGER REFERENCES products_product(id)
);

-- Query always includes tenant check
SELECT * FROM orders_orderitem oi
JOIN orders_order o ON oi.order_id = o.id
WHERE o.tenant_id = 1;  -- ← CRITICAL!
```

#### Pattern 3: Composite Unique Constraints

```sql
-- ✅ GOOD: Unique per tenant
CREATE TABLE products_product (
    tenant_id INTEGER NOT NULL,
    sku VARCHAR(100),
    UNIQUE(tenant_id, sku)  -- ← Tenant 1 dan Tenant 2 bisa punya SKU yang sama
);
```

---

## 4. Tenant Isolation

### Middleware-Based Isolation

**Django Middleware** automatically adds tenant filter ke semua queries.

```python
# backend/apps/tenants/middleware.py

class TenantMiddleware:
    """
    Middleware untuk auto-detect tenant dari:
    1. Subdomain (tenant1.pos.com)
    2. Header (X-Tenant-ID)
    3. JWT Token (tenant_id in claims)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 1. Get tenant dari subdomain
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        
        # 2. Atau dari header
        tenant_id = request.headers.get('X-Tenant-ID')
        
        # 3. Atau dari JWT token
        if hasattr(request, 'user') and request.user.is_authenticated:
            tenant_id = request.user.tenant_id
        
        # Set tenant di request
        if tenant_id:
            try:
                request.tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                return HttpResponse('Tenant not found', status=404)
        
        # Set tenant di thread local (untuk auto-filtering)
        set_current_tenant(request.tenant)
        
        response = self.get_response(request)
        return response
```

### Model Manager Auto-Filtering

```python
# backend/apps/core/models.py

class TenantManager(models.Manager):
    """
    Manager yang otomatis filter berdasarkan tenant
    """
    
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant:
            return qs.filter(tenant=tenant)
        
        # Superuser bisa lihat semua tenant
        if hasattr(self, 'request') and self.request.user.is_superuser:
            return qs
        
        # Default: return empty untuk keamanan
        return qs.none()


class TenantModel(models.Model):
    """
    Base model untuk semua model yang tenant-specific
    """
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    
    objects = TenantManager()  # Default manager dengan auto-filtering
    all_objects = models.Manager()  # Bypass filter (untuk admin/superuser)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        # Auto-set tenant dari current request
        if not self.tenant_id:
            self.tenant = get_current_tenant()
        super().save(*args, **kwargs)
```

### Usage Example

```python
# ✅ AUTOMATICALLY FILTERED BY TENANT

# Model definition
class Product(TenantModel):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# View - tenant sudah auto-filtered!
def get_products(request):
    products = Product.objects.all()  # ← Only returns current tenant's products!
    return JsonResponse({'products': list(products.values())})

# ❌ BYPASS FILTER (ONLY FOR SUPERUSER)
all_products = Product.all_objects.all()  # Gets products from ALL tenants
```

---

## 5. User Roles & Permissions

### Role Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                      SYSTEM ADMIN                       │
│              (Super User - Multi-Tenant)                │
│  - Can access ALL tenants                               │
│  - Can create/suspend tenants                           │
│  - Can view all analytics                               │
└─────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │             TENANT OWNER                       │     │
│  │  - Can manage tenant settings                  │     │
│  │  - Can create outlets                          │     │
│  │  - Can add/remove users                        │     │
│  │  - Full access to all tenant data              │     │
│  └────────────────────────────────────────────────┘     │
│                            │                             │
│  ┌────────────────────────┴───────────────────────┐     │
│  │                                                 │     │
│  │  ┌─────────────────┐      ┌─────────────────┐  │     │
│  │  │  ADMIN          │      │  MANAGER        │  │     │
│  │  │  - Manage menu  │      │  - View reports │  │     │
│  │  │  - View reports │      │  - Manage staff │  │     │
│  │  │  - Manage users │      │  - Inventory    │  │     │
│  │  └─────────────────┘      └─────────────────┘  │     │
│  │                                                 │     │
│  │  ┌─────────────────┐      ┌─────────────────┐  │     │
│  │  │  CASHIER        │      │  KITCHEN STAFF  │  │     │
│  │  │  - Create orders│      │  - View orders  │  │     │
│  │  │  - Process pay  │      │  - Update status│  │     │
│  │  │  - Basic reports│      │  - Mark ready   │  │     │
│  │  └─────────────────┘      └─────────────────┘  │     │
│  │                                                 │     │
│  │  ┌─────────────────┐                            │     │
│  │  │  WAITER         │                            │     │
│  │  │  - Take orders  │                            │     │
│  │  │  - View menu    │                            │     │
│  │  │  - Serve tables │                            │     │
│  │  └─────────────────┘                            │     │
│  └─────────────────────────────────────────────────┘     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Permission Matrix

| Feature | Owner | Admin | Manager | Cashier | Kitchen | Waiter |
|---------|-------|-------|---------|---------|---------|--------|
| **Tenant Settings** |
| Edit tenant info | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage subscription | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Create outlets | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **User Management** |
| Add/remove users | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Assign roles | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Menu Management** |
| Create/edit products | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Create categories | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Set prices | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Upload images | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Orders** |
| Create orders | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| View all orders | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cancel orders | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modify orders | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Kitchen** |
| View kitchen orders | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| Update order status | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Payments** |
| Process payments | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Refund payments | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Reports** |
| View all reports | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| View sales reports | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Export data | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Inventory** |
| Manage stock | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| View stock | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

### Permission Implementation

```python
# backend/apps/users/permissions.py

class TenantPermission:
    """
    Permission checker untuk tenant-specific actions
    """
    
    PERMISSIONS = {
        'owner': [
            'tenant.edit',
            'tenant.delete',
            'outlet.create',
            'outlet.edit',
            'user.create',
            'user.edit',
            'user.delete',
            'product.create',
            'product.edit',
            'product.delete',
            'order.create',
            'order.edit',
            'order.delete',
            'payment.process',
            'payment.refund',
            'report.view_all',
            'report.export',
        ],
        'admin': [
            'outlet.create',
            'user.create',
            'user.edit',
            'product.create',
            'product.edit',
            'order.create',
            'order.edit',
            'payment.process',
            'report.view_all',
        ],
        'manager': [
            'user.view',
            'product.create',
            'product.edit',
            'order.view',
            'report.view',
        ],
        'cashier': [
            'order.create',
            'order.view',
            'order.edit',
            'payment.process',
        ],
        'kitchen': [
            'order.view_kitchen',
            'order.update_status',
        ],
        'waiter': [
            'order.create',
            'order.view',
        ],
    }
    
    @classmethod
    def has_permission(cls, user, permission):
        """
        Check if user has specific permission
        """
        if user.is_superuser:
            return True
        
        role_permissions = cls.PERMISSIONS.get(user.role, [])
        return permission in role_permissions


# Usage in views
class ProductViewSet(viewsets.ModelViewSet):
    def create(self, request):
        if not TenantPermission.has_permission(request.user, 'product.create'):
            return Response({'error': 'Permission denied'}, status=403)
        
        # Create product...
```

---

## 6. API Design

### RESTful Endpoints

#### Base URL Structure

**Option 1: Header-Based** ✅ (RECOMMENDED)
```
POST /api/products/
Headers: 
  X-Tenant-ID: 123
  Authorization: Bearer <token>
```

**Option 2: Subdomain-Based**
```
POST https://tenant1.pos.example.com/api/products/
```

**Option 3: Path-Based**
```
POST /api/tenants/123/products/
```

### API Endpoints

#### Authentication

```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
POST /api/auth/refresh/
POST /api/auth/password/reset/
```

#### Tenant Management (Owner Only)

```http
GET    /api/tenants/                    # List all tenants (superuser only)
GET    /api/tenants/me/                 # Get current tenant info
POST   /api/tenants/                    # Create new tenant (superuser)
PATCH  /api/tenants/me/                 # Update current tenant
DELETE /api/tenants/{id}/               # Delete tenant (superuser)

# Outlets
GET    /api/outlets/                    # List outlets for current tenant
POST   /api/outlets/                    # Create outlet
GET    /api/outlets/{id}/               # Get outlet detail
PATCH  /api/outlets/{id}/               # Update outlet
DELETE /api/outlets/{id}/               # Delete outlet
```

#### User Management

```http
GET    /api/users/                      # List users in tenant
POST   /api/users/                      # Create user
GET    /api/users/{id}/                 # Get user detail
PATCH  /api/users/{id}/                 # Update user
DELETE /api/users/{id}/                 # Delete user
POST   /api/users/{id}/reset-password/  # Reset user password
```

#### Products

```http
GET    /api/products/categories/        # List categories
POST   /api/products/categories/        # Create category
GET    /api/products/products/          # List products
POST   /api/products/products/          # Create product
GET    /api/products/products/{id}/     # Get product detail
PATCH  /api/products/products/{id}/     # Update product
DELETE /api/products/products/{id}/     # Delete product
POST   /api/products/products/bulk/     # Bulk create products
```

#### Orders

```http
GET    /api/orders/                     # List orders
POST   /api/orders/                     # Create order
GET    /api/orders/{id}/                # Get order detail
PATCH  /api/orders/{id}/                # Update order
DELETE /api/orders/{id}/                # Cancel order
POST   /api/orders/{id}/confirm/        # Confirm order
POST   /api/orders/{id}/complete/       # Complete order

# Kitchen
GET    /api/orders/kitchen/             # Kitchen display orders
PATCH  /api/orders/{id}/kitchen-status/ # Update kitchen status
```

#### Payments

```http
GET    /api/payments/                   # List payments
POST   /api/payments/                   # Create payment
GET    /api/payments/{id}/              # Get payment detail
POST   /api/payments/{id}/verify/       # Verify payment status
POST   /api/payments/webhooks/midtrans/ # Midtrans webhook
POST   /api/payments/webhooks/xendit/   # Xendit webhook
```

#### Reports

```http
GET    /api/reports/sales-summary/      # Sales summary
GET    /api/reports/sales-by-category/  # Sales by category
GET    /api/reports/sales-by-product/   # Top selling products
GET    /api/reports/sales-by-period/    # Sales by date range
GET    /api/reports/cashier-performance/ # Cashier performance
POST   /api/reports/export/             # Export to CSV/Excel
```

### Example API Responses

#### Product List

```http
GET /api/products/products/
Headers:
  X-Tenant-ID: 1
  Authorization: Bearer eyJ0eXAi...

Response:
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant_id": 1,
      "sku": "P001",
      "name": "Nasi Goreng Spesial",
      "description": "Nasi goreng dengan telur dan ayam",
      "category": 1,
      "category_name": "Main Course",
      "price": "25000.00",
      "cost": "15000.00",
      "image": "https://cdn.example.com/products/nasi-goreng.jpg",
      "is_available": true,
      "is_featured": true,
      "stock_quantity": 50,
      "modifiers": [
        {
          "id": 1,
          "name": "Extra Pedas",
          "type": "spice_level",
          "price_adjustment": "0.00"
        }
      ]
    }
  ]
}
```

#### Order Create

```http
POST /api/orders/
Headers:
  X-Tenant-ID: 1
  X-Outlet-ID: 1
  Authorization: Bearer eyJ0eXAi...

Request Body:
{
  "order_type": "dine_in",
  "table_number": "A-05",
  "customer_name": "John Doe",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "modifiers": [
        {"id": 1, "name": "Extra Pedas"}
      ],
      "notes": "Tidak pakai bawang"
    },
    {
      "product_id": 5,
      "quantity": 1
    }
  ]
}

Response:
{
  "id": 101,
  "tenant_id": 1,
  "outlet_id": 1,
  "order_number": "ORD-20251225-0101",
  "order_type": "dine_in",
  "table_number": "A-05",
  "customer_name": "John Doe",
  "items": [
    {
      "id": 201,
      "product_id": 1,
      "product_name": "Nasi Goreng Spesial",
      "quantity": 2,
      "unit_price": "25000.00",
      "subtotal": "50000.00",
      "modifiers": [
        {"name": "Extra Pedas", "price": "0.00"}
      ]
    },
    {
      "id": 202,
      "product_id": 5,
      "product_name": "Es Teh Manis",
      "quantity": 1,
      "unit_price": "5000.00",
      "subtotal": "5000.00"
    }
  ],
  "subtotal": "55000.00",
  "tax": "5500.00",
  "service_charge": "2750.00",
  "total": "63250.00",
  "status": "pending",
  "payment_status": "unpaid",
  "created_at": "2025-12-25T10:30:00Z"
}
```

---

## 7. Frontend Architecture

### Tenant Context

```javascript
// frontend/src/lib/stores/tenant.js

import { writable } from 'svelte/store';

export const currentTenant = writable(null);
export const currentOutlet = writable(null);

export async function loadTenant() {
    const response = await fetch('/api/tenants/me/');
    const tenant = await response.json();
    currentTenant.set(tenant);
}

export async function loadOutlet(outletId) {
    const response = await fetch(`/api/outlets/${outletId}/`);
    const outlet = await response.json();
    currentOutlet.set(outlet);
}
```

### Multi-Tenant UI

```svelte
<!-- frontend/src/routes/+layout.svelte -->
<script>
    import { onMount } from 'svelte';
    import { currentTenant, loadTenant } from '$lib/stores/tenant';
    
    onMount(async () => {
        await loadTenant();
    });
</script>

{#if $currentTenant}
    <header style="background-color: {$currentTenant.primary_color}">
        <img src={$currentTenant.logo_url} alt={$currentTenant.name} />
        <h1>{$currentTenant.name}</h1>
    </header>
    
    <slot />
{:else}
    <p>Loading tenant...</p>
{/if}
```

### Outlet Selector

```svelte
<!-- frontend/src/lib/components/OutletSelector.svelte -->
<script>
    import { currentOutlet } from '$lib/stores/tenant';
    
    export let outlets = [];
    
    function selectOutlet(outlet) {
        currentOutlet.set(outlet);
        localStorage.setItem('outlet_id', outlet.id);
    }
</script>

<select on:change={(e) => selectOutlet(outlets[e.target.value])}>
    {#each outlets as outlet, i}
        <option value={i}>
            {outlet.name} - {outlet.city}
        </option>
    {/each}
</select>
```

---

## 8. Security Considerations

### Row-Level Security

```python
# ALWAYS enforce tenant filtering
def get_products(request):
    tenant = request.tenant  # From middleware
    products = Product.objects.filter(tenant=tenant)  # ✅ Safe
    
    # ❌ NEVER do this (exposes all tenants):
    products = Product.objects.all()
```

### SQL Injection Prevention

```python
# ✅ GOOD: Use ORM
Product.objects.filter(tenant_id=tenant_id, sku=sku)

# ❌ BAD: Raw SQL without parameterization
cursor.execute(f"SELECT * FROM products WHERE sku = '{sku}'")

# ✅ GOOD: Parameterized raw SQL
cursor.execute("SELECT * FROM products WHERE tenant_id = %s AND sku = %s", [tenant_id, sku])
```

### API Rate Limiting

```python
# Per-tenant rate limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
        'apps.core.throttling.TenantRateThrottle',  # Custom
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/hour',  # Per user
        'anon': '100/hour',   # Per IP
        'tenant': '10000/hour',  # Per tenant
    }
}
```

### Data Backup Strategy

```bash
# Per-tenant backup script
#!/bin/bash

TENANT_ID=$1

pg_dump -h localhost -U pos_user pos_db \
  --table=tenants_tenant \
  --table=products_* \
  --table=orders_* \
  --table=payments_* \
  --where="tenant_id=$TENANT_ID" \
  > backup_tenant_${TENANT_ID}_$(date +%Y%m%d).sql
```

---

## 9. Deployment Strategy

### Environment-Based Deployment

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: pos_db
      POSTGRES_USER: pos_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://pos_user:${DB_PASSWORD}@db:5432/pos_db
      REDIS_URL: redis://redis:6379/0
      DJANGO_SETTINGS_MODULE: config.settings.production
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    environment:
      PUBLIC_API_URL: https://api.pos.example.com
    depends_on:
      - backend
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

### Scaling Strategy

```
┌────────────────────────────────────────────────────────┐
│                     LOAD BALANCER                      │
│                  (Nginx / AWS ALB)                     │
└────────────────────┬───────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐            ┌────▼────┐
    │ Backend │            │ Backend │
    │ Node 1  │            │ Node 2  │
    └────┬────┘            └────┬────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   PostgreSQL Master   │
         │   (Write Operations)  │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐            ┌────▼────┐
    │ PG Read │            │ PG Read │
    │ Replica │            │ Replica │
    └─────────┘            └─────────┘
```

---

## 10. Scalability & Performance

### Database Indexing Strategy

```sql
-- Critical indexes for multi-tenant queries
CREATE INDEX idx_products_tenant_available 
    ON products_product(tenant_id, is_available);

CREATE INDEX idx_orders_tenant_date 
    ON orders_order(tenant_id, created_at DESC);

CREATE INDEX idx_orders_tenant_status 
    ON orders_order(tenant_id, status, created_at);

-- Composite index for common queries
CREATE INDEX idx_orderitems_order_product 
    ON orders_orderitem(order_id, product_id);

-- Partial index for active tenants only
CREATE INDEX idx_tenants_active 
    ON tenants_tenant(id) 
    WHERE is_active = TRUE;
```

### Query Optimization

```python
# ❌ BAD: N+1 queries
orders = Order.objects.filter(tenant=tenant)
for order in orders:
    print(order.items.all())  # ← Query for each order!

# ✅ GOOD: Prefetch related
orders = Order.objects.filter(tenant=tenant).prefetch_related('items')
for order in orders:
    print(order.items.all())  # ← No additional queries!

# ✅ BETTER: Select related for foreign keys
orders = Order.objects.filter(tenant=tenant)\
    .select_related('outlet', 'cashier')\
    .prefetch_related('items__product')
```

### Caching Strategy

```python
from django.core.cache import cache

def get_tenant_products(tenant_id):
    cache_key = f'tenant_{tenant_id}_products'
    
    # Try cache first
    products = cache.get(cache_key)
    
    if products is None:
        # Cache miss - query DB
        products = Product.objects.filter(
            tenant_id=tenant_id,
            is_available=True
        ).values()
        
        # Cache for 5 minutes
        cache.set(cache_key, list(products), 300)
    
    return products
```

### Performance Monitoring

```python
# backend/apps/core/middleware.py

import time
from django.utils.deprecation import MiddlewareMixin

class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log slow queries (> 1 second)
            if duration > 1.0:
                logger.warning(
                    f"Slow request: {request.path} "
                    f"took {duration:.2f}s for tenant {request.tenant.id}"
                )
        
        return response
```

---

## 📊 Summary

### Key Benefits of Multi-Tenant Architecture

1. ✅ **Cost Efficiency**: Shared infrastructure untuk ribuan tenant
2. ✅ **Easy Maintenance**: Satu update untuk semua tenant
3. ✅ **Scalability**: Bisa grow sampai 10,000+ tenants
4. ✅ **Data Isolation**: Tenant A tidak bisa akses data Tenant B
5. ✅ **Customization**: Setiap tenant bisa punya branding sendiri
6. ✅ **Performance**: Optimized queries dengan proper indexing

### Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Database Schema | ✅ Complete | All tables have tenant_id |
| Models | ✅ Complete | TenantModel base class |
| Middleware | ✅ Complete | Auto-filtering by tenant |
| API Endpoints | ✅ Complete | RESTful with tenant context |
| Permissions | ✅ Complete | Role-based access control |
| Frontend | 🏗️ In Progress | Tenant context & branding |
| Testing | ⏳ Pending | Unit & integration tests |
| Documentation | ✅ Complete | This document! |

### Next Steps

1. ✅ **Implement Frontend Tenant Context**
2. ✅ **Add Outlet Selector UI**
3. ✅ **Implement Permission Checks**
4. ⏳ **Add Reports & Analytics**
5. ⏳ **Implement Backup Strategy**
6. ⏳ **Load Testing**
7. ⏳ **Security Audit**

---

**GitHub**: https://github.com/dadinjaenudin/kiosk-svelte  
**Status**: 🟢 Multi-Tenant Architecture Designed & Ready  
**Date**: 2025-12-25

---

*This document serves as the complete blueprint for the multi-tenant POS system. All implementations should follow these patterns for consistency and security.*
