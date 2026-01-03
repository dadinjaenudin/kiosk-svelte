# 📋 Product Modifiers Documentation

Dokumentasi lengkap tentang modifiers yang di-seed untuk setiap tenant di Food Court.

## 🎯 Overview

Setelah menjalankan `python manage.py seed_foodcourt`, sistem akan membuat **~100+ modifiers** untuk 38 products di 5 tenants. Modifiers memungkinkan customer untuk customize order mereka dengan pilihan:

- **Size** - Porsi Kecil/Sedang/Besar
- **Spicy Level** - Level 1-5 (Tidak Pedas sampai Extra Pedas)
- **Toppings** - Extra Keju, Telur, dll
- **Extras** - Extra Daging, Nasi, Mie, dll
- **Sauce** - Kuah Santan/Bening

---

## 🏪 Modifiers by Tenant

### 1. 🟧 Warung Nasi Padang

**Products dengan Modifiers:** NP-001, NP-002, NP-003, NP-004, NP-005
- Rendang Sapi
- Ayam Pop
- Gulai Ikan
- Dendeng Balado
- Gulai Tunjang

**Modifiers Available:**

| Type | Name | Price Adjustment |
|------|------|------------------|
| size | Porsi Kecil | -Rp 5,000 |
| size | Porsi Sedang | Rp 0 (gratis) |
| size | Porsi Besar | +Rp 8,000 |
| extra | Extra Sambal | +Rp 2,000 |
| extra | Extra Nasi | +Rp 5,000 |

**Use Case:**
- Customer pesan Rendang Sapi (Rp 45,000)
- Pilih **Porsi Besar** (+Rp 8,000)
- Pilih **Extra Sambal** (+Rp 2,000)
- **Total: Rp 55,000**

---

### 2. 🟨 Mie Ayam & Bakso

#### A. Mie Ayam Products (MB-001, MB-002)
- Mie Ayam Spesial
- Mie Ayam Jumbo

**Modifiers:**

| Type | Name | Price Adjustment |
|------|------|------------------|
| extra | Pangsit Goreng | +Rp 3,000 |
| extra | Extra Ayam | +Rp 8,000 |
| extra | Extra Mie | +Rp 5,000 |
| extra | Tidak Pakai Sawi | Rp 0 (gratis) |

#### B. Bakso Products (MB-003, MB-004, MB-005)
- Bakso Sapi
- Bakso Urat
- Bakso Campur

**Modifiers:**

| Type | Name | Price Adjustment |
|------|------|------------------|
| extra | Extra Bakso (2 pcs) | +Rp 10,000 |
| extra | Extra Mie | +Rp 5,000 |
| spicy | Kuah Pedas | Rp 0 (gratis) |
| extra | Kuah Ekstra | +Rp 3,000 |

**Use Case:**
- Customer pesan Mie Ayam Spesial (Rp 25,000)
- Pilih **Pangsit Goreng** (+Rp 3,000)
- Pilih **Extra Ayam** (+Rp 8,000)
- **Total: Rp 36,000**

---

### 3. 🟥 Ayam Geprek Mantap

**Products dengan Modifiers:** AG-001, AG-002, AG-003, AG-004
- Ayam Geprek Original
- Ayam Geprek Keju
- Ayam Geprek Mozarella
- Ayam Geprek Jumbo

**Modifiers:**

| Type | Name | Price Adjustment |
|------|------|------------------|
| spicy | Level 1 (Tidak Pedas) | Rp 0 (gratis) |
| spicy | Level 2 (Sedang) | Rp 0 (gratis) |
| spicy | Level 3 (Pedas) | Rp 0 (gratis) |
| spicy | Level 4 (Sangat Pedas) | Rp 0 (gratis) |
| spicy | Level 5 (Extra Pedas) | Rp 0 (gratis) |
| topping | Extra Keju | +Rp 7,000 |
| extra | Extra Nasi | +Rp 5,000 |
| extra | Tanpa Nasi | -Rp 5,000 |

**UI Display:**
- **Level Pedas** ditampilkan secara **inline horizontal** dengan checkbox
- **Topping/Extra** ditampilkan secara **inline horizontal** dengan checkbox

**Use Case:**
- Customer pesan Ayam Geprek Original (Rp 28,000)
- Pilih **Level 3 (Pedas)** (Rp 0)
- Pilih **Extra Keju** (+Rp 7,000)
- Pilih **Extra Nasi** (+Rp 5,000)
- **Total: Rp 40,000**

---

### 4. 🟡 Soto Betawi H. Mamat

**Products dengan Modifiers:** SB-001, SB-002, SB-003, SB-004
- Soto Betawi Daging
- Soto Betawi Babat
- Soto Betawi Paru
- Soto Betawi Campur

**Modifiers:**

| Type | Name | Price Adjustment |
|------|------|------------------|
| sauce | Kuah Santan | Rp 0 (gratis) |
| sauce | Kuah Bening | Rp 0 (gratis) |
| topping | Emping | +Rp 5,000 |
| extra | Jeruk Limau | +Rp 2,000 |
| extra | Extra Daging | +Rp 12,000 |
| spicy | Sambal Rawit | Rp 0 (gratis) |

**Use Case:**
- Customer pesan Soto Betawi Daging (Rp 38,000)
- Pilih **Kuah Santan** (Rp 0)
- Pilih **Emping** (+Rp 5,000)
- Pilih **Extra Daging** (+Rp 12,000)
- Pilih **Sambal Rawit** (Rp 0)
- **Total: Rp 55,000**

---

### 5. 🟩 Nasi Goreng Abang

**Products dengan Modifiers:** NG-001, NG-002, NG-003, NG-004, NG-005
- Nasi Goreng Biasa
- Nasi Goreng Spesial
- Nasi Goreng Seafood
- Nasi Goreng Pete
- Nasi Goreng Kambing

**Modifiers:**

| Type | Name | Price Adjustment |
|------|------|------------------|
| topping | Telur Mata Sapi | +Rp 5,000 |
| topping | Telur Dadar | +Rp 4,000 |
| extra | Extra Ayam | +Rp 10,000 |
| extra | Extra Seafood | +Rp 15,000 |
| extra | Kerupuk | +Rp 3,000 |
| extra | Acar | +Rp 2,000 |
| spicy | Level Pedas (1-5) | Rp 0 (gratis) |

**Use Case:**
- Customer pesan Nasi Goreng Biasa (Rp 20,000)
- Pilih **Telur Mata Sapi** (+Rp 5,000)
- Pilih **Extra Ayam** (+Rp 10,000)
- Pilih **Kerupuk** (+Rp 3,000)
- Pilih **Level Pedas (1-5)** (Rp 0)
- **Total: Rp 38,000**

---

## 📊 Modifier Statistics

### Total Counts per Tenant:

| Tenant | Products with Modifiers | Total Modifiers |
|--------|-------------------------|-----------------|
| 🟧 Nasi Padang | 5 | 25 (5 modifiers × 5 products) |
| 🟨 Mie Ayam | 5 | 24 (4 modifiers × 2 mie + 4 modifiers × 3 bakso) |
| 🟥 Ayam Geprek | 4 | 32 (8 modifiers × 4 products) |
| 🟡 Soto Betawi | 4 | 24 (6 modifiers × 4 products) |
| 🟩 Nasi Goreng | 5 | 35 (7 modifiers × 5 products) |
| **TOTAL** | **23 products** | **~140 modifiers** |

---

## 🧪 Testing Modifiers

### Test 1: Pilih Product dengan Modifiers

1. Buka http://localhost:5174/kiosk
2. Klik product **"Ayam Geprek Original"**
3. Modal modifiers akan muncul
4. Seharusnya ada **8 modifiers**:
   - 5 Level Pedas (horizontal inline)
   - 1 Extra Keju (horizontal inline)
   - 1 Extra Nasi (horizontal inline)
   - 1 Tanpa Nasi (horizontal inline)

### Test 2: Price Calculation

1. Pilih **Ayam Geprek Original** (Rp 28,000)
2. Pilih **Level 3 (Pedas)** (Rp 0)
3. Pilih **Extra Keju** (+Rp 7,000)
4. Klik **"Tambah ke Keranjang"**
5. Check cart:
   - Item: Ayam Geprek Original
   - Modifiers: Level 3, Extra Keju
   - **Price: Rp 35,000** (28,000 + 0 + 7,000)

### Test 3: Negative Price Adjustment

1. Pilih **Nasi Padang - Rendang Sapi** (Rp 45,000)
2. Pilih **Porsi Kecil** (-Rp 5,000)
3. Total: **Rp 40,000** (45,000 - 5,000)

### Test 4: Multiple Modifiers

1. Pilih **Soto Betawi Daging** (Rp 38,000)
2. Pilih **Kuah Santan** (Rp 0)
3. Pilih **Emping** (+Rp 5,000)
4. Pilih **Extra Daging** (+Rp 12,000)
5. Total: **Rp 55,000** (38,000 + 0 + 5,000 + 12,000)

---

## 🔧 Technical Details

### Database Schema:

```python
class ProductModifier(models.Model):
    product = ForeignKey(Product)        # Parent product
    name = CharField(max_length=100)     # "Extra Keju", "Level 3"
    type = CharField(max_length=50)      # "spicy", "topping", "extra", "size", "sauce"
    price_adjustment = DecimalField()    # Can be negative, zero, or positive
    is_active = BooleanField()           # Enable/disable modifier
    sort_order = IntegerField()          # Display order in modal
```

### API Response Example:

```json
{
  "id": 2,
  "sku": "AG-001",
  "name": "Ayam Geprek Original",
  "price": "28000.00",
  "modifiers": [
    {
      "id": 15,
      "name": "Level 1 (Tidak Pedas)",
      "type": "spicy",
      "price_adjustment": "0.00",
      "is_active": true,
      "sort_order": 1
    },
    {
      "id": 16,
      "name": "Level 2 (Sedang)",
      "type": "spicy",
      "price_adjustment": "0.00",
      "is_active": true,
      "sort_order": 2
    },
    {
      "id": 20,
      "name": "Extra Keju",
      "type": "topping",
      "price_adjustment": "7000.00",
      "is_active": true,
      "sort_order": 6
    }
  ]
}
```

### Frontend Display Logic:

```javascript
// Group modifiers by type
const modifiersByType = {
  spicy: [...],      // Display inline horizontal
  topping: [...],    // Display inline horizontal  
  extra: [...],      // Display inline horizontal
  size: [...],       // Display as buttons
  sauce: [...]       // Display as buttons
};

// Calculate total price
const totalPrice = basePrice + modifiers.reduce((sum, mod) => {
  return sum + parseFloat(mod.price_adjustment);
}, 0);
```

---

## 🎨 UI/UX Guidelines

### Inline Display (Horizontal)
Types: **spicy**, **topping**, **extra**

Display as horizontal pills dengan checkmark:
```
Level Pedas:
[ ] Level 1  [ ] Level 2  [✓] Level 3  [ ] Level 4  [ ] Level 5

Topping:
[✓] Extra Keju  [ ] Extra Nasi  [ ] Tanpa Nasi
```

### Button Display (Vertical)
Types: **size**, **sauce**

Display as clickable buttons:
```
Porsi:
● Porsi Kecil (-Rp 5,000)
○ Porsi Sedang (Rp 0)
○ Porsi Besar (+Rp 8,000)
```

---

## 📱 Mobile Responsive

Modal modifiers sudah responsive untuk mobile:
- Compact layout dengan 2-3 kolom inline
- Scrollable jika modifiers terlalu banyak
- Touch-friendly button size (min 44x44px)
- Clear price indication (+/- Rp)

---

## 💡 Business Logic

### Rules:

1. **Multiple Selection Allowed** - Customer bisa pilih lebih dari 1 modifier per type (contoh: Extra Keju + Extra Nasi)

2. **Price Adjustment Can Be:**
   - **Positive** (+Rp) - Extra topping/daging
   - **Zero** (Rp 0) - Free options seperti level pedas
   - **Negative** (-Rp) - Discount untuk porsi kecil atau tanpa nasi

3. **Cart Display** - Modifiers harus terlihat jelas di cart dengan:
   - Modifier name
   - Price adjustment
   - Included in subtotal

4. **Receipt Printing** - Modifiers harus muncul di receipt dengan indentasi

---

## 🚀 Future Enhancements

Possible improvements:

1. **Modifier Groups** - Force customer pilih minimal 1 per group (contoh: wajib pilih 1 level pedas)

2. **Max Selection** - Limit berapa banyak extras yang bisa dipilih

3. **Conditional Modifiers** - Modifiers yang muncul based on other selections

4. **Image for Modifiers** - Visual representation untuk level pedas, size, etc

5. **Modifier Availability** - Enable/disable modifiers based on stock

---

## 📝 Summary

Setelah menjalankan `seed_foodcourt`, Anda akan memiliki:

✅ **38 products** di 5 tenants  
✅ **~140 modifiers** dengan berbagai types  
✅ **Price adjustments** dari -Rp 5,000 sampai +Rp 15,000  
✅ **Inline display** untuk spicy/topping/extra  
✅ **Button display** untuk size/sauce  
✅ **Cart calculation** yang include modifiers  

Customers dapat fully customize orders mereka sesuai preferensi! 🎉
