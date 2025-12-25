# 🔧 DATABASE MIGRATION REQUIRED

## ❌ Error
```
django.db.utils.ProgrammingError: relation "tenants" does not exist
LINE 1: ... FROM "tenants" ...
```

## 🔍 Root Cause

**Database tables not created yet**

After Phase 2 implementation, new models were added:
- `apps.core` (TenantModel, managers)
- Updated `apps.products` (inherit from TenantModel)
- Enhanced `apps.tenants` (serializers, views)

But migrations haven't been run in the Docker container, so the database schema is outdated.

---

## ✅ Solution: Run Migrations

### Option 1: Quick Deploy Script (RECOMMENDED)

**Use the automated script:**
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Stop containers
2. Start database
3. Run migrations
4. Seed data (if needed)
5. Start all services
6. Test endpoints

---

### Option 2: Manual Step-by-Step

#### Step 1: Pull Latest Code
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
```

#### Step 2: Stop All Containers
```bash
docker-compose down
```

#### Step 3: Start Database Only
```bash
docker-compose up -d db
sleep 10  # Wait for PostgreSQL
```

#### Step 4: Run Migrations
```bash
# Run migrations
docker-compose run --rm backend python manage.py migrate

# Expected output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, 
#                         tenants, products, orders, payments, users
# Running migrations:
#   Applying tenants.0001_initial... OK
#   Applying products.0001_initial... OK
#   ...
```

#### Step 5: Verify Migrations
```bash
docker-compose run --rm backend python manage.py showmigrations

# Should show [X] for applied migrations:
# tenants
#  [X] 0001_initial
# products
#  [X] 0001_initial
# ...
```

#### Step 6: Seed Data
```bash
docker-compose run --rm backend python manage.py seed_demo_data

# Expected:
# 🌱 Starting data seeding...
# ✓ Tenant: Warung Makan Sedap
# ✓ Outlet: Cabang Pusat
# ...
# ✅ Data seeding completed successfully!
```

#### Step 7: Verify Data
```bash
docker-compose run --rm backend python check_data.py

# Expected:
# 📊 Database Check:
#   Tenants: 1
#   Outlets: 2
#   Users: 2
#   Categories: 5
#   Products: 20
```

#### Step 8: Start All Services
```bash
docker-compose up -d

# Wait for services to start
sleep 15
```

#### Step 9: Check Service Status
```bash
docker-compose ps

# All should be "Up":
# kiosk_pos_backend    Up
# kiosk_pos_frontend   Up
# kiosk_pos_db         Up
```

#### Step 10: Test API
```bash
# Health check
curl http://localhost:8001/api/health/
# {"status":"ok","service":"POS Backend"}

# Categories
curl http://localhost:8001/api/products/categories/
# {"count":5,"results":[...]}

# Products
curl http://localhost:8001/api/products/products/
# {"count":20,"results":[...]}
```

#### Step 11: Open Frontend
```
http://localhost:5174/kiosk
```

Check console (F12):
```
Categories loaded: 5
Products loaded: 20
```

---

## 🔄 Migration Commands Reference

### Common Migration Commands
```bash
# Create new migrations
docker-compose run --rm backend python manage.py makemigrations

# Apply migrations
docker-compose run --rm backend python manage.py migrate

# Show migration status
docker-compose run --rm backend python manage.py showmigrations

# Rollback migration
docker-compose run --rm backend python manage.py migrate app_name migration_name

# Fake initial migration (if tables already exist)
docker-compose run --rm backend python manage.py migrate --fake-initial

# Show SQL for migration
docker-compose run --rm backend python manage.py sqlmigrate app_name migration_number
```

### Database Commands
```bash
# Access PostgreSQL shell
docker-compose exec db psql -U pos_user -d pos_db

# List tables
\dt

# Describe table
\d tenants

# Check data
SELECT COUNT(*) FROM products;

# Exit
\q
```

---

## 🐛 Troubleshooting

### Issue 1: "relation does not exist"
**Solution**: Run migrations
```bash
docker-compose run --rm backend python manage.py migrate
```

### Issue 2: "Migration is already applied"
**Solution**: Check migration status
```bash
docker-compose run --rm backend python manage.py showmigrations
```

If needed, fake the migration:
```bash
docker-compose run --rm backend python manage.py migrate --fake app_name
```

### Issue 3: "Database connection refused"
**Solution**: Ensure database is running
```bash
docker-compose up -d db
sleep 10
docker-compose ps
```

### Issue 4: "Conflicting migrations"
**Solution**: Resolve conflicts manually or rebuild
```bash
# Nuclear option - start fresh
docker-compose down -v
docker-compose up -d db
sleep 10
docker-compose run --rm backend python manage.py migrate
docker-compose run --rm backend python manage.py seed_demo_data
docker-compose up -d
```

### Issue 5: No data after migration
**Solution**: Seed data
```bash
docker-compose exec backend python manage.py seed_demo_data
```

---

## 📊 Database Schema

After migrations, these tables will be created:

### Core Tables
- `tenants` - Tenant/brand information
- `outlets` - Store locations
- `users_user` - User accounts

### Product Tables
- `categories` - Product categories
- `products` - Menu items
- `product_modifiers` - Product options (size, toppings, etc)
- `outlet_products` - Outlet-specific product availability

### Order Tables
- `orders` - Customer orders
- `order_items` - Items in orders

### Payment Tables
- `payments` - Payment transactions

---

## 🎯 Expected Results

After successful migration and seeding:

### Database
```
Tenants: 1
  - Warung Makan Sedap

Outlets: 2
  - Cabang Pusat
  - Cabang Mall

Users: 2
  - admin (admin123)
  - cashier (cashier123)

Categories: 5
  - Main Course (10 products)
  - Beverages (5 products)
  - Desserts (3 products)
  - Snacks (2 products)
  - Special Menu (0 products)

Products: 20
  - Nasi Goreng Spesial (Rp 25,000)
  - Mie Goreng (Rp 20,000)
  - ... (18 more)
```

### API Endpoints
```
✅ /api/health/ - 200 OK
✅ /api/products/categories/ - 5 categories
✅ /api/products/products/ - 20 products
✅ /api/tenants/me/ - Tenant info (authenticated)
✅ /api/outlets/ - 2 outlets (authenticated)
```

### Frontend
```
✅ Categories: 5 tabs displayed
✅ Products: 20 items displayed
✅ Category filter working
✅ Add to cart working
✅ No console errors
```

---

## 🚀 Quick Commands

### Full Reset & Deploy
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
docker-compose down -v  # Remove volumes
docker-compose up -d db
sleep 10
docker-compose run --rm backend python manage.py migrate
docker-compose run --rm backend python manage.py seed_demo_data
docker-compose up -d
```

### Quick Restart
```bash
docker-compose restart backend frontend
```

### Check Logs
```bash
docker-compose logs backend | tail -50
docker-compose logs frontend | tail -50
```

### Test Everything
```bash
# Health
curl http://localhost:8001/api/health/

# Data check
docker-compose exec backend python check_data.py

# API test
curl http://localhost:8001/api/products/categories/ | python -m json.tool
```

---

## 📚 Related Files

```
backend/
├── apps/
│   ├── tenants/
│   │   └── migrations/
│   │       └── 0001_initial.py
│   ├── products/
│   │   └── migrations/
│   │       └── 0001_initial.py
│   └── users/
│       └── migrations/
│           └── 0001_initial.py
├── manage.py
└── config/
    └── settings.py

Root:
├── deploy.sh              # Automated deployment script
├── DEPLOYMENT_GUIDE.sh    # Step-by-step guide
└── docker-compose.yml     # Service configuration
```

---

## ✅ Summary

**MIGRATION REQUIRED! ✅**

Error:
- ❌ `relation "tenants" does not exist`

Solution:
1. `git pull origin main`
2. `docker-compose down`
3. `docker-compose up -d db && sleep 10`
4. `docker-compose run --rm backend python manage.py migrate`
5. `docker-compose run --rm backend python manage.py seed_demo_data`
6. `docker-compose up -d`

Quick deploy:
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
chmod +x deploy.sh
./deploy.sh
```

**GitHub**: https://github.com/dadinjaenudin/kiosk-svelte
**Status**: ✅ **READY TO MIGRATE!**

After migration, system akan fully functional dengan database schema yang up-to-date! 🚀
