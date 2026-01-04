# 04 - DATABASE SCHEMA

## Overview

Database Kiosk POS menggunakan **PostgreSQL 15** dengan pattern **Row-Level Multi-Tenancy**. Setiap tabel yang tenant-specific memiliki `tenant_id` foreign key untuk isolasi data.

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MULTI-TENANT CORE                                │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   TENANT     │
│──────────────│
│ id (PK)      │◄──┐
│ name         │   │
│ slug (UQ)    │   │
│ logo         │   │
│ tax_rate     │   │
└──────────────┘   │
        │          │
        │ 1        │
        │          │
        ▼ N        │
┌──────────────┐   │
│   OUTLET     │   │
│──────────────│   │
│ id (PK)      │   │
│ tenant_id(FK)├───┘
│ name         │
│ address      │
│ phone        │
│ websocket_url│
└──────────────┘
        │
        │ 1
        │
        ▼ N

┌─────────────────────────────────────────────────────────────────────────┐
│                         USER & AUTHENTICATION                            │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│      USER        │
│──────────────────│
│ id (PK)          │
│ username (UQ)    │
│ email            │
│ password         │
│ role             │◄─── Choices: super_admin, admin, tenant_owner,
│ tenant_id (FK)   │               manager, cashier, kitchen
│ outlet_id (FK)   │
│ accessible_outlets│ ── M2M → Outlet (for managers)
└──────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         PRODUCT MANAGEMENT                               │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐
│  CATEGORY    │ 1     N │   PRODUCT    │
│──────────────│◄────────│──────────────│
│ id (PK)      │         │ id (PK)      │
│ tenant_id(FK)│         │ tenant_id(FK)│
│ name         │         │ category_id  │
│ description  │         │ sku (UQ)     │
│ image        │         │ name         │
└──────────────┘         │ description  │
                         │ image        │
                         │ price        │
                         │ cost         │
                         │ stock        │
                         └──────────────┘
                                │
                                │ 1
                                │
                                ▼ N
                         ┌──────────────────┐
                         │ PRODUCT_MODIFIER │
                         │──────────────────│
                         │ id (PK)          │
                         │ product_id (FK)  │
                         │ name             │
                         │ type             │◄─── size, topping, spicy, extra
                         │ price_modifier   │
                         └──────────────────┘

                         ┌──────────────────┐
                         │ OUTLET_PRODUCT   │◄─── Per-outlet pricing
                         │──────────────────│
                         │ id (PK)          │
                         │ outlet_id (FK)   │
                         │ product_id (FK)  │
                         │ price_override   │
                         │ is_available     │
                         │ stock            │
                         └──────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         ORDER PROCESSING                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│     ORDER        │ 1     N │   ORDER_ITEM     │
│──────────────────│◄────────│──────────────────│
│ id (PK)          │         │ id (PK)          │
│ tenant_id (FK)   │         │ order_id (FK)    │
│ outlet_id (FK)   │         │ product_id (FK)  │
│ order_number(UQ) │         │ product_name     │◄─── Snapshot
│ status           │         │ product_sku      │◄─── Snapshot
│ customer_name    │         │ quantity         │
│ customer_phone   │         │ unit_price       │
│ subtotal         │         │ total_price      │
│ tax_amount       │         │ modifiers        │◄─── JSON array
│ service_charge   │         │ modifiers_price  │
│ discount_amount  │         │ notes            │
│ total_amount     │         └──────────────────┘
│ payment_status   │
│ source           │◄─── kiosk, web, cashier
│ cashier_id (FK)  │
│ created_at       │
└──────────────────┘
        │
        │ 1
        │
        ▼ N
┌──────────────────┐
│    PAYMENT       │
│──────────────────│
│ id (PK)          │
│ order_id (FK)    │
│ transaction_id(UQ│
│ external_id      │◄─── Payment gateway reference
│ payment_method   │◄─── cash, qris, gopay, card, etc.
│ provider         │◄─── midtrans, xendit, stripe
│ amount           │
│ status           │
│ metadata         │◄─── JSON
│ qr_code_url      │
│ redirect_url     │
│ paid_at          │
└──────────────────┘
        │
        │ 1
        │
        ▼ N
┌──────────────────┐
│ PAYMENT_CALLBACK │◄─── Webhook logs
│──────────────────│
│ id (PK)          │
│ payment_id (FK)  │
│ provider         │
│ payload          │◄─── JSON
│ processed        │
│ processed_at     │
└──────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         PROMOTION ENGINE                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────┐
│    PROMOTION      │
│───────────────────│
│ id (PK)           │
│ tenant_id (FK)    │
│ name              │
│ code (UQ)         │
│ promo_type        │◄─── percentage, fixed, buy_x_get_y, bundle
│ discount_value    │
│ min_purchase_amt  │
│ min_quantity      │◄─── For buy_x_get_y
│ start_date        │
│ end_date          │
│ is_active         │
│ usage_count       │
│ max_usage         │
└───────────────────┘
        │
        │ M
        │
        ▼ N
┌──────────────────────┐
│ PROMOTION_PRODUCT    │◄─── Many-to-many junction table
│──────────────────────│
│ id (PK)              │
│ promotion_id (FK)    │
│ product_id (FK)      │
│ product_role         │◄─── 'buy', 'get', 'both' for buy_x_get_y
│ discount_override    │
│ priority             │
└──────────────────────┘
        ▲
        │ N
        │
        │ M
┌──────────────────┐
│    PRODUCT       │
│ (referenced)     │
└──────────────────┘

┌───────────────────┐
│ PROMOTION_USAGE   │◄─── Track usage per customer
│───────────────────│
│ id (PK)           │
│ promotion_id (FK) │
│ order_id (FK)     │
│ customer_id_field │◄─── Customer phone/email/session
│ discount_applied  │
│ created_at        │
└───────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         CUSTOMER MANAGEMENT                              │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│     CUSTOMER         │
│──────────────────────│
│ id (PK)              │
│ tenant_id (FK)       │
│ name                 │
│ email                │
│ phone (indexed)      │◄─── Unique per tenant
│ gender               │
│ date_of_birth        │
│ address              │
│ city                 │
│ postal_code          │
│ membership_number(UQ)│◄─── CUST-XXXXXXXX
│ membership_tier      │◄─── regular, silver, gold, platinum
│ points               │
│ preferred_outlet_id  │
│ notes                │
│ marketing_consent    │
│ is_active            │
└──────────────────────┘
```

---

## Table Schemas

### 1. Tenant & Outlet Tables

#### `tenants`
```sql
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    logo VARCHAR(255),
    primary_color VARCHAR(7) DEFAULT '#FF6B35',
    secondary_color VARCHAR(7) DEFAULT '#F7931E',
    phone VARCHAR(20),
    email VARCHAR(254),
    website VARCHAR(200),
    tax_rate DECIMAL(5,2) DEFAULT 10.00,
    service_charge_rate DECIMAL(5,2) DEFAULT 5.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_is_active ON tenants(is_active);
```

#### `outlets`
```sql
CREATE TABLE outlets (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100),
    province VARCHAR(100),
    postal_code VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(254),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    opening_time TIME,
    closing_time TIME,
    websocket_url VARCHAR(255) DEFAULT 'http://localhost:3002',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, slug)
);

CREATE INDEX idx_outlets_tenant ON outlets(tenant_id);
CREATE INDEX idx_outlets_is_active ON outlets(is_active);
```

---

### 2. User Table

#### `users_user`
```sql
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254),
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    role VARCHAR(20) DEFAULT 'cashier',
    -- Choices: super_admin, admin, tenant_owner, manager, cashier, kitchen
    phone_number VARCHAR(20),
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    outlet_id INTEGER REFERENCES outlets(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-many for accessible outlets (managers)
CREATE TABLE users_user_accessible_outlets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users_user(id) ON DELETE CASCADE,
    outlet_id INTEGER REFERENCES outlets(id) ON DELETE CASCADE,
    UNIQUE(user_id, outlet_id)
);

CREATE INDEX idx_users_username ON users_user(username);
CREATE INDEX idx_users_tenant ON users_user(tenant_id);
CREATE INDEX idx_users_outlet ON users_user(outlet_id);
CREATE INDEX idx_users_role ON users_user(role);
```

---

### 3. Product Tables

#### `categories`
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    image VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_tenant ON categories(tenant_id);
CREATE INDEX idx_categories_active ON categories(is_active);
```

#### `products`
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    outlet_id INTEGER REFERENCES outlets(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    image VARCHAR(255),
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) DEFAULT 0,
    track_inventory BOOLEAN DEFAULT FALSE,
    stock INTEGER DEFAULT 0,
    low_stock_alert INTEGER DEFAULT 10,
    is_available BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_taxable BOOLEAN DEFAULT TRUE,
    is_customizable BOOLEAN DEFAULT FALSE,
    discount_price DECIMAL(10,2),
    preparation_time INTEGER DEFAULT 10,
    calories INTEGER,
    allergens VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_tenant ON products(tenant_id);
CREATE INDEX idx_products_category ON products(tenant_id, category_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_available ON products(is_available);
```

#### `product_modifiers`
```sql
CREATE TABLE product_modifiers (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) DEFAULT 'extra',
    -- Choices: size, topping, spicy, extra, sauce
    price_modifier DECIMAL(10,2) DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0
);

CREATE INDEX idx_modifiers_product ON product_modifiers(product_id);
```

#### `outlet_products`
```sql
CREATE TABLE outlet_products (
    id SERIAL PRIMARY KEY,
    outlet_id INTEGER NOT NULL REFERENCES outlets(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price_override DECIMAL(10,2),
    is_available BOOLEAN DEFAULT TRUE,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(outlet_id, product_id)
);

CREATE INDEX idx_outlet_products ON outlet_products(outlet_id, product_id);
```

---

### 4. Order Tables

#### `orders`
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    outlet_id INTEGER NOT NULL REFERENCES outlets(id) ON DELETE CASCADE,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    -- Choices: draft, pending, confirmed, preparing, ready, served, completed, cancelled
    customer_name VARCHAR(200),
    customer_phone VARCHAR(20),
    customer_email VARCHAR(254),
    table_number VARCHAR(20),
    notes TEXT,
    subtotal DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    service_charge DECIMAL(12,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    payment_status VARCHAR(20) DEFAULT 'unpaid',
    paid_amount DECIMAL(12,2) DEFAULT 0,
    source VARCHAR(20) DEFAULT 'web',
    -- Choices: kiosk, web, cashier
    device_id VARCHAR(50),
    cashier_id INTEGER REFERENCES users_user(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_orders_number ON orders(order_number);
CREATE INDEX idx_orders_tenant ON orders(tenant_id);
CREATE INDEX idx_orders_outlet ON orders(outlet_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_source ON orders(source);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
CREATE INDEX idx_orders_outlet_created ON orders(outlet_id, created_at DESC);
```

#### `order_items`
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE PROTECT,
    product_name VARCHAR(200),  -- Snapshot
    product_sku VARCHAR(50),    -- Snapshot
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(12,2),
    modifiers JSONB DEFAULT '[]',
    modifiers_price DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

---

### 5. Payment Tables

#### `payments`
```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    external_id VARCHAR(200),
    payment_method VARCHAR(20),
    -- Choices: cash, qris, gopay, ovo, shopeepay, dana, debit_card, credit_card
    provider VARCHAR(50),
    amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    -- Choices: pending, processing, success, failed, cancelled, refunded
    metadata JSONB DEFAULT '{}',
    qr_code_url VARCHAR(200),
    redirect_url VARCHAR(200),
    error_message TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,
    expired_at TIMESTAMP
);

CREATE INDEX idx_payments_transaction ON payments(transaction_id);
CREATE INDEX idx_payments_external ON payments(external_id);
CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created ON payments(created_at DESC);
```

#### `payment_callbacks`
```sql
CREATE TABLE payment_callbacks (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER REFERENCES payments(id) ON DELETE CASCADE,
    provider VARCHAR(50),
    payload JSONB DEFAULT '{}',
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_callbacks_payment ON payment_callbacks(payment_id);
CREATE INDEX idx_callbacks_processed ON payment_callbacks(processed);
```

---

### 6. Promotion Tables

#### `promotions`
```sql
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    code VARCHAR(50) UNIQUE,
    promo_type VARCHAR(20) DEFAULT 'percentage',
    -- Choices: percentage, fixed_amount, buy_x_get_y, bundle_deal
    discount_value DECIMAL(10,2) NOT NULL,
    min_purchase_amount DECIMAL(10,2) DEFAULT 0,
    min_quantity INTEGER,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    -- Day of week availability (JSON array)
    available_days JSONB DEFAULT '["mon","tue","wed","thu","fri","sat","sun"]',
    start_time TIME,
    end_time TIME,
    max_usage INTEGER,
    max_usage_per_customer INTEGER,
    usage_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    -- Choices: draft, scheduled, active, expired, paused
    is_active BOOLEAN DEFAULT FALSE,
    is_stackable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users_user(id) ON DELETE SET NULL
);

CREATE INDEX idx_promotions_tenant ON promotions(tenant_id);
CREATE INDEX idx_promotions_code ON promotions(code);
CREATE INDEX idx_promotions_dates ON promotions(start_date, end_date);
CREATE INDEX idx_promotions_active ON promotions(is_active, status);
```

#### `promotion_products`
```sql
CREATE TABLE promotion_products (
    id SERIAL PRIMARY KEY,
    promotion_id INTEGER NOT NULL REFERENCES promotions(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    product_role VARCHAR(10) DEFAULT 'both',
    -- Choices: buy, get, both (for buy_x_get_y)
    discount_override DECIMAL(10,2),
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(promotion_id, product_id)
);

CREATE INDEX idx_promo_products ON promotion_products(promotion_id, product_id);
CREATE INDEX idx_promo_products_priority ON promotion_products(priority DESC);
```

#### `promotion_usages`
```sql
CREATE TABLE promotion_usages (
    id SERIAL PRIMARY KEY,
    promotion_id INTEGER NOT NULL REFERENCES promotions(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    customer_identifier VARCHAR(255),
    discount_applied DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_promo_usages_promo ON promotion_usages(promotion_id);
CREATE INDEX idx_promo_usages_customer ON promotion_usages(customer_identifier);
CREATE INDEX idx_promo_usages_created ON promotion_usages(created_at);
```

---

### 7. Customer Table

#### `customers`
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(254),
    phone VARCHAR(20),
    gender CHAR(1),  -- M, F, O
    date_of_birth DATE,
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(10),
    membership_number VARCHAR(50) UNIQUE,
    membership_tier VARCHAR(50) DEFAULT 'regular',
    points INTEGER DEFAULT 0,
    preferred_outlet_id INTEGER REFERENCES outlets(id) ON DELETE SET NULL,
    notes TEXT,
    marketing_consent BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_visit TIMESTAMP,
    UNIQUE(tenant_id, phone)
);

CREATE INDEX idx_customers_tenant ON customers(tenant_id);
CREATE INDEX idx_customers_phone ON customers(tenant_id, phone);
CREATE INDEX idx_customers_membership ON customers(membership_number);
CREATE INDEX idx_customers_tier ON customers(tenant_id, membership_tier);
CREATE INDEX idx_customers_created ON customers(tenant_id, created_at DESC);
```

---

## Database Indexes Strategy

### Primary Indexes (Auto-created)
- Primary keys (id) on all tables
- Unique constraints (slug, sku, order_number, etc.)

### Performance Indexes
```sql
-- Multi-tenant queries
CREATE INDEX idx_tenant_filtering ON <table>(tenant_id, created_at DESC);

-- Order lookups
CREATE INDEX idx_order_status_outlet ON orders(outlet_id, status, created_at DESC);

-- Product search
CREATE INDEX idx_product_search ON products USING gin(to_tsvector('english', name || ' ' || description));

-- Payment tracking
CREATE INDEX idx_payment_order_status ON payments(order_id, status);

-- Customer lookup
CREATE INDEX idx_customer_lookup ON customers(tenant_id, phone) WHERE is_active = TRUE;
```

---

## Data Types Reference

| PostgreSQL Type | Django Field | Usage Example |
|----------------|--------------|---------------|
| SERIAL | AutoField | Primary keys (id) |
| VARCHAR(n) | CharField | Names, codes |
| TEXT | TextField | Long descriptions |
| DECIMAL(m,n) | DecimalField | Prices, amounts |
| INTEGER | IntegerField | Quantities, counts |
| BOOLEAN | BooleanField | Flags, status |
| TIMESTAMP | DateTimeField | Dates with time |
| DATE | DateField | Birth dates |
| TIME | TimeField | Opening hours |
| JSONB | JSONField | Metadata, arrays |
| INET | GenericIPAddressField | IP addresses |

---

## Database Constraints

### Foreign Key Constraints
```sql
-- Example: Cascade deletion
ALTER TABLE products 
ADD CONSTRAINT fk_products_tenant 
FOREIGN KEY (tenant_id) 
REFERENCES tenants(id) 
ON DELETE CASCADE;

-- Example: Protect deletion
ALTER TABLE order_items 
ADD CONSTRAINT fk_orderitems_product 
FOREIGN KEY (product_id) 
REFERENCES products(id) 
ON DELETE PROTECT;

-- Example: Set null
ALTER TABLE orders 
ADD CONSTRAINT fk_orders_cashier 
FOREIGN KEY (cashier_id) 
REFERENCES users_user(id) 
ON DELETE SET NULL;
```

### Check Constraints
```sql
-- Positive prices
ALTER TABLE products 
ADD CONSTRAINT chk_price_positive 
CHECK (price >= 0);

-- Valid date range
ALTER TABLE promotions 
ADD CONSTRAINT chk_dates_valid 
CHECK (end_date > start_date);

-- Status values
ALTER TABLE orders 
ADD CONSTRAINT chk_status_valid 
CHECK (status IN ('draft', 'pending', 'confirmed', 'preparing', 'ready', 'served', 'completed', 'cancelled'));
```

---

## Query Examples

### 1. Get products for tenant
```sql
SELECT p.*, c.name as category_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.tenant_id = 67 
  AND p.is_available = TRUE
ORDER BY c.sort_order, p.name;
```

### 2. Get orders with items (for outlet)
```sql
SELECT 
    o.*,
    json_agg(
        json_build_object(
            'product_name', oi.product_name,
            'quantity', oi.quantity,
            'total_price', oi.total_price
        )
    ) as items
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE o.outlet_id = 45
  AND o.created_at >= CURRENT_DATE
GROUP BY o.id
ORDER BY o.created_at DESC;
```

### 3. Get active promotions for tenant
```sql
SELECT *
FROM promotions
WHERE tenant_id = 67
  AND is_active = TRUE
  AND start_date <= NOW()
  AND end_date >= NOW()
  AND (max_usage IS NULL OR usage_count < max_usage)
ORDER BY created_at DESC;
```

### 4. Customer order history with totals
```sql
SELECT 
    c.name,
    c.phone,
    COUNT(o.id) as total_orders,
    SUM(o.total_amount) as total_spent,
    MAX(o.created_at) as last_order
FROM customers c
LEFT JOIN orders o ON o.customer_phone = c.phone AND o.tenant_id = c.tenant_id
WHERE c.tenant_id = 67
GROUP BY c.id
ORDER BY total_spent DESC;
```

---

## Backup & Restore

### Backup Database
```bash
# Full backup
pg_dump kiosk_pos > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup specific tenant
pg_dump kiosk_pos -t tenants -t outlets -t products -t orders \
  --where="tenant_id=67" > tenant_67_backup.sql

# Compressed backup
pg_dump kiosk_pos | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database
```bash
# Restore full backup
psql kiosk_pos < backup_20260104_120000.sql

# Restore compressed backup
gunzip -c backup_20260104.sql.gz | psql kiosk_pos
```

---

## Performance Tuning

### Connection Pooling
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'kiosk_pos',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'pool': {
                'min_size': 2,
                'max_size': 10,
            }
        }
    }
}
```

### Query Optimization
```python
# Use select_related for ForeignKey
products = Product.objects.select_related('category', 'tenant')

# Use prefetch_related for ManyToMany
orders = Order.objects.prefetch_related('items__product')

# Use only() to limit fields
products = Product.objects.only('id', 'name', 'price')

# Use values() for dictionaries
product_names = Product.objects.values('id', 'name')
```

---

**Last Updated**: January 4, 2026  
**Database Version**: PostgreSQL 15  
**Schema Version**: 2.0
