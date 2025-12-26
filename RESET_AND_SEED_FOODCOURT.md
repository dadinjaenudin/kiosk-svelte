# SOLUSI: Filter Tenant Tidak Muncul

## 🔍 DIAGNOSIS

Dari console log, terlihat:
```
✅ Products loaded: 19
✅ Tenants extracted: 1
🏪 Tenants: Array(1)
```

**Problem**: Hanya ada **1 tenant** (Warung Makan Sedap) dengan 19 produk.

**Root Cause**: Belum menjalankan seed data untuk 5 tenant Food Court.

---

## ✅ SOLUSI - LANGKAH DEMI LANGKAH

### Step 1: Hapus Data Lama

Buka **Command Prompt** atau **PowerShell** di komputer user:

```bash
cd D:\YOGYA-Kiosk\kiosk-svelte

# Hapus semua data lama
docker-compose exec backend python manage.py shell
```

Kemudian di Python shell, ketik:

```python
from apps.tenants.models import Tenant
from apps.products.models import Product, Category

# Hapus semua data
Product.all_objects.all().delete()
Category.all_objects.all().delete()
Tenant.objects.all().delete()

print("✓ Data lama berhasil dihapus")
exit()
```

### Step 2: Seed 5 Tenant Baru

```bash
docker-compose exec backend python manage.py seed_foodcourt
```

**Expected output**:
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
  ✓ Rendang Sapi - Rp 45,000
  ✓ Ayam Pop - Rp 38,000
  ...

(Ulangi untuk 4 tenant lainnya)

============================================================
✅ Food Court Data Seeding Complete!
============================================================

📊 Summary:
   Tenants: 5
   Products: 38
   Categories: 15

🏪 Tenants Created:
   • Warung Nasi Padang (7 products) - Color: #FF6B35
   • Mie Ayam & Bakso (6 products) - Color: #F7931E
   • Ayam Geprek Mantap (6 products) - Color: #DC143C
   • Soto Betawi H. Mamat (6 products) - Color: #FFC300
   • Nasi Goreng Abang (7 products) - Color: #28A745
```

### Step 3: Restart Frontend

```bash
docker-compose restart frontend
```

Tunggu **15 detik** untuk frontend restart.

### Step 4: Test di Browser

1. Buka: http://localhost:5174/kiosk
2. **Hard reload**: Tekan `Ctrl + Shift + R` (atau `Ctrl + F5`)
3. Buka Console: Tekan `F12`

**Expected Console Logs**:
```
Loading food court data...
✅ Products loaded: 38
📦 First product: {name: "Rendang Sapi", tenant_name: "Warung Nasi Padang", ...}
Product: Rendang Sapi, Tenant ID: 1, Tenant Name: Warung Nasi Padang
Product: Ayam Pop, Tenant ID: 1, Tenant Name: Warung Nasi Padang
...
Product: Mie Ayam Spesial, Tenant ID: 2, Tenant Name: Mie Ayam & Bakso
...
✅ Tenants extracted: 5
🏪 Tenants: Array(5)
  [0]: {id: 1, name: "Warung Nasi Padang", slug: "warung-nasi-padang", color: "#FF6B35"}
  [1]: {id: 2, name: "Mie Ayam & Bakso", slug: "mie-ayam-bakso", color: "#F7931E"}
  [2]: {id: 3, name: "Ayam Geprek Mantap", slug: "ayam-geprek", color: "#DC143C"}
  [3]: {id: 4, name: "Soto Betawi H. Mamat", slug: "soto-betawi", color: "#FFC300"}
  [4]: {id: 5, name: "Nasi Goreng Abang", slug: "nasi-goreng", color: "#28A745"}
```

**Expected UI**:
- Section "FILTER BY RESTAURANT:" muncul
- 6 tombol filter:
  - "All Restaurants"
  - 🟧 Warung Nasi Padang
  - 🟨 Mie Ayam & Bakso
  - 🟥 Ayam Geprek Mantap
  - 🟡 Soto Betawi H. Mamat
  - 🟩 Nasi Goreng Abang
- Total 38 produk terlihat

---

## 🧪 VERIFIKASI

### Test 1: Cek Database

```bash
docker-compose exec backend python manage.py shell
```

```python
from apps.tenants.models import Tenant
from apps.products.models import Product

# Harus menunjukkan 5 tenant
for t in Tenant.objects.all():
    count = Product.all_objects.filter(tenant=t).count()
    print(f"{t.name}: {count} products - Color: {t.primary_color}")

# Expected output:
# Warung Nasi Padang: 7 products - Color: #FF6B35
# Mie Ayam & Bakso: 6 products - Color: #F7931E
# Ayam Geprek Mantap: 6 products - Color: #DC143C
# Soto Betawi H. Mamat: 6 products - Color: #FFC300
# Nasi Goreng Abang: 7 products - Color: #28A745
```

### Test 2: Cek API

```bash
curl http://localhost:8001/api/products/products/ | jq '.results | length'
# Expected: 38

curl http://localhost:8001/api/products/products/ | jq '[.results[].tenant_name] | unique'
# Expected: ["Warung Nasi Padang", "Mie Ayam & Bakso", "Ayam Geprek Mantap", "Soto Betawi H. Mamat", "Nasi Goreng Abang"]
```

### Test 3: Test Filter di Browser

1. Klik tombol **"Warung Nasi Padang"**

**Console Log**:
```
🏪 Tenant filter changed: 1
📊 Products before filter: 38
📊 Products after filter: 7
🏪 Selected tenant: Warung Nasi Padang
```

**UI**:
- Hanya 7 produk terlihat (Rendang, Ayam Pop, Gulai Ikan, dll)
- Tombol highlighted dengan border orange
- Produk lain hidden

2. Klik tombol **"All Restaurants"**

**Console Log**:
```
🏪 Tenant filter changed: null
📊 Products before filter: 38
📊 Products after filter: 38
🏪 Showing all restaurants
```

**UI**:
- Semua 38 produk terlihat lagi

---

## 📝 QUICK COMMAND SCRIPT

Buat file `reset_and_seed.bat` di `D:\YOGYA-Kiosk\kiosk-svelte\`:

```batch
@echo off
echo ================================================
echo RESET AND SEED FOOD COURT DATA
echo ================================================
echo.

cd /d D:\YOGYA-Kiosk\kiosk-svelte

echo Step 1: Deleting old data...
docker-compose exec backend python manage.py shell -c "from apps.tenants.models import Tenant; from apps.products.models import Product, Category; Product.all_objects.all().delete(); Category.all_objects.all().delete(); Tenant.objects.all().delete(); print('Old data deleted')"

echo.
echo Step 2: Seeding 5 tenants...
docker-compose exec backend python manage.py seed_foodcourt

echo.
echo Step 3: Restarting frontend...
docker-compose restart frontend

echo.
echo ================================================
echo DONE! Waiting 15 seconds for services...
echo ================================================
timeout /t 15

echo.
echo Open: http://localhost:5174/kiosk
echo Then press Ctrl+Shift+R to hard reload
echo.
pause
```

Kemudian jalankan:
```bash
reset_and_seed.bat
```

---

## ❌ TROUBLESHOOTING

### Problem: Command tidak ditemukan

**Error**:
```
python manage.py seed_foodcourt
python: can't open file 'manage.py'
```

**Fix**: Pastikan path sudah benar
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
docker-compose exec backend python manage.py seed_foodcourt
```

### Problem: Seed command tidak ada

**Error**:
```
Unknown command: 'seed_foodcourt'
```

**Fix**: Pull code terbaru dulu
```bash
git pull origin main
docker-compose restart backend
docker-compose exec backend python manage.py seed_foodcourt
```

### Problem: Filter masih tidak muncul setelah seed

**Check Console**:
- Pastikan log menunjukkan `Tenants extracted: 5`
- Pastikan `Products loaded: 38`

**Fix**:
1. Hard reload: `Ctrl + Shift + R`
2. Clear browser cache
3. Restart frontend: `docker-compose restart frontend`
4. Check API: `curl http://localhost:8001/api/products/products/`

---

## 📊 EXPECTED FINAL RESULT

### Console (F12)
```
✅ Products loaded: 38
✅ Tenants extracted: 5
🏪 Tenants: (5) [{…}, {…}, {…}, {…}, {…}]
```

### UI
```
┌─────────────────────────────────────────────────┐
│ FILTER BY RESTAURANT:                           │
├─────────────────────────────────────────────────┤
│ [All] [🟧Nasi Padang] [🟨Mie Ayam] [🟥Geprek]   │
│       [🟡Soto Betawi] [🟩Nasi Goreng]           │
└─────────────────────────────────────────────────┘

Product Grid (38 items):
┌──────────────────┐ ┌──────────────────┐
│ Rendang Sapi     │ │ Mie Ayam Spesial │
│ 🟧 Nasi Padang   │ │ 🟨 Mie Ayam      │
│ Rp 45,000        │ │ Rp 25,000        │
└──────────────────┘ └──────────────────┘
...
```

---

## ✅ CHECKLIST

- [ ] Run `git pull origin main`
- [ ] Delete old data via shell
- [ ] Run `seed_foodcourt` command
- [ ] See "5 Tenants Created" in output
- [ ] Restart frontend
- [ ] Hard reload browser (Ctrl+Shift+R)
- [ ] Console shows "Products loaded: 38"
- [ ] Console shows "Tenants extracted: 5"
- [ ] UI shows 6 filter buttons
- [ ] Click filter buttons → products filter correctly
- [ ] All 38 products visible with colored badges

---

**Silakan jalankan langkah-langkah di atas dan share screenshot console logs setelah selesai!** 🚀
