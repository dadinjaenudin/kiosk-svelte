# Sample Data untuk Fitur Search

## Overview
File ini berisi sample data untuk menguji fitur search dengan filter:
- ⭐ **Populer** (Popular/Bestseller items)
- 🔥 **Promo** (Items with active promotions)
- ✓ **Tersedia** (Available items only)

## Data Summary

### 📊 Statistics
- **Total Products**: 20+
- **Popular Items**: 12 products
- **Promo Items**: 7 products
- **Available**: 18 products
- **Sold Out**: 2 products

---

## 🍗 AYAM GEPREK MANTAP

| SKU | Product | Popular | Promo | Available | Price | Promo Price |
|-----|---------|---------|-------|-----------|-------|-------------|
| AG-001 | Ayam Geprek Original | ⭐ | ❌ | ✓ | Rp 40.000 | - |
| AG-002 | Ayam Geprek Keju | ⭐ | 🔥 | ✓ | Rp 42.000 | **Rp 38.000** |
| AG-003 | Ayam Geprek Sambal Matah | ❌ | ❌ | ✓ | Rp 43.000 | - |
| AG-004 | Ayam Geprek Jumbo | ⭐ | ❌ | ✓ | Rp 45.000 | - |
| AG-005 | Ayam Geprek Mozarella | ❌ | 🔥 | ✓ | Rp 48.000 | **Rp 43.000** |
| AG-006 | Ayam Geprek Pedas Gila | ⭐ | ❌ | ❌ | Rp 42.000 | - |

**Tags**: `pedas`, `ayam`, `geprek`, `populer`, `keju`, `jumbo`, `sold out`

---

## 🍜 SOTO HOUSE

| SKU | Product | Popular | Promo | Available | Price | Promo Price |
|-----|---------|---------|-------|-----------|-------|-------------|
| SH-001 | Soto Ayam | ⭐ | ❌ | ✓ | Rp 25.000 | - |
| SH-002 | Soto Betawi | ⭐ | 🔥 | ✓ | Rp 32.000 | **Rp 27.000** |
| SH-003 | Soto Kudus | ❌ | ❌ | ✓ | Rp 28.000 | - |
| SH-004 | Soto Daging | ❌ | ❌ | ✓ | Rp 30.000 | - |

**Tags**: `soto`, `ayam`, `sapi`, `berkuah`, `hangat`, `populer`, `betawi`

---

## 🍛 NASI PADANG SEDERHANA

| SKU | Product | Popular | Promo | Available | Price | Promo Price |
|-----|---------|---------|-------|-----------|-------|-------------|
| NP-001 | Nasi Rendang | ⭐ | ❌ | ✓ | Rp 35.000 | - |
| NP-002 | Nasi Gulai Ayam | ❌ | 🔥 | ✓ | Rp 28.000 | **Rp 22.000** |
| NP-003 | Nasi Gulai Kambing | ⭐ | 🔥 | ✓ | Rp 45.000 | **Rp 38.000** |
| NP-004 | Nasi Dendeng Balado | ❌ | ❌ | ✓ | Rp 32.000 | - |
| NP-005 | Nasi Ayam Pop | ❌ | ❌ | ❌ | Rp 30.000 | - |

**Tags**: `nasi`, `rendang`, `gulai`, `kambing`, `padang`, `populer`, `sold out`

---

## 🍝 MIE AYAM BAROKAH

| SKU | Product | Popular | Promo | Available | Price | Promo Price |
|-----|---------|---------|-------|-----------|-------|-------------|
| MA-001 | Mie Ayam Original | ⭐ | ❌ | ✓ | Rp 15.000 | - |
| MA-002 | Mie Ayam Bakso | ⭐ | 🔥 | ✓ | Rp 22.000 | **Rp 18.000** |
| MA-003 | Mie Ayam Jumbo | ❌ | ❌ | ✓ | Rp 25.000 | - |
| MA-004 | Mie Ayam Pangsit | ❌ | ❌ | ✓ | Rp 20.000 | - |

**Tags**: `mie`, `ayam`, `bakso`, `pangsit`, `populer`, `jumbo`

---

## 🥤 MINUMAN & DESSERT

| SKU | Product | Popular | Promo | Available | Price | Promo Price |
|-----|---------|---------|-------|-----------|-------|-------------|
| BV-001 | Es Teh Manis | ⭐ | ❌ | ✓ | Rp 5.000 | - |
| BV-002 | Es Jeruk | ❌ | ❌ | ✓ | Rp 8.000 | - |
| BV-003 | Jus Alpukat | ❌ | 🔥 | ✓ | Rp 15.000 | **Rp 12.000** |
| DS-001 | Es Campur | ⭐ | ❌ | ✓ | Rp 12.000 | - |

**Tags**: `minuman`, `es`, `teh`, `jeruk`, `jus`, `dessert`, `populer`

---

## 🧪 Test Scenarios

### 1. Search by Name
```
Query: "nasi"
Expected: 5 products from Nasi Padang
```

### 2. Search by Description
```
Query: "pedas"
Expected: Ayam Geprek products + Dendeng Balado
```

### 3. Search by Tenant
```
Query: "soto"
Expected: 4 products from Soto House
```

### 4. Popular Filter
```
Filter: ⭐ Populer
Expected: 12 products
- AG-001, AG-002, AG-004, AG-006
- SH-001, SH-002
- NP-001, NP-003
- MA-001, MA-002
- BV-001, DS-001
```

### 5. Promo Filter
```
Filter: 🔥 Promo
Expected: 7 products with discounts
- AG-002: Rp 42k → Rp 38k
- AG-005: Rp 48k → Rp 43k
- SH-002: Rp 32k → Rp 27k
- NP-002: Rp 28k → Rp 22k
- NP-003: Rp 45k → Rp 38k
- MA-002: Rp 22k → Rp 18k
- BV-003: Rp 15k → Rp 12k
```

### 6. Available Filter
```
Filter: ✓ Tersedia (default ON)
Expected: 18 products (excludes AG-006, NP-005)

Toggle OFF:
Expected: All 20 products including sold out
```

### 7. Combined Filters
```
Search: "ayam"
Filter: ⭐ Populer + 🔥 Promo
Expected: AG-002 (Ayam Geprek Keju), MA-002 (Mie Ayam Bakso)
```

### 8. Complex Search
```
Search: "nasi gulai"
Filter: 🔥 Promo
Expected: NP-002 (Nasi Gulai Ayam), NP-003 (Nasi Gulai Kambing)
```

---

## 🚀 Installation

### Step 1: Run Migration
```bash
cd /home/user/webapp
docker-compose exec backend python manage.py migrate products
```

### Step 2: Populate Data
```bash
cd /home/user/webapp/backend
./populate_search_data.sh
```

### Alternative (Manual SQL)
```bash
docker-compose exec -T db psql -U postgres -d kiosk_pos < sample_data_search.sql
```

---

## 📝 Database Schema Changes

### New Fields Added:
```sql
ALTER TABLE products ADD COLUMN is_popular BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN has_promo BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN promo_price DECIMAL(10,2);
```

### Updated Product Model:
```python
class Product(TenantModel):
    # ... existing fields ...
    
    # New flags
    is_popular = models.BooleanField(default=False, help_text='Popular/Bestseller item')
    has_promo = models.BooleanField(default=False, help_text='Item has active promotion')
    promo_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
```

---

## 🎯 Expected UI Behavior

### Search Input
- Type "nasi" → Shows all nasi products
- Type "pedas" → Shows spicy items
- Type "ayam geprek" → Shows Ayam Geprek products

### Quick Filters
- Click [⭐ Populer] → Green button, shows 12 popular items
- Click [🔥 Promo] → Green button, shows 7 promo items
- Click [✓ Tersedia] → Toggle availability (default ON)

### Result Counter
```
Results: 12 produk ditemukan
```
Shows when any filter is active

---

## 🐛 Troubleshooting

### Products not showing filters?
Check if fields exist:
```sql
SELECT is_popular, has_promo, promo_price FROM products LIMIT 5;
```

### All filters returning 0 results?
Run the SQL update script again:
```bash
docker-compose exec -T db psql -U postgres -d kiosk_pos < sample_data_search.sql
```

### Search not working?
Check frontend filteredProducts logic includes all fields:
```javascript
if (showPopular && !p.is_popular) return false;
if (showPromo && !p.has_promo) return false;
if (showAvailable && !p.is_available) return false;
```

---

## 📊 Data Distribution

```
Category Distribution:
├─ Ayam Geprek: 6 products (3 popular, 2 promo, 1 sold out)
├─ Soto: 4 products (2 popular, 1 promo)
├─ Nasi Padang: 5 products (2 popular, 2 promo, 1 sold out)
├─ Mie Ayam: 4 products (2 popular, 1 promo)
└─ Minuman: 4 products (2 popular, 1 promo)

Total: 20+ products
```

---

**Last Updated**: 2025-12-27
**Version**: 1.0
**Author**: Kiosk POS Team
