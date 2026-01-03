# 📊 Database Schema & ERD

## Table of Contents
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Core Tables](#core-tables)
- [Product & Catalog](#product--catalog)
- [Orders & Transactions](#orders--transactions)
- [Users & Authentication](#users--authentication)
- [Promotions](#promotions)
- [Indexes & Performance](#indexes--performance)
- [Migrations](#migrations)

---

## Entity Relationship Diagram

```
┌─────────────┐
│   Tenant    │
│  (Brand)    │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────┐         ┌─────────────┐
│   Outlet    │         │    User     │
│  (Store)    │◀────────│ (Staff)     │
└──────┬──────┘   N:1   └──────┬──────┘
       │                        │
       │ 1:N                    │ 1:N
       │                        │
┌──────▼──────┐         ┌──────▼──────┐
│  Category   │         │    Order    │
└──────┬──────┘         └──────┬──────┘
       │                        │
       │ 1:N                    │ 1:N
       │                        │
┌──────▼──────┐         ┌──────▼──────┐
│   Product   │────────▶│  OrderItem  │
│  (Menu)     │   N:1   └─────────────┘
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────┐
│  Modifier   │
└─────────────┘

┌─────────────┐         ┌─────────────┐
│  Promotion  │◀───────▶│   Product   │
└─────────────┘   N:N   └─────────────┘

┌─────────────┐         ┌─────────────┐
│  Customer   │────────▶│    Order    │
└─────────────┘   1:N   └──────┬──────┘
                               │
                               │ 1:1
                               │
                        ┌──────▼──────┐
                        │   Payment   │
                        └─────────────┘
```

---

## Core Tables

### tenants

Represents restaurant brands/franchises.

```sql
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    logo VARCHAR(255),
    
    -- Branding
    primary_color VARCHAR(7) DEFAULT '#FF6B35',
    secondary_color VARCHAR(7) DEFAULT '#F7931E',
    
    -- Business
    phone VARCHAR(20),
    email VARCHAR(254),
    website VARCHAR(200),
    
    -- Settings
    tax_rate DECIMAL(5,2) DEFAULT 10.00,
    service_charge_rate DECIMAL(5,2) DEFAULT 5.00,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_slug (slug),
    INDEX idx_active (is_active)
);
```

**Sample Data**:
```sql
INSERT INTO tenants (name, slug, primary_color, tax_rate) VALUES
('Ayam Geprek Bensu', 'ayam-geprek-bensu', '#FF6B35', 10.00),
('Kopi Kenangan', 'kopi-kenangan', '#8B4513', 10.00),
('Bakso Boedjangan', 'bakso-boedjangan', '#DC143C', 10.00);
```

### outlets

Physical store locations.

```sql
CREATE TABLE outlets (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20) NOT NULL,
    
    -- Location
    address TEXT NOT NULL,
    city VARCHAR(100),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    
    -- Contact
    phone VARCHAR(20),
    manager VARCHAR(200),
    
    -- Operations
    operating_hours JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (tenant_id, code),
    INDEX idx_tenant (tenant_id),
    INDEX idx_active (is_active)
);
```

**Sample Data**:
```sql
INSERT INTO outlets (tenant_id, name, code, address, city, phone) VALUES
(1, 'Ayam Geprek Bensu - Tunjungan Plaza', 'TP-001', 'Mall Tunjungan Plaza Lt.4', 'Surabaya', '031-1234567'),
(1, 'Ayam Geprek Bensu - Galaxy Mall', 'GM-001', 'Galaxy Mall Lt.3', 'Surabaya', '031-7654321'),
(2, 'Kopi Kenangan - Tunjungan Plaza', 'TP-002', 'Mall Tunjungan Plaza Lt.GF', 'Surabaya', '031-2345678');
```

---

## Product & Catalog

### categories

Product categories for organizing menu.

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    description TEXT,
    image VARCHAR(255),
    sort_order INT DEFAULT 0,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_tenant_sort (tenant_id, sort_order),
    INDEX idx_active (is_active)
);
```

**Sample Data**:
```sql
INSERT INTO categories (tenant_id, name, sort_order) VALUES
(1, 'Ayam Geprek', 1),
(1, 'Minuman', 2),
(1, 'Paket Hemat', 3),
(2, 'Kopi', 1),
(2, 'Non-Kopi', 2);
```

### products

Menu items/products.

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    outlet_id INT REFERENCES outlets(id) ON DELETE CASCADE,  -- NULL = available at all outlets
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    image VARCHAR(255),
    
    -- Pricing
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) DEFAULT 0,
    
    -- Stock
    track_stock BOOLEAN DEFAULT FALSE,
    stock_quantity INT DEFAULT 0,
    low_stock_alert INT DEFAULT 10,
    
    -- Flags
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    is_popular BOOLEAN DEFAULT FALSE,
    has_promo BOOLEAN DEFAULT FALSE,
    promo_price DECIMAL(10,2),
    
    -- Meta
    preparation_time INT DEFAULT 10,  -- minutes
    calories INT,
    tags VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_tenant_category (tenant_id, category_id),
    INDEX idx_outlet (outlet_id),
    INDEX idx_sku (sku),
    INDEX idx_active (is_active, is_available),
    INDEX idx_featured (is_featured),
    INDEX idx_popular (is_popular),
    INDEX idx_promo (has_promo)
);
```

**Sample Data**:
```sql
INSERT INTO products (tenant_id, category_id, sku, name, price, is_popular) VALUES
(1, 1, 'AGR-001', 'Ayam Geprek Original', 25000, TRUE),
(1, 1, 'AGR-002', 'Ayam Geprek Keju', 30000, TRUE),
(1, 2, 'MIN-001', 'Es Teh Manis', 5000, FALSE),
(2, 4, 'KOP-001', 'Kopi Kenangan Mantan', 20000, TRUE);
```

### product_modifiers

Customization options (size, toppings, etc).

```sql
CREATE TABLE product_modifiers (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,  -- NULL = global modifier
    
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) DEFAULT 'extra',  -- size, topping, spicy, extra, sauce
    price_adjustment DECIMAL(10,2) DEFAULT 0,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_product (product_id),
    INDEX idx_type (type)
);
```

**Sample Data**:
```sql
INSERT INTO product_modifiers (product_id, name, type, price_adjustment) VALUES
(1, 'Level 1 (Ga Pedes)', 'spicy', 0),
(1, 'Level 5 (Pedes Banget)', 'spicy', 0),
(1, 'Extra Sambal', 'extra', 2000),
(1, 'Extra Keju', 'extra', 5000),
(4, 'Ukuran Reguler', 'size', 0),
(4, 'Ukuran Large', 'size', 5000);
```

---

## Orders & Transactions

### orders

Main order/transaction record.

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    outlet_id INT NOT NULL REFERENCES outlets(id) ON DELETE CASCADE,
    
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- draft, pending, confirmed, preparing, ready, served, completed, cancelled
    
    -- Customer (optional for walk-in)
    customer_name VARCHAR(200),
    customer_phone VARCHAR(20),
    customer_email VARCHAR(254),
    
    -- Order details
    table_number VARCHAR(20),
    notes TEXT,
    
    -- Pricing
    subtotal DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    service_charge_amount DECIMAL(12,2) DEFAULT 0,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    
    -- Payment
    payment_status VARCHAR(20) DEFAULT 'unpaid',  -- unpaid, partial, paid, refunded
    paid_amount DECIMAL(12,2) DEFAULT 0,
    
    -- Staff
    cashier_id INT REFERENCES users_user(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    INDEX idx_tenant_outlet (tenant_id, outlet_id),
    INDEX idx_order_number (order_number),
    INDEX idx_status (status),
    INDEX idx_payment_status (payment_status),
    INDEX idx_created (created_at DESC),
    INDEX idx_outlet_created (outlet_id, created_at DESC)
);
```

### order_items

Individual items in an order.

```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE PROTECT,
    
    -- Snapshot (preserve even if product changes)
    product_name VARCHAR(200) NOT NULL,
    product_sku VARCHAR(50) NOT NULL,
    
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    
    -- Modifiers (JSON)
    modifiers JSONB DEFAULT '[]',
    notes TEXT,
    
    -- Kitchen status
    kitchen_status VARCHAR(20) DEFAULT 'pending',  -- pending, cooking, ready
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_order (order_id),
    INDEX idx_product (product_id),
    INDEX idx_kitchen_status (kitchen_status)
);
```

**Sample Data**:
```sql
-- Order
INSERT INTO orders (tenant_id, outlet_id, order_number, customer_name, subtotal, tax_amount, total_amount) 
VALUES (1, 1, 'ORD-20260103-A1B2', 'John Doe', 30000, 3000, 33000);

-- Order Items
INSERT INTO order_items (order_id, product_id, product_name, product_sku, quantity, unit_price, total_price, modifiers)
VALUES 
(1, 1, 'Ayam Geprek Original', 'AGR-001', 1, 25000, 25000, '[{"name":"Level 5","price":0}]'),
(1, 3, 'Es Teh Manis', 'MIN-001', 1, 5000, 5000, '[]');
```

### payments

Payment records (supports multiple payments per order).

```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    
    method VARCHAR(20) NOT NULL,  -- cash, qris, card, ewallet
    amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, success, failed, cancelled
    
    -- Gateway info
    transaction_id VARCHAR(100),
    gateway VARCHAR(50),  -- midtrans, xendit, manual
    gateway_response JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    INDEX idx_order (order_id),
    INDEX idx_method (method),
    INDEX idx_status (status),
    INDEX idx_transaction_id (transaction_id)
);
```

---

## Users & Authentication

### users_user

Custom user model with roles.

```sql
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    
    -- Django auth fields
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254),
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    
    -- Custom fields
    role VARCHAR(20) DEFAULT 'cashier',  -- super_admin, admin, tenant_owner, manager, cashier, kitchen
    phone_number VARCHAR(20),
    tenant_id INT REFERENCES tenants(id) ON DELETE CASCADE,
    outlet_id INT REFERENCES outlets(id) ON DELETE SET NULL,
    
    -- Permissions
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_tenant (tenant_id),
    INDEX idx_outlet (outlet_id),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
);
```

### users_user_accessible_outlets

Many-to-many relationship for multi-outlet access.

```sql
CREATE TABLE users_user_accessible_outlets (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    outlet_id INT NOT NULL REFERENCES outlets(id) ON DELETE CASCADE,
    
    UNIQUE (user_id, outlet_id),
    INDEX idx_user (user_id),
    INDEX idx_outlet (outlet_id)
);
```

**Sample Data**:
```sql
-- Super Admin
INSERT INTO users_user (username, password, role, is_staff, is_superuser) 
VALUES ('admin', 'hashed_password', 'super_admin', TRUE, TRUE);

-- Tenant Owner
INSERT INTO users_user (username, password, role, tenant_id) 
VALUES ('bensu_owner', 'hashed_password', 'tenant_owner', 1);

-- Cashier
INSERT INTO users_user (username, password, role, tenant_id, outlet_id) 
VALUES ('cashier_tp01', 'hashed_password', 'cashier', 1, 1);

-- Kitchen Staff
INSERT INTO users_user (username, password, role, tenant_id, outlet_id) 
VALUES ('kitchen_tp01', 'hashed_password', 'kitchen', 1, 1);
```

---

## Promotions

### promotions

Promotion campaigns.

```sql
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(20) NOT NULL,  -- percentage, fixed, buy_x_get_y, bundle
    code VARCHAR(50) UNIQUE,
    
    -- Discount rules
    discount_value DECIMAL(10,2) NOT NULL,
    min_purchase DECIMAL(10,2) DEFAULT 0,
    max_discount DECIMAL(10,2),
    max_usage INT,
    usage_count INT DEFAULT 0,
    
    -- Validity
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_tenant (tenant_id),
    INDEX idx_code (code),
    INDEX idx_active_dates (is_active, start_date, end_date)
);
```

### promotions_products

Many-to-many: which products are in promotion.

```sql
CREATE TABLE promotions_products (
    id SERIAL PRIMARY KEY,
    promotion_id INT NOT NULL REFERENCES promotions(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    UNIQUE (promotion_id, product_id),
    INDEX idx_promotion (promotion_id),
    INDEX idx_product (product_id)
);
```

### customers

Customer records for loyalty program.

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(200) NOT NULL,
    email VARCHAR(254),
    phone VARCHAR(20) UNIQUE NOT NULL,
    
    -- Loyalty
    loyalty_points INT DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    visit_count INT DEFAULT 0,
    last_visit TIMESTAMP,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_tenant (tenant_id),
    INDEX idx_phone (phone),
    INDEX idx_email (email)
);
```

---

## Indexes & Performance

### Essential Indexes

```sql
-- Tenant-based queries (most common)
CREATE INDEX idx_products_tenant_active ON products(tenant_id, is_active, is_available);
CREATE INDEX idx_orders_tenant_date ON orders(tenant_id, created_at DESC);
CREATE INDEX idx_orders_outlet_status ON orders(outlet_id, status, created_at DESC);

-- Search queries
CREATE INDEX idx_products_name ON products USING gin(to_tsvector('english', name));
CREATE INDEX idx_products_tags ON products USING gin(string_to_array(tags, ','));

-- Lookup queries
CREATE INDEX idx_order_number_unique ON orders(order_number);
CREATE INDEX idx_product_sku_unique ON products(sku);

-- Foreign key indexes (for joins)
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_payments_order ON payments(order_id);
```

### Query Optimization Examples

```sql
-- Fast: Uses idx_products_tenant_active
SELECT * FROM products 
WHERE tenant_id = 1 
  AND is_active = TRUE 
  AND is_available = TRUE;

-- Fast: Uses idx_orders_outlet_status
SELECT * FROM orders 
WHERE outlet_id = 1 
  AND status = 'pending' 
ORDER BY created_at DESC 
LIMIT 50;

-- Fast: Uses idx_order_number_unique
SELECT * FROM orders 
WHERE order_number = 'ORD-20260103-A1B2';
```

---

## Migrations

### Initial Migration

```python
# backend/apps/tenants/migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                # ... other fields
            ],
            options={
                'db_table': 'tenants',
            },
        ),
        migrations.CreateModel(
            name='Outlet',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('tenant', models.ForeignKey(to='tenants.Tenant')),
                # ... other fields
            ],
            options={
                'db_table': 'outlets',
            },
        ),
    ]
```

### Running Migrations

```bash
# Create migrations
python manage.py makemigrations

# Show SQL
python manage.py sqlmigrate tenants 0001

# Apply migrations
python manage.py migrate

# Check status
python manage.py showmigrations
```

### Data Migration Example

```python
# Add default tenant
from django.db import migrations

def create_default_tenant(apps, schema_editor):
    Tenant = apps.get_model('tenants', 'Tenant')
    Tenant.objects.create(
        name='Default Restaurant',
        slug='default',
        tax_rate=10.00,
        service_charge_rate=5.00
    )

class Migration(migrations.Migration):
    dependencies = [
        ('tenants', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(create_default_tenant),
    ]
```

---

## Database Statistics

### Table Size Query

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;
```

### Row Counts

```sql
SELECT 
    'tenants' AS table_name, COUNT(*) AS row_count FROM tenants
UNION ALL
SELECT 'outlets', COUNT(*) FROM outlets
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items;
```

---

## Backup & Restore

### Backup

```bash
# Full database backup
pg_dump -U pos_user -h localhost -d pos_db > backup_$(date +%Y%m%d).sql

# Specific tables
pg_dump -U pos_user -t tenants -t outlets pos_db > tenants_backup.sql

# Compressed backup
pg_dump -U pos_user pos_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore

```bash
# Restore full database
psql -U pos_user -d pos_db < backup_20260103.sql

# Restore from compressed
gunzip -c backup_20260103.sql.gz | psql -U pos_user -d pos_db
```

---

## Next Steps

- **[BACKEND_API_REFERENCE.md](BACKEND_API_REFERENCE.md)** - API endpoints documentation
- **[DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)** - Setup development environment
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment

---

**Last Updated**: January 3, 2026
