# Quick Setup Guide - Search Features

## 🚀 Quick Start

### 1. Pull Latest Changes
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
```

### 2. Restart Services
```bash
docker-compose restart backend frontend
```

### 3. Run Database Migration
```bash
docker-compose exec backend python manage.py migrate products
```

### 4. Populate Sample Data
```bash
cd backend
./populate_search_data.sh
```

**OR manually:**
```bash
docker-compose exec -T db psql -U postgres -d kiosk_pos -f backend/sample_data_search.sql
```

### 5. Test the Features
Open: http://localhost:5174/kiosk

---

## 📊 Sample Data Overview

### Products with Flags:

**⭐ Popular Items (12):**
- Ayam Geprek Original
- Ayam Geprek Keju
- Ayam Geprek Jumbo
- Ayam Geprek Pedas Gila (SOLD OUT)
- Soto Ayam
- Soto Betawi
- Nasi Rendang
- Nasi Gulai Kambing
- Mie Ayam Original
- Mie Ayam Bakso
- Es Teh Manis
- Es Campur

**🔥 Promo Items (7):**
- Ayam Geprek Keju: Rp 42.000 → **Rp 38.000**
- Ayam Geprek Mozarella: Rp 48.000 → **Rp 43.000**
- Soto Betawi: Rp 32.000 → **Rp 27.000**
- Nasi Gulai Ayam: Rp 28.000 → **Rp 22.000**
- Nasi Gulai Kambing: Rp 45.000 → **Rp 38.000**
- Mie Ayam Bakso: Rp 22.000 → **Rp 18.000**
- Jus Alpukat: Rp 15.000 → **Rp 12.000**

**❌ Sold Out (2):**
- Ayam Geprek Pedas Gila
- Nasi Ayam Pop

---

## 🧪 Test Scenarios

### 1. Search Test
```
🔍 Type "nasi"
Expected: 5 Nasi Padang products

🔍 Type "ayam geprek"
Expected: 6 Ayam Geprek products

🔍 Type "pedas"
Expected: Spicy items (Ayam Geprek, Dendeng Balado)
```

### 2. Quick Filter Test
```
Click [⭐ Populer]
Expected: 12 products (green button)

Click [🔥 Promo]
Expected: 7 products with discounted prices

Click [✓ Tersedia] (toggle OFF)
Expected: All 20+ products including sold out
```

### 3. Combined Filter Test
```
🔍 Search: "nasi"
⭐ Popular: ON
🔥 Promo: ON
Expected: "Nasi Gulai Kambing" (popular + promo)
```

---

## 🎨 Expected UI

```
┌─────────────────────────────────┐
│ ☰ 🍽️ Food Court Kiosk    🛒[1]│
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │🔍 Cari nasi goreng...    ✕ │ │
│ └─────────────────────────────┘ │
│ [⭐ Populer] [🔥 Promo]         │
│ [✓ Tersedia]                    │
│ Results: 5 produk ditemukan     │
├─────────────────────────────────┤
│ ┌──────┬──────┐                 │
│ │ 🍔   │ 🍔   │                 │
│ │ PROMO│ ⭐   │  ← Badges       │
│ └──────┴──────┘                 │
└─────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Issue: No products showing filters
**Solution:**
```bash
# Check database
docker-compose exec db psql -U postgres -d kiosk_pos
SELECT name, is_popular, has_promo, is_available FROM products LIMIT 5;
```

### Issue: SQL file not found
**Solution:**
```bash
# Make sure you're in the right directory
cd D:\YOGYA-Kiosk\kiosk-svelte\backend
ls -la sample_data_search.sql
```

### Issue: Migration error
**Solution:**
```bash
# Run migration manually
docker-compose exec backend python manage.py migrate products 0002
```

---

## 📝 Manual SQL (If Script Fails)

```bash
docker-compose exec db psql -U postgres -d kiosk_pos

-- Add columns
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_popular BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS has_promo BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS promo_price DECIMAL(10,2);

-- Update some products manually
UPDATE products SET is_popular = TRUE WHERE sku IN ('AG-001', 'AG-002', 'AG-004', 'SH-001', 'SH-002', 'NP-001', 'MA-001', 'MA-002');
UPDATE products SET has_promo = TRUE, promo_price = price * 0.9 WHERE sku IN ('AG-002', 'SH-002', 'NP-003', 'MA-002');
UPDATE products SET is_available = FALSE WHERE sku IN ('AG-006', 'NP-005');
```

---

## ✅ Verification

After setup, verify:

1. **Frontend loads**: http://localhost:5174/kiosk
2. **Search works**: Type something and see results
3. **Filters work**: Click buttons and see them turn green
4. **Counter shows**: "Results: X produk ditemukan"
5. **Product badges**: See ⭐ and 🔥 on products

---

**Ready to test!** 🎉
