# 🔍 Troubleshooting: Filter Promo Kosong

## Masalah
Ketika menekan tombol "🔥 Promo", hasil menunjukkan **0 produk ditemukan**.

## Kemungkinan Penyebab

### 1. Data Belum Di-Seed
Database masih kosong atau field `has_promo`, `is_popular`, `promo_price` belum di-update.

**✅ Solusi:**
```bash
# Jalankan command seed
docker-compose exec backend python manage.py seed_foodcourt

# Atau jika ingin reset dulu
docker-compose exec backend python manage.py seed_foodcourt --clear
```

### 2. Migration Belum Dijalankan
Field `is_popular`, `has_promo`, `promo_price` belum ada di database.

**✅ Solusi:**
```bash
# Jalankan migration
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### 3. API Tidak Mengembalikan Field yang Benar
Backend tidak mengirim field `has_promo`, `is_popular`, dll.

**✅ Cara Cek:**
1. Buka browser Developer Tools (F12)
2. Buka tab **Network**
3. Refresh halaman kiosk
4. Cari request ke `/api/products/`
5. Lihat Response - pastikan ada field:
   - `is_popular`: true/false
   - `has_promo`: true/false
   - `promo_price`: angka atau null

**Contoh Response yang Benar:**
```json
{
  "id": 2,
  "sku": "AG-002",
  "name": "Ayam Geprek Keju",
  "price": "42000.00",
  "is_popular": true,
  "has_promo": true,
  "promo_price": "38000.00",
  "is_available": true
}
```

### 4. Frontend Cache Masih Lama
Browser masih menggunakan data lama yang tidak ada field promo.

**✅ Solusi:**
1. Hard refresh browser: `Ctrl + Shift + R` (Windows/Linux) atau `Cmd + Shift + R` (Mac)
2. Clear browser cache
3. Atau buka Incognito/Private Window

### 5. Product SKU Tidak Cocok
Command seed mencari product berdasarkan SKU. Jika SKU di database berbeda, data tidak akan ter-update.

**✅ Cara Cek:**
```bash
# Masuk ke Django shell
docker-compose exec backend python manage.py shell

# Cek SKU yang ada
from apps.products.models import Product
print(Product.objects.values_list('sku', 'name'))

# Cek product dengan promo
print(Product.objects.filter(has_promo=True).count())
```

**Expected Output:**
```python
# Seharusnya ada minimal 7 product dengan has_promo=True:
# AG-002, AG-005, SH-002, NP-002, NP-003, MA-002, BV-003
```

## Verifikasi Step-by-Step

### Step 1: Cek Database
```bash
# Masuk ke PostgreSQL
docker-compose exec db psql -U kiosk_user -d kiosk_db

# Cek apakah column ada
\d products_product

# Cek data promo
SELECT sku, name, has_promo, promo_price, is_popular FROM products_product WHERE has_promo = true;

# Expected: 7 rows
```

### Step 2: Cek API Response
```bash
# Test API langsung
curl http://localhost:8000/api/products/ | jq '.[] | select(.has_promo == true) | {sku, name, has_promo, promo_price}'

# Expected: 7 products dengan has_promo=true
```

### Step 3: Cek Frontend Console
1. Buka http://localhost:5174/kiosk
2. Buka Developer Tools (F12)
3. Buka tab **Console**
4. Ketik:
```javascript
// Cek semua products
console.table(
  products.map(p => ({
    name: p.name,
    popular: p.is_popular,
    promo: p.has_promo,
    available: p.is_available
  }))
)

// Cek products dengan promo
console.log('Products with promo:', products.filter(p => p.has_promo))
```

## Expected Data Setelah Seed

Setelah menjalankan `seed_foodcourt`, seharusnya ada:

### 7 Products dengan Promo (🔥):
1. **AG-002** - Ayam Geprek Keju (Rp 42,000 → Rp 38,000)
2. **AG-005** - Ayam Geprek Mozarella (Rp 48,000 → Rp 43,000)
3. **SH-002** - Soto Betawi (Rp 32,000 → Rp 27,000)
4. **NP-002** - Nasi Gulai Ayam (Rp 28,000 → Rp 22,000)
5. **NP-003** - Nasi Gulai Kambing (Rp 45,000 → Rp 38,000)
6. **MA-002** - Mie Ayam Bakso (Rp 22,000 → Rp 18,000)
7. **BV-003** - Jus Alpukat (Rp 15,000 → Rp 12,000)

### 8 Products Populer (⭐):
1. AG-001, AG-002, AG-004, AG-006
2. SH-001, SH-002
3. NP-001, NP-003
4. MA-001, MA-002
5. BV-001, DS-001

### 4 Products Populer + Promo (⭐🔥):
1. **AG-002** - Ayam Geprek Keju
2. **SH-002** - Soto Betawi
3. **NP-003** - Nasi Gulai Kambing
4. **MA-002** - Mie Ayam Bakso

## Quick Test

Setelah seed, test dengan:

1. ✅ Klik filter **⭐ Populer** → Seharusnya ada **8 produk**
2. ✅ Klik filter **🔥 Promo** → Seharusnya ada **7 produk**
3. ✅ Klik **KEDUA filter** (Populer + Promo) → Seharusnya ada **4 produk**
4. ✅ Search "ayam" + filter Promo → Seharusnya ada **AG-002, MA-002**

## Jika Masih Kosong

Jika setelah semua step di atas masih kosong:

1. **Restart semua container:**
```bash
docker-compose down
docker-compose up -d
```

2. **Re-run migrations dan seed:**
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed_foodcourt --clear
```

3. **Clear browser cache dan hard refresh**

4. **Cek logs untuk error:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

## Kontak Support

Jika masih ada masalah, berikan informasi berikut:
- Output dari `docker-compose exec backend python manage.py seed_foodcourt`
- Screenshot dari Network tab (API response)
- Screenshot dari Console tab (JavaScript errors)
- Output dari `SELECT COUNT(*) FROM products_product WHERE has_promo = true;`
