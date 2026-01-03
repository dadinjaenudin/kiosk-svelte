# 🚀 Quick Start: Test Promo Filter

## Langkah Cepat (5 Menit)

### 1️⃣ Jalankan Migration & Seed Data

```bash
# Step 1: Jalankan migration (jika belum)
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Step 2: Seed data sample dengan flag promo/popular
docker-compose exec backend python manage.py seed_foodcourt

# Expected output:
# 🌱 Starting seed process...
# 🍗 Seeding Ayam Geprek Mantap...
#    ✓ Updated 6 Ayam Geprek products
# 🍜 Seeding Soto House...
#    ✓ Updated 4 Soto House products
# ...
# ✅ Sample data seeded successfully!
# 📊 Summary:
#    Total Products: 20+
#    ⭐ Popular: 8+ products
#    🔥 Promo: 7+ products
```

### 2️⃣ Verifikasi Data di Database

```bash
# Cek status dengan command khusus
docker-compose exec backend python manage.py check_promo_data

# Expected output:
# 🔍 Checking database status...
# 📊 Database Summary:
#    Total Products: 20+
#    ⭐ Popular: 8
#    🔥 Promo: 7
#    ✓ Available: 18
#    🌟 Popular + Promo: 4
#
# 🔥 Promo Products (7):
#    ⭐ AG-002: Ayam Geprek Keju (Rp 42,000 → Rp 38,000)
#    AG-005: Ayam Geprek Mozarella (Rp 48,000 → Rp 43,000)
#    ...
```

### 3️⃣ Test di Browser

1. **Buka aplikasi**: http://localhost:5174/kiosk

2. **Hard refresh browser**: 
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

3. **Test filter Promo**:
   - Klik tombol **"🔥 Promo"**
   - Seharusnya muncul **7 produk** dengan harga promo

4. **Test filter Popular**:
   - Klik tombol **"⭐ Populer"**
   - Seharusnya muncul **8 produk**

5. **Test kombinasi**:
   - Klik **KEDUA** tombol (Populer + Promo)
   - Seharusnya muncul **4 produk**:
     - Ayam Geprek Keju
     - Soto Betawi
     - Nasi Gulai Kambing
     - Mie Ayam Bakso

## 🔍 Jika Masih 0 Produk

### Cek API Response

1. Buka **Developer Tools** (F12)
2. Tab **Network**
3. Refresh halaman
4. Cari request `/api/products/`
5. Klik → Tab **Response**
6. Cari satu product dan pastikan ada field:

```json
{
  "id": 2,
  "name": "Ayam Geprek Keju",
  "price": "42000.00",
  "is_popular": true,      ← HARUS ADA
  "has_promo": true,       ← HARUS ADA
  "promo_price": "38000.00" ← HARUS ADA
}
```

**Jika field tidak ada**:
- Backend belum restart setelah migration
- Serializer belum update
- Jalankan: `docker-compose restart backend`

### Cek Browser Console

1. Developer Tools → Tab **Console**
2. Ketik command ini:

```javascript
// Cek total products loaded
console.log('Total products:', products.length)

// Cek products dengan promo
console.log('Promo products:', products.filter(p => p.has_promo).length)

// Lihat detail 1 product
console.log(products[0])
```

**Jika `has_promo` undefined**:
- API tidak mengirim field tersebut
- Perlu restart backend

### Restart Semua (Nuclear Option)

```bash
# Stop semua container
docker-compose down

# Build ulang (jika ada perubahan code)
docker-compose build

# Start kembali
docker-compose up -d

# Tunggu backend siap (30 detik)
sleep 30

# Jalankan seed lagi
docker-compose exec backend python manage.py seed_foodcourt

# Buka browser dan hard refresh
```

## 📊 Expected Results Summary

Setelah setup berhasil:

| Filter | Jumlah Produk |
|--------|---------------|
| Semua (tanpa filter) | 20+ |
| ⭐ Populer | 8 |
| 🔥 Promo | 7 |
| ✓ Tersedia | 18 |
| ⭐ + 🔥 (keduanya) | 4 |

## 🆘 Troubleshooting Lengkap

Lihat file: **`TROUBLESHOOTING_PROMO.md`**

Atau jalankan diagnostic:
```bash
docker-compose exec backend python manage.py check_promo_data
```

## 📞 Butuh Help?

Jika masih tidak bisa, capture:
1. Screenshot hasil dari `check_promo_data`
2. Screenshot Network tab (API response)
3. Screenshot Console tab (errors jika ada)
4. Screenshot halaman dengan 0 results
