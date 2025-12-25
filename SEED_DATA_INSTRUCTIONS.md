# Quick Fix: Database Kosong (0 Products)

## Status: ✅ API WORKING - Hanya Perlu Seed Data

---

## 🎯 Masalah Saat Ini

Console output:
```
✅ Categories API response: {count: 0, results: Array(0)}
✅ Categories loaded: 0
✅ Products API response: {count: 0, results: Array(0)}
✅ Products loaded: 0
```

**Good News**: 
- ✅ API sudah bekerja dengan benar
- ✅ Pagination handling sudah fix
- ✅ CORS sudah fix
- ✅ Authentication sudah fix
- ✅ Frontend bisa connect ke backend

**Problem**: 
- ❌ Database kosong (belum ada data)

---

## 🚀 SOLUSI - Seed Demo Data

### Langkah 1: Check Status Docker

```bash
docker-compose ps
```

**Expected**: Semua service status `Up`

### Langkah 2: Seed Demo Data

```bash
docker-compose exec backend python manage.py seed_demo_data
```

**Expected Output**:
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
✓ Category: Main Course (10 products)
✓ Category: Beverages (5 products)
✓ Category: Desserts (3 products)
✓ Category: Snacks (2 products)
✓ Category: Special Menu (0 products)
Creating products...
✓ Created 20 products
Creating product modifiers...
✓ Created 15 modifiers
Creating sample order...
✓ Sample Order #ORD-001

✅ Seeding completed successfully!

Summary:
  Tenants: 1
  Outlets: 2
  Users: 2
  Categories: 5
  Products: 20
  Modifiers: 15
  Orders: 1
```

### Langkah 3: Verify Data Ada

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

### Langkah 4: Test Kiosk Mode

1. **Refresh browser** (atau hard reload: **Ctrl+Shift+R**)
2. Open: http://localhost:5174/kiosk
3. Check Console (F12):

**Expected**:
```
Syncing with server...
Categories API response: {count: 5, results: Array(5)}
Categories loaded: 5
Products API response: {count: 20, results: Array(20)}
Products loaded: 20
```

4. **Visual Check**: Harusnya **20 produk tampil** di Kiosk!

---

## 📦 Data yang Di-seed

### 1. Tenant & Outlets
- **1 Tenant**: Warung Makan Sedap
- **2 Outlets**: Cabang Pusat, Cabang Mall

### 2. Users
- **Admin**: admin / admin123
- **Cashier**: cashier / cashier123

### 3. Categories (5)
1. **Main Course** - Hidangan Utama
2. **Beverages** - Minuman
3. **Desserts** - Makanan Penutup
4. **Snacks** - Cemilan
5. **Special Menu** - Menu Spesial

### 4. Products (20)

#### Main Course (10)
1. Nasi Goreng Spesial - Rp 25,000
2. Mie Goreng - Rp 20,000
3. Ayam Bakar - Rp 35,000
4. Sate Ayam - Rp 30,000
5. Gado-Gado - Rp 22,000
6. Nasi Uduk - Rp 18,000
7. Soto Ayam - Rp 23,000
8. Rendang - Rp 40,000
9. Pecel Lele - Rp 25,000
10. Nasi Rawon - Rp 28,000

#### Beverages (5)
1. Es Teh Manis - Rp 5,000
2. Es Jeruk - Rp 8,000
3. Jus Alpukat - Rp 15,000
4. Es Kelapa Muda - Rp 12,000
5. Kopi Hitam - Rp 10,000

#### Desserts (3)
1. Es Campur - Rp 18,000
2. Pisang Goreng - Rp 10,000
3. Klepon - Rp 8,000

#### Snacks (2)
1. Keripik Singkong - Rp 8,000
2. Lumpia Basah - Rp 12,000

### 5. Product Modifiers (15)
- **Level Pedas**: Tidak Pedas, Sedang, Pedas, Extra Pedas
- **Ukuran**: Small, Medium, Large
- **Topping**: Extra Telur (+Rp 5,000), Extra Ayam (+Rp 10,000), Extra Keju (+Rp 8,000)
- **Es/Panas**: Dingin, Panas
- **Gula**: Tanpa Gula, Normal, Extra Manis

### 6. Sample Order (1)
- Order #ORD-001
- 3 items total
- Status: Completed

---

## 🧪 Verification Commands

### Check All Services Running
```bash
docker-compose ps
```

### Check Database Tables
```bash
docker-compose exec db psql -U pos_user -d pos_db -c "\dt"
```

Expected: 25+ tables including:
- users_user
- tenants_tenant
- tenants_outlet
- products_category
- products_product
- products_productmodifier
- orders_order
- payments_payment

### Check Product Count Directly
```bash
docker-compose exec db psql -U pos_user -d pos_db -c "SELECT COUNT(*) FROM products_product;"
```

Expected: `count = 20`

### Check Categories Count
```bash
docker-compose exec db psql -U pos_user -d pos_db -c "SELECT COUNT(*) FROM products_category;"
```

Expected: `count = 5`

### Test API with curl
```bash
# Test Categories
curl -s http://localhost:8001/api/products/categories/ | python -m json.tool | head -30

# Test Products
curl -s http://localhost:8001/api/products/products/ | python -m json.tool | head -50
```

---

## 🔧 Troubleshooting

### Problem: "Command not found: seed_demo_data"

**Solution**: Check command file exists
```bash
docker-compose exec backend ls -la apps/products/management/commands/
```

Should see: `seed_demo_data.py`

If not exist, rebuild:
```bash
docker-compose down
docker-compose up --build -d
```

### Problem: "apps.products.models.DoesNotExist"

**Cause**: Models tidak ada di database

**Solution**: Run migrations
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed_demo_data
```

### Problem: Seed command berjalan tapi 0 products

**Check logs**:
```bash
docker-compose exec backend python manage.py seed_demo_data --verbosity 2
```

### Problem: Database connection error

**Restart services**:
```bash
docker-compose restart db backend
sleep 30
docker-compose exec backend python manage.py seed_demo_data
```

---

## 📊 Complete Deployment Flow

```bash
# 1. Update code
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main

# 2. Rebuild (optional, jika ada perubahan besar)
docker-compose down
docker-compose up --build -d

# 3. Wait for services to be ready
sleep 30

# 4. Check services
docker-compose ps

# 5. Run migrations (jika belum)
docker-compose exec backend python manage.py migrate

# 6. Seed data
docker-compose exec backend python manage.py seed_demo_data

# 7. Verify data
docker-compose exec backend python check_data.py

# 8. Test Kiosk
# Open: http://localhost:5174/kiosk
```

---

## ✅ Success Checklist

After seeding, you should have:

- [x] `docker-compose ps` - All services Up
- [x] 1 Tenant (Warung Makan Sedap)
- [x] 2 Outlets (Cabang Pusat, Cabang Mall)
- [x] 2 Users (admin, cashier)
- [x] 5 Categories
- [x] 20 Products
- [x] 15 Modifiers
- [x] Console: `Categories loaded: 5`
- [x] Console: `Products loaded: 20`
- [x] Kiosk displays products visually
- [x] Can add products to cart
- [x] Can filter by category

---

## 🎉 Expected Final Result

### Console Output
```
✅ Syncing with server...
✅ Categories API response: {count: 5, results: Array(5)}
✅ Categories loaded: 5
✅ Products API response: {count: 20, results: Array(20)}
✅ Products loaded: 20
```

### Visual Result
- **Category tabs** at top: Main Course, Beverages, Desserts, Snacks, Special Menu
- **Product grid** showing 20 products with:
  - Product name
  - Price (Rp format)
  - Image placeholder
  - "Add to Cart" button
- **Cart** on right side (empty initially)

---

## 🔗 Access URLs

After seeding:

- 🛒 **Kiosk Mode**: http://localhost:5174/kiosk (20 products displayed)
- 👤 **Admin Panel**: http://localhost:8001/admin (admin/admin123)
  - View all products, categories, users, orders
- 📖 **API Docs**: http://localhost:8001/api/docs
  - Interactive API documentation
- 📦 **Categories API**: http://localhost:8001/api/products/categories/
- 📦 **Products API**: http://localhost:8001/api/products/products/

---

## 🚀 ONE-LINE FIX

Untuk yang terburu-buru, jalankan satu command ini:

```bash
docker-compose exec backend python manage.py seed_demo_data && echo "✅ Seeding done! Refresh Kiosk page: http://localhost:5174/kiosk"
```

Lalu **refresh browser** (Ctrl+Shift+R)

---

**GitHub**: https://github.com/dadinjaenudin/kiosk-svelte  
**Status**: 🟢 READY TO SEED

---

## 📝 Summary

**Masalah**: Database kosong (0 products)  
**Solusi**: Jalankan `seed_demo_data` command  
**Hasil**: 20 products, 5 categories tampil di Kiosk  
**Time**: < 1 menit  

Silakan jalankan command seed dan test lagi! 🚀
