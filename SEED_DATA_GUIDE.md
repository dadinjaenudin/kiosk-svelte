# 🌱 Seed Demo Data - Cara Mengisi Sample Data

## 🚀 Quick Command

```bash
# Dari terminal di directory project
cd D:\YOGYA-Kiosk\kiosk-svelte

# Jalankan seed command
docker-compose exec backend python manage.py seed_demo_data
```

---

## 📊 Data yang Akan Dibuat

### **1. Tenant & Outlets**
- ✅ 1 Tenant: "Warung Makan Sedap"
- ✅ 2 Outlets: 
  - Cabang Pusat (Jakarta Pusat)
  - Cabang Selatan (Jakarta Selatan)

### **2. Users**
- ✅ Admin User
  - Username: `admin`
  - Password: `admin123`
  - Role: Admin
  
- ✅ Cashier User
  - Username: `cashier`
  - Password: `cashier123`
  - Role: Cashier

### **3. Categories** (5 kategori)
- 🍛 Makanan Utama
- 🥤 Minuman Dingin
- ☕ Minuman Panas
- 🍪 Snack
- 🍰 Dessert

### **4. Products** (20 produk)

**Makanan Utama:**
- Nasi Goreng Spesial - Rp 35,000
- Mie Goreng Jawa - Rp 32,000
- Ayam Bakar Madu - Rp 45,000
- Soto Ayam - Rp 28,000
- Gado-Gado - Rp 25,000

**Minuman Dingin:**
- Es Teh Manis - Rp 8,000
- Es Jeruk - Rp 10,000
- Es Campur - Rp 15,000
- Jus Alpukat - Rp 18,000
- Es Teler - Rp 20,000

**Minuman Panas:**
- Kopi Hitam - Rp 12,000
- Teh Tarik - Rp 10,000
- Cappuccino - Rp 18,000
- Hot Chocolate - Rp 15,000

**Snack:**
- Pisang Goreng - Rp 12,000
- Tahu Isi - Rp 8,000

**Dessert:**
- Es Krim Vanilla - Rp 15,000
- Puding Coklat - Rp 12,000
- Kue Lapis - Rp 10,000
- Brownies - Rp 18,000

### **5. Product Modifiers**
- Extra Telur (+Rp 5,000)
- Level Pedas:
  - Normal (Rp 0)
  - Sedang (Rp 0)
  - Pedas (Rp 0)
  - Extra Pedas (+Rp 2,000)

### **6. Sample Order**
- 1 Order dengan 2 items
- Status: Draft
- Payment: Pending

---

## 🔍 Verifikasi Data Sudah Masuk

### **Cara 1: Via Admin Panel**
```
1. Buka: http://localhost:8001/admin
2. Login: admin / admin123
3. Cek sections:
   - Users (should show 2 users)
   - Tenants (should show 1 tenant)
   - Outlets (should show 2 outlets)
   - Categories (should show 5 categories)
   - Products (should show 20 products)
   - Orders (should show 1 order)
```

### **Cara 2: Via Database**
```bash
# Akses PostgreSQL
docker-compose exec db psql -U pos_user -d pos_db

# Count data
SELECT 'Tenants' as table_name, COUNT(*) FROM tenants
UNION ALL
SELECT 'Outlets', COUNT(*) FROM outlets
UNION ALL
SELECT 'Users', COUNT(*) FROM users_user
UNION ALL
SELECT 'Categories', COUNT(*) FROM categories
UNION ALL
SELECT 'Products', COUNT(*) FROM products
UNION ALL
SELECT 'Orders', COUNT(*) FROM orders;

# Exit
\q
```

### **Cara 3: Via Kiosk Mode**
```
1. Buka: http://localhost:5174/kiosk
2. Lihat products ditampilkan
3. Coba add to cart
```

---

## ❌ Troubleshooting

### **Error: "Table doesn't exist"**
```bash
# Run migrations dulu
docker-compose exec backend python manage.py migrate

# Lalu seed lagi
docker-compose exec backend python manage.py seed_demo_data
```

### **Error: "Duplicate key"**
```bash
# Data sudah ada, hapus dulu
docker-compose exec backend python manage.py flush --noinput

# Lalu seed lagi
docker-compose exec backend python manage.py seed_demo_data
```

### **Data masih kosong setelah seed**
```bash
# Cek logs untuk error
docker-compose logs backend | grep -i error

# Atau run seed dengan verbose output
docker-compose exec backend python manage.py seed_demo_data --verbosity 2
```

---

## 🔄 Reset Data (Mulai dari Awal)

```bash
# Stop containers
docker-compose down -v

# Start fresh
docker-compose up -d

# Wait for migrations
sleep 30

# Seed data
docker-compose exec backend python manage.py seed_demo_data

# Check admin panel
open http://localhost:8001/admin
```

---

## 📝 Custom Seed Data

Jika ingin edit data yang di-seed, edit file:
```
backend/apps/products/management/commands/seed_demo_data.py
```

Lalu run ulang:
```bash
docker-compose exec backend python manage.py seed_demo_data
```

---

## ✅ Success Indicators

Setelah seed berhasil, Anda akan lihat:
```
🌱 Starting data seeding...
Creating tenant...
✓ Tenant: Warung Makan Sedap
Creating outlets...
✓ Outlet: Cabang Pusat
✓ Outlet: Cabang Selatan
Creating users...
✓ User: admin (Admin)
✓ User: cashier (Cashier)
Creating categories...
✓ Category: Makanan Utama
✓ Category: Minuman Dingin
✓ Category: Minuman Panas
✓ Category: Snack
✓ Category: Dessert
Creating products...
✓ 20 products created
Creating modifiers...
✓ Product modifiers created
Creating sample order...
✓ Sample order created
✅ Demo data seeded successfully!
🖥️  Kiosk Mode: http://localhost:5174/kiosk
👤 Admin Panel: http://localhost:8001/admin (admin/admin123)
```

---

## 🎯 Next Steps

1. ✅ Seed data
2. ✅ Login ke admin panel
3. ✅ Test Kiosk Mode
4. ✅ Add products to cart
5. ✅ Test checkout flow
6. ✅ Test payment integration

**Selamat mencoba!** 🚀
