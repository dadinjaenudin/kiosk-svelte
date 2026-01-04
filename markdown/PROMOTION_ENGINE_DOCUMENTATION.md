# Promotion Engine - Complete Documentation

## Overview
Promotion Engine adalah sistem untuk mengelola berbagai jenis promosi di aplikasi POS Kiosk. Sistem ini mendukung 4 tipe promosi utama dengan fleksibilitas tinggi untuk berbagai skenario bisnis.

---

## Table of Contents
1. [Promotion Types](#promotion-types)
2. [Database Schema](#database-schema)
3. [Field Definitions](#field-definitions)
4. [API Endpoints](#api-endpoints)
5. [Implementation Guide](#implementation-guide)
6. [Use Cases & Examples](#use-cases--examples)
7. [Best Practices](#best-practices)

---

## Promotion Types

### 1. Percentage Discount (%)
**Konsep**: Diskon persentase dari harga produk yang dipilih.

**Cara Kerja**:
- Customer membeli produk yang terdaftar dalam promosi
- Sistem memberikan diskon X% dari harga produk
- Diskon dihitung: `harga_produk × (discount_value / 100)`

**Form Fields**:
- `promo_type`: `percentage`
- `discount_value`: Nilai persentase (contoh: `20` untuk 20%)
- `min_purchase_amount`: Minimum pembelian untuk aktivasi (opsional)
- `min_quantity`: Minimum jumlah item (default: 1)
- `products`: Produk-produk yang mendapat diskon

**Use Cases**:
```
✅ Diskon 15% untuk semua Pizza
✅ Diskon 20% untuk produk tertentu jika belanja min Rp 50.000
✅ Diskon 10% untuk kategori Dessert
✅ Flash Sale 50% untuk produk pilihan
```

**Example**:
```json
{
  "name": "Diskon 20% All Pizza",
  "promo_type": "percentage",
  "discount_value": 20,
  "min_purchase_amount": 0,
  "min_quantity": 1,
  "product_ids": [1, 2, 3],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Calculation Example**:
- Produk: Pepperoni Pizza (Rp 95.000)
- Discount: 20%
- **Final Price**: Rp 95.000 - (Rp 95.000 × 20%) = **Rp 76.000**

---

### 2. Fixed Amount (Rp)
**Konsep**: Diskon nominal tetap dalam Rupiah untuk produk tertentu.

**Cara Kerja**:
- Customer membeli produk yang terdaftar dalam promosi
- Sistem mengurangi harga dengan nominal tetap
- Diskon dihitung: `harga_produk - discount_value`

**Form Fields**:
- `promo_type`: `fixed_amount`
- `discount_value`: Nilai diskon dalam Rupiah (contoh: `15000` untuk Rp 15.000)
- `min_purchase_amount`: Minimum pembelian untuk aktivasi (opsional)
- `min_quantity`: Minimum jumlah item (default: 1)
- `products`: Produk-produk yang mendapat diskon

**Use Cases**:
```
✅ Potongan Rp 10.000 untuk Burger
✅ Cashback Rp 5.000 untuk pembelian min Rp 50.000
✅ Diskon Rp 20.000 untuk produk tertentu
✅ Promo payday: potongan Rp 25.000
```

**Example**:
```json
{
  "name": "Potongan Rp 15.000 Cheese Burger",
  "promo_type": "fixed_amount",
  "discount_value": 15000,
  "min_purchase_amount": 0,
  "min_quantity": 1,
  "product_ids": [5],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Calculation Example**:
- Produk: Cheese Burger (Rp 55.000)
- Discount: Rp 15.000
- **Final Price**: Rp 55.000 - Rp 15.000 = **Rp 40.000**

---

### 3. Buy X Get Y (+)
**Konsep**: Beli produk X dengan quantity tertentu, dapat produk Y gratis atau diskon.

**Cara Kerja**:
- Customer harus membeli produk "Buy (X)" minimal sejumlah `min_quantity`
- Sistem memberikan diskon untuk produk "Get (Y)"
- Diskon bisa 100% (gratis) atau persentase/nominal tertentu
- Menggunakan **product_role** untuk membedakan X dan Y

**Product Roles**:
- `buy`: Produk yang harus dibeli (syarat)
- `get`: Produk yang akan didapat (reward)
- `both`: Produk bisa sebagai syarat atau reward (contoh: Buy 1 Get 1)

**Form Fields**:
- `promo_type`: `buy_x_get_y`
- `discount_value`: Diskon untuk produk Y (contoh: `100` untuk gratis)
- `discount_type`: `percentage` atau `fixed_amount`
- `min_quantity`: Jumlah minimum produk X yang harus dibeli
- `products_with_roles`: Array of `{id: number, role: 'buy'|'get'|'both'}`

**Use Cases**:
```
✅ Buy 2 Pepperoni Pizza Get 1 Cheese Burger Free
✅ Buy 1 Main Course Get 1 Drink Free
✅ Buy 3 Get 1 (produk sama)
✅ Buy 2 Large Pizza Get 1 Small Pizza 50% Off
```

**Example 1: Buy 2 Get 1 Free (Different Product)**:
```json
{
  "name": "Buy 2 Pepperoni Pizza Get Cheese Burger Free",
  "promo_type": "buy_x_get_y",
  "discount_value": 100,
  "discount_type": "percentage",
  "min_quantity": 2,
  "products_with_roles": [
    {"id": 1, "role": "buy"},   // Pepperoni Pizza (harus beli 2)
    {"id": 5, "role": "get"}    // Cheese Burger (gratis)
  ],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Example 2: Buy 1 Get 1 (Same Product)**:
```json
{
  "name": "Buy 1 Get 1 Free - Iced Tea",
  "promo_type": "buy_x_get_y",
  "discount_value": 100,
  "discount_type": "percentage",
  "min_quantity": 1,
  "products_with_roles": [
    {"id": 10, "role": "both"}  // Iced Tea bisa buy atau get
  ],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Calculation Example**:
- Buy: 2× Pepperoni Pizza @ Rp 95.000 = Rp 190.000
- Get: 1× Cheese Burger @ Rp 55.000 (100% off) = Rp 0
- **Total**: Rp 190.000 (hemat Rp 55.000)

---

### 4. Bundle Deal (📦)
**Konsep**: Paket beberapa produk dengan harga khusus. Customer harus beli SEMUA produk dalam bundle.

**Cara Kerja**:
- Customer harus membeli SEMUA produk yang terdaftar dalam bundle
- Sistem memberikan diskon dari total harga produk
- Semua produk menggunakan role `both` (setara, wajib semua)
- Bundle tidak terpenuhi jika ada produk yang tidak dibeli

**Form Fields**:
- `promo_type`: `bundle_deal`
- `discount_value`: Diskon dari total (bisa percentage atau fixed)
- `discount_type`: `percentage` atau `fixed_amount`
- `min_quantity`: Biasanya 1 (untuk 1 paket lengkap)
- `product_ids` atau `products_with_roles`: Semua produk dalam bundle

**Use Cases**:
```
✅ Paket Lunch: 1 Pizza + 1 Drink + 1 Dessert = Rp 100.000
✅ Paket Keluarga: 2 Pizza + 4 Drinks = Hemat Rp 50.000
✅ Combo Meal: Burger + Fries + Cola = Diskon 20%
✅ Breakfast Bundle: Coffee + Sandwich + Fruit = Rp 35.000
```

**Example**:
```json
{
  "name": "Paket Hemat Burger + Drink",
  "promo_type": "bundle_deal",
  "discount_value": 15000,
  "discount_type": "fixed_amount",
  "min_quantity": 1,
  "product_ids": [5, 6, 10],  // Cheese Burger, Classic Burger, Iced Tea
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Calculation Example**:
- Cheese Burger: Rp 55.000
- Classic Burger: Rp 45.000
- Iced Tea: Rp 12.000
- **Total Normal**: Rp 112.000
- **Diskon**: Rp 15.000
- **Bundle Price**: **Rp 97.000** (hemat 13.4%)

---

## Database Schema

### Promotion Model
```python
class Promotion(TenantModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    promo_type = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Percentage Discount'),
            ('fixed_amount', 'Fixed Amount'),
            ('buy_x_get_y', 'Buy X Get Y'),
            ('bundle_deal', 'Bundle Deal'),
        ]
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Percentage'),
            ('fixed_amount', 'Fixed Amount'),
        ],
        default='percentage'
    )
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    min_quantity = models.IntegerField(default=1)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### PromotionProduct Model
```python
class PromotionProduct(models.Model):
    ROLE_BUY = 'buy'
    ROLE_GET = 'get'
    ROLE_BOTH = 'both'
    
    ROLE_CHOICES = [
        (ROLE_BUY, 'Buy Product (X)'),
        (ROLE_GET, 'Get Product (Y)'),
        (ROLE_BOTH, 'Both Buy and Get'),
    ]
    
    promotion = models.ForeignKey(
        'Promotion',
        on_delete=models.CASCADE,
        related_name='products'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )
    product_role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_BOTH,
        help_text="Role of this product in Buy X Get Y promotions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('promotion', 'product')
```

---

## Field Definitions

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | ✅ | Nama promosi (contoh: "Flash Sale 50%") |
| `description` | Text | ❌ | Deskripsi detail promosi |
| `promo_type` | Choice | ✅ | Tipe promosi: `percentage`, `fixed_amount`, `buy_x_get_y`, `bundle_deal` |
| `discount_value` | Decimal | ✅ | Nilai diskon (persentase atau nominal) |
| `discount_type` | Choice | ❌ | Tipe diskon untuk promo tertentu: `percentage` atau `fixed_amount` |
| `start_date` | DateTime | ✅ | Tanggal mulai promosi |
| `end_date` | DateTime | ✅ | Tanggal selesai promosi |
| `is_active` | Boolean | ✅ | Status aktif/nonaktif |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `min_purchase_amount` | Decimal | 0 | Minimum pembelian untuk aktivasi promosi |
| `min_quantity` | Integer | 1 | Minimum jumlah produk untuk Buy X Get Y |
| `max_uses` | Integer | null | Maksimum penggunaan promosi |
| `max_uses_per_customer` | Integer | null | Maksimum penggunaan per customer |

### Product Association

| Field | Type | Description |
|-------|------|-------------|
| `product_ids` | Array[Int] | Array ID produk (backward compatible) |
| `products_with_roles` | Array[Object] | Array of `{id: number, role: string}` untuk Buy X Get Y |

---

## API Endpoints

### 1. List All Promotions
```http
GET /api/promotions/
```

**Query Parameters**:
- `tenant_id`: Filter by tenant
- `is_active`: Filter by active status
- `promo_type`: Filter by type

**Response**:
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Flash Sale 50%",
      "promo_type": "percentage",
      "discount_value": "50.00",
      "products": [...],
      "is_valid_now": true
    }
  ]
}
```

### 2. Create Promotion
```http
POST /api/promotions/
```

**Request Body (Old Format - Backward Compatible)**:
```json
{
  "name": "Diskon 20% Pizza",
  "promo_type": "percentage",
  "discount_value": 20,
  "product_ids": [1, 2, 3],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true,
  "tenant_id": 67
}
```

**Request Body (New Format - With Roles)**:
```json
{
  "name": "Buy 2 Get 1 Free",
  "promo_type": "buy_x_get_y",
  "discount_value": 100,
  "min_quantity": 2,
  "products_with_roles": [
    {"id": 1, "role": "buy"},
    {"id": 5, "role": "get"}
  ],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true,
  "tenant_id": 67
}
```

### 3. Update Promotion
```http
PATCH /api/promotions/{id}/
```

**Request Body**: Same as create

### 4. Delete Promotion
```http
DELETE /api/promotions/{id}/
```

### 5. Get Products for Selector
```http
GET /api/promotions/products-for-selector/?tenant_id={id}
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "Pepperoni Pizza",
    "price": "95000.00",
    "image": "/media/products/pizza.jpg"
  }
]
```

---

## Implementation Guide

### Frontend: Creating Promotion

**Step 1: Select Promotion Type**
```svelte
<select bind:value={formData.promo_type}>
  <option value="percentage">% Percentage Discount</option>
  <option value="fixed_amount">Rp Fixed Amount</option>
  <option value="buy_x_get_y">+ Buy X Get Y</option>
  <option value="bundle_deal">📦 Bundle Deal</option>
</select>
```

**Step 2: Handle Product Selection**
```svelte
<ProductSelector
  bind:selected={selectedProducts}
  {tenantId}
  promoType={formData.promo_type}
  on:change={handleProductChange}
/>
```

**Step 3: Submit with Roles (for Buy X Get Y)**
```javascript
const productsWithRoles = selectedProducts.map(p => ({
  id: p.id,
  role: p.role || 'both'
}));

const submitData = {
  ...formData,
  products_with_roles: productsWithRoles
};

await createPromotion(submitData);
```

### Backend: Handling Promotion

**Serializer**:
```python
class PromotionSerializer(serializers.ModelSerializer):
    products_with_roles = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    def create(self, validated_data):
        products_with_roles = validated_data.pop('products_with_roles', None)
        promotion = Promotion.objects.create(**validated_data)
        
        if products_with_roles:
            for item in products_with_roles:
                product = Product.all_objects.get(id=item['id'])
                PromotionProduct.objects.create(
                    promotion=promotion,
                    product=product,
                    product_role=item.get('role', 'both')
                )
        
        return promotion
```

---

## Use Cases & Examples

### Case 1: Weekend Flash Sale
**Objective**: Diskon 30% untuk semua Pizza di akhir pekan

```json
{
  "name": "Weekend Flash Sale - All Pizza 30% OFF",
  "promo_type": "percentage",
  "discount_value": 30,
  "product_ids": [1, 2, 3, 4],
  "start_date": "2026-01-04T00:00:00Z",
  "end_date": "2026-01-05T23:59:59Z",
  "is_active": true
}
```

**Result**:
- Pepperoni Pizza: ~~Rp 95.000~~ → **Rp 66.500**
- Margherita Pizza: ~~Rp 85.000~~ → **Rp 59.500**

---

### Case 2: Payday Cashback
**Objective**: Potongan Rp 25.000 untuk pembelian minimal Rp 100.000

```json
{
  "name": "Payday Cashback - Rp 25K",
  "promo_type": "fixed_amount",
  "discount_value": 25000,
  "min_purchase_amount": 100000,
  "product_ids": [],  // All products
  "start_date": "2026-01-25T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Result**:
- Belanja Rp 150.000 → Bayar **Rp 125.000**
- Belanja Rp 80.000 → Tidak dapat diskon (belum mencapai min)

---

### Case 3: Buy 2 Get 1 Same Product
**Objective**: Beli 2 Iced Tea dapat 1 Iced Tea gratis

```json
{
  "name": "Buy 2 Get 1 Free - Iced Tea",
  "promo_type": "buy_x_get_y",
  "discount_value": 100,
  "discount_type": "percentage",
  "min_quantity": 2,
  "products_with_roles": [
    {"id": 10, "role": "both"}
  ],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Result**:
- 3× Iced Tea @ Rp 12.000
- Bayar: 2× Rp 12.000 = **Rp 24.000** (1 gratis)

---

### Case 4: Cross-Product Buy X Get Y
**Objective**: Beli 2 Pizza dapat 1 Cheese Burger gratis

```json
{
  "name": "Buy 2 Pizza Get Cheese Burger Free",
  "promo_type": "buy_x_get_y",
  "discount_value": 100,
  "discount_type": "percentage",
  "min_quantity": 2,
  "products_with_roles": [
    {"id": 1, "role": "buy"},   // Pepperoni Pizza
    {"id": 2, "role": "buy"},   // Margherita Pizza
    {"id": 5, "role": "get"}    // Cheese Burger
  ],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Result**:
- 2× Pizza @ Rp 95.000 = Rp 190.000
- 1× Cheese Burger (gratis)
- **Total**: Rp 190.000 (hemat Rp 55.000)

---

### Case 5: Family Bundle
**Objective**: Paket Keluarga dengan harga spesial

```json
{
  "name": "Paket Keluarga - 2 Pizza + 4 Drinks",
  "promo_type": "bundle_deal",
  "discount_value": 50000,
  "discount_type": "fixed_amount",
  "min_quantity": 1,
  "product_ids": [1, 2, 10, 11],
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Bundle Contents**:
- 2× Pizza @ Rp 95.000 = Rp 190.000
- 4× Drink @ Rp 12.000 = Rp 48.000
- **Total Normal**: Rp 238.000
- **Diskon**: Rp 50.000
- **Bundle Price**: **Rp 188.000**

---

### Case 6: Combo Percentage Bundle
**Objective**: Bundle dengan diskon persentase

```json
{
  "name": "Lunch Combo - Save 25%",
  "promo_type": "bundle_deal",
  "discount_value": 25,
  "discount_type": "percentage",
  "min_quantity": 1,
  "product_ids": [5, 10, 15],  // Burger + Drink + Fries
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "is_active": true
}
```

**Result**:
- Burger (Rp 55.000) + Drink (Rp 12.000) + Fries (Rp 18.000)
- **Total Normal**: Rp 85.000
- **Diskon 25%**: Rp 21.250
- **Bundle Price**: **Rp 63.750**

---

## Best Practices

### 1. Naming Convention
✅ **Good**:
- "Flash Sale 50% - All Pizza"
- "Buy 2 Get 1 Free - Iced Tea"
- "Paket Hemat Burger + Drink"

❌ **Bad**:
- "Promo 1"
- "Special"
- "Discount"

### 2. Date Range
- Selalu set `end_date` dengan waktu `23:59:59` untuk mencakup seluruh hari terakhir
- Gunakan `is_active` untuk mengontrol promosi tanpa mengubah tanggal
- Test promosi dengan range tanggal pendek terlebih dahulu

### 3. Discount Value
- **Percentage**: Gunakan nilai 1-100
- **Fixed Amount**: Gunakan nominal dalam Rupiah (tanpa desimal jika tidak perlu)
- Pastikan diskon tidak melebihi harga produk (untuk fixed_amount)

### 4. Product Selection
- Untuk Bundle Deal: Pilih produk yang sering dibeli bersamaan
- Untuk Buy X Get Y: Pastikan produk X (buy) dan Y (get) jelas berbeda kecuali sama produk
- Gunakan role `both` untuk Buy X Get X (same product)

### 5. Minimum Values
- `min_purchase_amount`: Gunakan untuk promosi cashback atau minimum belanja
- `min_quantity`: Khusus untuk Buy X Get Y
- Set ke 0 atau 1 jika tidak ada minimum

### 6. Testing
- Test setiap promosi sebelum di-aktifkan
- Verify kalkulasi diskon benar
- Check apakah promosi muncul di kasir
- Test edge cases (multiple promotions, expired dates, etc.)

### 7. Product Roles (Buy X Get Y)
- `buy`: Untuk produk yang harus dibeli (syarat)
- `get`: Untuk produk yang didapat (reward)
- `both`: Untuk produk yang bisa sebagai syarat atau reward (Buy 1 Get 1 same product)

### 8. Multi-Tenant Consideration
- Setiap promosi harus terikat dengan tenant
- Gunakan `Product.all_objects` di serializer untuk akses cross-tenant
- Pastikan `tenant_id` selalu disertakan saat create/update

---

## Validation Rules

### Backend Validation
```python
# In Promotion model
def clean(self):
    # Validate date range
    if self.start_date >= self.end_date:
        raise ValidationError("End date must be after start date")
    
    # Validate discount value
    if self.discount_type == 'percentage' and self.discount_value > 100:
        raise ValidationError("Percentage discount cannot exceed 100%")
    
    # Validate min_quantity for Buy X Get Y
    if self.promo_type == 'buy_x_get_y' and self.min_quantity < 1:
        raise ValidationError("Minimum quantity must be at least 1")
```

### Frontend Validation
```javascript
// Validate before submit
function validatePromotion(formData) {
  const errors = [];
  
  if (!formData.name) errors.push("Name is required");
  if (!formData.promo_type) errors.push("Promo type is required");
  if (formData.discount_value <= 0) errors.push("Discount value must be positive");
  if (selectedProducts.length === 0) errors.push("Select at least one product");
  
  if (formData.promo_type === 'buy_x_get_y') {
    const hasBuy = selectedProducts.some(p => p.role === 'buy' || p.role === 'both');
    const hasGet = selectedProducts.some(p => p.role === 'get' || p.role === 'both');
    if (!hasBuy || !hasGet) errors.push("Buy X Get Y requires both buy and get products");
  }
  
  return errors;
}
```

---

## Troubleshooting

### Issue 1: Products Not Showing in Edit Page
**Cause**: Tenant filtering blocking cross-tenant access

**Solution**: Use `Product.all_objects` instead of `Product.objects`:
```python
# In serializer
product = Product.all_objects.get(id=product_id)
```

### Issue 2: Products Showing as "undefined NaN"
**Cause**: Product data not properly loaded in serializer

**Solution**: Add exception handling:
```python
def get_product_name(self, obj):
    try:
        if obj.product_id:
            product = Product.all_objects.filter(id=obj.product_id).first()
            return product.name if product else f'Product {obj.product_id}'
    except Exception:
        return f'Product {obj.product_id}'
```

### Issue 3: Role Selector Not Showing
**Cause**: PromoType not passed to ProductSelector

**Solution**: Pass promoType prop:
```svelte
<ProductSelector
  bind:selected={selectedProducts}
  promoType={formData.promo_type}
/>
```

### Issue 4: Promotion Not Applied in Cashier
**Possible Causes**:
1. Promotion expired or not active
2. Product not in promotion list
3. Minimum requirements not met
4. Tenant mismatch

**Debug Steps**:
1. Check `is_active` and `is_valid_now` fields
2. Verify product IDs in promotion
3. Check min_purchase_amount and min_quantity
4. Verify tenant_id matches

---

## Future Enhancements

### Planned Features
- [ ] Promo code system (PROMO2026)
- [ ] Customer-specific promotions
- [ ] Tiered discounts (buy more, save more)
- [ ] Stackable promotions
- [ ] Promotion analytics dashboard
- [ ] Auto-deactivate expired promotions
- [ ] Promotion scheduling (queue system)
- [ ] A/B testing for promotions

### API Improvements
- [ ] Bulk create promotions
- [ ] Clone promotion
- [ ] Promotion templates
- [ ] Export/Import promotions
- [ ] Promotion preview/simulation

---

## Version History

### v1.0 (Current)
- Basic promotion types (percentage, fixed_amount)
- Product association
- Date range validation
- Tenant isolation

### v2.0 (Released)
- Buy X Get Y feature
- Product roles (buy, get, both)
- Bundle Deal support
- products_with_roles API
- Backward compatibility

---

## Support & Contact

For questions or issues:
- Check GitHub Issues
- Review this documentation
- Contact development team

---

**Last Updated**: January 4, 2026
**Version**: 2.0
**Maintainer**: POS Kiosk Development Team
