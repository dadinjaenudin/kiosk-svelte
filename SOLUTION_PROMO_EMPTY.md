# ✅ SOLUSI: Filter Promo Kosong (0 Products)

## 🔍 Root Cause

Database kosong! Command `check_promo_data` menunjukkan:
```
Total Products: 0
⭐ Popular: 0
🔥 Promo: 0
```

Anda perlu **seed data dulu** sebelum filter promo bisa bekerja.

---

## 🚀 SOLUSI LENGKAP (5 Menit)

### Step 1: Pull Update Terbaru

```powershell
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
```

### Step 2: Restart Backend (Agar Code Baru Loaded)

```powershell
docker-compose restart backend
```

Tunggu 10 detik.

### Step 3: Jalankan Migration (Jika Belum)

```powershell
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### Step 4: Seed Food Court Data

```powershell
docker-compose exec backend python manage.py seed_foodcourt
```

**Expected Output:**
```
🏪 Creating Food Court with 5 Tenants...
============================================================
Creating Tenant: Warung Nasi Padang
============================================================
✓ Tenant created: Warung Nasi Padang
✓ Outlet: Warung Nasi Padang - Food Court
✓ User: warung-nasi-padang (password: password123)
Creating categories...
  ✓ Nasi Padang
  ✓ Sayur
  ✓ Minuman
Creating products...
  ✓ Rendang Sapi - Rp 45,000 ⭐
  ✓ Ayam Pop - Rp 38,000 (Promo: Rp 32,000)
  ✓ Gulai Ikan - Rp 42,000 (Promo: Rp 36,000) ⭐
  ...

[Repeat untuk 4 tenant lainnya]

============================================================
✅ Food Court Data Seeding Complete!
============================================================

📊 Summary:
   Tenants: 5
   Products: 38
   Categories: 15
   ⭐ Popular: 11
   🔥 Promo: 7
   🌟 Popular + Promo: 5

🏪 Tenants Created:
   • Warung Nasi Padang (7 products, 2 popular, 2 promo) - Color: #FF6B35
   • Mie Ayam & Bakso (6 products, 3 popular, 2 promo) - Color: #F7931E
   • Ayam Geprek Mantap (6 products, 3 popular, 1 promo) - Color: #DC143C
   • Soto Betawi H. Mamat (6 products, 2 popular, 1 promo) - Color: #FFC300
   • Nasi Goreng Abang (7 products, 3 popular, 2 promo) - Color: #28A745
```

### Step 5: Verifikasi dengan Check Command

```powershell
docker-compose exec backend python manage.py check_promo_data
```

**Expected Output:**
```
🔍 Checking database status...

📊 Database Summary:
   Total Products: 38
   ⭐ Popular: 11
   🔥 Promo: 7
   ✓ Available: 38
   🌟 Popular + Promo: 5

🔥 Promo Products (7):
   ⭐ NP-002: Ayam Pop (Rp 38,000 → Rp 32,000)
   ⭐ NP-003: Gulai Ikan (Rp 42,000 → Rp 36,000)
   ⭐ MB-002: Mie Ayam Jumbo (Rp 32,000 → Rp 27,000)
   MB-004: Bakso Urat (Rp 35,000 → Rp 30,000)
   ⭐ AG-002: Ayam Geprek Keju (Rp 35,000 → Rp 30,000)
   ⭐ SB-002: Soto Betawi Babat (Rp 35,000 → Rp 29,000)
   ⭐ NG-002: Nasi Goreng Spesial (Rp 28,000 → Rp 23,000)
   NG-004: Nasi Goreng Pete (Rp 32,000 → Rp 27,000)
```

### Step 6: Test di Browser

1. Buka: **http://localhost:5174/kiosk**
2. **Hard Refresh**: `Ctrl + Shift + R`
3. Klik filter **🔥 Promo** → Seharusnya muncul **7 produk**
4. Klik filter **⭐ Populer** → Seharusnya muncul **11 produk**
5. Klik **KEDUA filter** → Seharusnya muncul **5 produk**

---

## 📊 Data Yang Di-Seed

### 🔥 7 Produk Promo:

| Tenant | SKU | Product | Regular | Promo | Diskon |
|--------|-----|---------|---------|-------|--------|
| 🟧 Nasi Padang | NP-002 | Ayam Pop | Rp 38,000 | **Rp 32,000** | 16% |
| 🟧 Nasi Padang | NP-003 | Gulai Ikan | Rp 42,000 | **Rp 36,000** | 14% |
| 🟨 Mie Ayam | MB-002 | Mie Ayam Jumbo | Rp 32,000 | **Rp 27,000** | 16% |
| 🟨 Mie Ayam | MB-004 | Bakso Urat | Rp 35,000 | **Rp 30,000** | 14% |
| 🟥 Ayam Geprek | AG-002 | Ayam Geprek Keju | Rp 35,000 | **Rp 30,000** | 14% |
| 🟡 Soto Betawi | SB-002 | Soto Betawi Babat | Rp 35,000 | **Rp 29,000** | 17% |
| 🟩 Nasi Goreng | NG-002 | Nasi Goreng Spesial | Rp 28,000 | **Rp 23,000** | 18% |
| 🟩 Nasi Goreng | NG-004 | Nasi Goreng Pete | Rp 32,000 | **Rp 27,000** | 16% |

### ⭐ 11 Produk Populer:

1. **NP-001** - Rendang Sapi (Nasi Padang)
2. **NP-003** - Gulai Ikan (Nasi Padang) + Promo
3. **MB-001** - Mie Ayam Spesial (Mie Ayam)
4. **MB-002** - Mie Ayam Jumbo (Mie Ayam) + Promo
5. **MB-006** - Es Teh Manis (Mie Ayam)
6. **AG-001** - Ayam Geprek Original (Geprek)
7. **AG-002** - Ayam Geprek Keju (Geprek) + Promo
8. **AG-004** - Ayam Geprek Jumbo (Geprek)
9. **SB-001** - Soto Betawi Daging (Soto)
10. **SB-002** - Soto Betawi Babat (Soto) + Promo
11. **NG-001** - Nasi Goreng Biasa (Nasi Goreng)
12. **NG-002** - Nasi Goreng Spesial (Nasi Goreng) + Promo
13. **NG-005** - Nasi Goreng Kambing (Nasi Goreng)

### 🌟 5 Produk BEST DEAL (Popular + Promo):

1. **NP-003** - Gulai Ikan (Rp 42,000 → Rp 36,000)
2. **MB-002** - Mie Ayam Jumbo (Rp 32,000 → Rp 27,000)
3. **AG-002** - Ayam Geprek Keju (Rp 35,000 → Rp 30,000)
4. **SB-002** - Soto Betawi Babat (Rp 35,000 → Rp 29,000)
5. **NG-002** - Nasi Goreng Spesial (Rp 28,000 → Rp 23,000)

---

## 🎯 Test Scenarios

### Test 1: Filter Promo
1. Klik tombol **"🔥 Promo"**
2. Hasil: **7 produk** dengan harga coret
3. Contoh: "Ayam Pop: ~~Rp 38,000~~ **Rp 32,000**"

### Test 2: Filter Popular
1. Klik tombol **"⭐ Populer"**
2. Hasil: **11 produk** bestseller
3. Badge "⭐ POPULER" muncul di card

### Test 3: Filter Kombinasi
1. Klik **KEDUA** tombol (Promo + Populer)
2. Hasil: **5 produk** best deals
3. Produk dengan badge "⭐ POPULER" DAN harga promo

### Test 4: Search + Filter
1. Ketik "ayam" di search bar
2. Klik filter **🔥 Promo**
3. Hasil: **AG-002 (Ayam Geprek Keju)** + **NP-002 (Ayam Pop)**

### Test 5: Filter by Tenant + Promo
1. Klik tenant **"🟧 Nasi Padang"**
2. Klik filter **🔥 Promo**
3. Hasil: **2 produk** (Ayam Pop, Gulai Ikan)

---

## 🆘 Troubleshooting

### Masalah: Command tidak ditemukan
**Error:**
```
Unknown command: 'seed_foodcourt'
```

**Fix:**
```powershell
# Pull code terbaru
git pull origin main

# Restart backend
docker-compose restart backend

# Tunggu 10 detik, coba lagi
docker-compose exec backend python manage.py seed_foodcourt
```

### Masalah: Filter masih 0 setelah seed
**Check:**
1. Hard refresh browser: `Ctrl + Shift + R`
2. Check API response di Developer Tools (F12) → Network tab
3. Restart frontend: `docker-compose restart frontend`

**Verify API:**
```powershell
# Test API langsung
curl http://localhost:8001/api/products/products/ | jq '.results | length'
# Expected: 38

# Check promo products
curl http://localhost:8001/api/products/products/ | jq '[.results[] | select(.has_promo == true)] | length'
# Expected: 7
```

### Masalah: Data sudah ada, mau reset
**Reset & Re-seed:**
```powershell
# Masuk Django shell
docker-compose exec backend python manage.py shell
```

Di Python shell:
```python
from apps.tenants.models import Tenant
from apps.products.models import Product, Category

# Hapus semua data
Product.all_objects.all().delete()
Category.all_objects.all().delete()
Tenant.objects.all().delete()

print("✓ Data deleted")
exit()
```

Lalu seed ulang:
```powershell
docker-compose exec backend python manage.py seed_foodcourt
```

---

## 📋 Quick Checklist

- [x] Git pull latest code
- [x] Restart backend
- [x] Run migrations
- [x] Run `seed_foodcourt`
- [x] See "38 Products" in output
- [x] Run `check_promo_data`
- [x] See "7 Promo" in output
- [x] Hard refresh browser
- [x] Click **🔥 Promo** filter
- [x] See **7 products** with promo prices
- [x] Test kombinasi filter

---

## 🎉 Selesai!

Setelah semua step di atas, filter promo Anda akan menampilkan **7 produk** dengan harga diskon!

**Screenshot Expected:**
```
┌─────────────────────────────────────────┐
│ 🔍 Search: [                         ]  │
│ ⭐ Populer  🔥 Promo  ✓ Tersedia       │
│                                         │
│ Results: 7 produk ditemukan            │
│                                         │
│ ┌──────────────────┐ ┌──────────────┐ │
│ │ Ayam Pop         │ │ Gulai Ikan   │ │
│ │ 🟧 Nasi Padang   │ │ 🟧 Nasi Padang│ │
│ │ ~~Rp 38,000~~    │ │ ~~Rp 42,000~~│ │
│ │ Rp 32,000 🔥     │ │ Rp 36,000 🔥 │ │
│ │ [+ Keranjang]    │ │ [+ Keranjang]│ │
│ └──────────────────┘ └──────────────┘ │
│ ...                                     │
└─────────────────────────────────────────┘
```

Selamat mencoba! 🚀
