# 🏪 FOOD COURT KIOSK - MULTI-TENANT CONCEPT

## 🎯 Use Case: Food Court

### Current (WRONG for Food Court):
```
User → Select Tenant → Select Outlet → Browse Menu → Order
```
❌ User harus pilih 1 tenant dulu
❌ Tidak bisa mix menu dari tenant berbeda
❌ Harus restart untuk ganti tenant

### New (CORRECT for Food Court):
```
User → Browse ALL Menus → Filter by Tenant/Category → Add to Cart (mixed) → Checkout
      → System splits order by tenant → Send to respective kitchens/printers
```
✅ User bisa lihat semua menu sekaligus
✅ Bisa mix order dari berbagai tenant
✅ Tenant jadi **filter tab** seperti category
✅ Order otomatis di-split per tenant

---

## 🎨 New UI Flow

### Main Screen Layout
```
┌─────────────────────────────────────────────────────────┐
│  🍽️ Food Court Kiosk              🛒 Cart (5)          │
├─────────────────────────────────────────────────────────┤
│  FILTER BY TENANT/BRAND:                                │
│  [All] [Nasi Goreng Abang] [Pizza Hut] [KFC] [Starbucks]│
├─────────────────────────────────────────────────────────┤
│  FILTER BY CATEGORY:                                     │
│  [All] [Main Course] [Snacks] [Drinks] [Desserts]       │
├─────────────────────────────────────────────────────────┤
│  PRODUCTS:                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │🍔 Burger │ │🍕 Pizza  │ │☕ Coffee │                │
│  │Pizza Hut │ │Pizza Hut │ │Starbucks│                │
│  │Rp 45,000│ │Rp 65,000│ │Rp 35,000│                │
│  └──────────┘ └──────────┘ └──────────┘                │
└─────────────────────────────────────────────────────────┘
```

### Cart with Tenant Grouping
```
┌─────────────────────────────┐
│  Your Order                 │
├─────────────────────────────┤
│  🏪 Pizza Hut               │
│  • Burger x1    Rp 45,000   │
│  • Pizza x2     Rp 130,000  │
│                              │
│  🏪 Starbucks               │
│  • Coffee x1    Rp 35,000   │
│                              │
│  🏪 Nasi Goreng Abang       │
│  • Nasi Goreng  Rp 25,000   │
├─────────────────────────────┤
│  Subtotal:    Rp 235,000    │
│  Tax (10%):   Rp  23,500    │
│  Service (5%): Rp  11,750   │
│  TOTAL:       Rp 270,250    │
├─────────────────────────────┤
│  [Checkout]                 │
└─────────────────────────────┘
```

---

## 🔧 Backend Changes Needed

### 1. Product API - Remove Tenant Filtering
```python
# backend/apps/products/views.py

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        # Show ALL products from ALL tenants for food court
        queryset = Product.all_objects.filter(is_available=True)
        
        # Optional: Filter by tenant if requested
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # Optional: Filter by category
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset.select_related('category', 'tenant').prefetch_related('modifiers')
```

### 2. Product Serializer - Add Tenant Info
```python
# backend/apps/products/serializers.py

class ProductSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    tenant_id = serializers.IntegerField(source='tenant.id', read_only=True)
    tenant_color = serializers.CharField(source='tenant.primary_color', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'image_url',
            'price', 'category', 'category_name',
            'tenant_id', 'tenant_name', 'tenant_color',  # ✅ Add tenant info
            'is_available', 'is_featured'
        ]
```

### 3. Order API - Split Order by Tenant
```python
# backend/apps/orders/views.py

class OrderViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        """
        Create order and split by tenant
        """
        items = request.data.get('items', [])
        
        # Group items by tenant
        tenant_orders = {}
        for item in items:
            product = Product.objects.get(id=item['product_id'])
            tenant_id = product.tenant_id
            
            if tenant_id not in tenant_orders:
                tenant_orders[tenant_id] = {
                    'tenant': product.tenant,
                    'items': []
                }
            
            tenant_orders[tenant_id]['items'].append({
                'product': product,
                'quantity': item['quantity'],
                'modifiers': item.get('modifiers', [])
            })
        
        # Create separate order for each tenant
        created_orders = []
        for tenant_id, order_data in tenant_orders.items():
            order = Order.objects.create(
                tenant=order_data['tenant'],
                # ... other fields
            )
            
            # Create order items
            for item_data in order_data['items']:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    # ...
                )
            
            # Send to kitchen display for this tenant
            send_to_kitchen(order)
            
            created_orders.append(order)
        
        return Response({
            'orders': [OrderSerializer(o).data for o in created_orders]
        })
```

---

## 🎨 Frontend Changes Needed

### 1. Load ALL Products (No Tenant Selection)
```javascript
// frontend/src/routes/kiosk/+page.svelte

let products = [];
let tenants = [];
let categories = [];
let selectedTenant = null;  // For filtering, not selection
let selectedCategory = null;

// Filtered products by tenant AND category
$: filteredProducts = products.filter(p => {
    if (selectedTenant && p.tenant_id !== selectedTenant) return false;
    if (selectedCategory && p.category !== selectedCategory) return false;
    return true;
});

async function loadKioskData() {
    // Load ALL products (no tenant filter)
    const productsRes = await fetch(`${apiUrl}/products/products/`);
    products = await productsRes.json();
    
    // Load all tenants for filter tabs
    const tenantsRes = await fetch(`${apiUrl}/public/tenants/`);
    tenants = await tenantsRes.json();
    
    // Load categories
    const categoriesRes = await fetch(`${apiUrl}/products/categories/`);
    categories = await categoriesRes.json();
}
```

### 2. Tenant Filter Tabs
```svelte
<!-- Tenant Filter Tabs -->
<div class="filter-section">
    <h3>Filter by Restaurant:</h3>
    <div class="filter-tabs">
        <button 
            class:active={selectedTenant === null}
            on:click={() => selectedTenant = null}
        >
            All Restaurants
        </button>
        {#each tenants as tenant}
            <button 
                class:active={selectedTenant === tenant.id}
                on:click={() => selectedTenant = tenant.id}
                style="border-color: {tenant.primary_color}"
            >
                {tenant.name}
            </button>
        {/each}
    </div>
</div>
```

### 3. Product Card with Tenant Badge
```svelte
<!-- Product Card -->
<div class="product-card">
    <!-- Tenant Badge -->
    <div class="tenant-badge" style="background: {product.tenant_color}">
        {product.tenant_name}
    </div>
    
    <img src={product.image_url} alt={product.name} />
    
    <h3>{product.name}</h3>
    <p class="price">{formatPrice(product.price)}</p>
    
    <button on:click={() => addToCart(product)}>
        Add to Cart
    </button>
</div>
```

### 4. Cart Grouped by Tenant
```svelte
<!-- Cart with Tenant Grouping -->
<div class="cart">
    {#each groupedCartItems as tenantGroup}
        <div class="tenant-group">
            <h4 class="tenant-header" style="color: {tenantGroup.color}">
                🏪 {tenantGroup.tenant_name}
            </h4>
            
            {#each tenantGroup.items as item}
                <div class="cart-item">
                    <span>{item.product_name} x{item.quantity}</span>
                    <span>{formatPrice(item.total)}</span>
                </div>
            {/each}
        </div>
    {/each}
    
    <!-- Totals -->
    <div class="cart-totals">
        <div>Subtotal: {formatPrice(subtotal)}</div>
        <div>Tax: {formatPrice(tax)}</div>
        <div>Total: {formatPrice(total)}</div>
    </div>
    
    <button on:click={checkout}>Checkout</button>
</div>

<script>
// Group cart items by tenant
$: groupedCartItems = Object.values(
    $cartItems.reduce((groups, item) => {
        const tenantId = item.tenant_id;
        if (!groups[tenantId]) {
            groups[tenantId] = {
                tenant_id: tenantId,
                tenant_name: item.tenant_name,
                color: item.tenant_color,
                items: []
            };
        }
        groups[tenantId].items.push(item);
        return groups;
    }, {})
);
</script>
```

---

## 📊 Data Flow

### 1. Load Products
```
Frontend → GET /api/products/products/ (no tenant filter)
        ← All products with tenant info
```

### 2. Filter Products
```
User clicks "Pizza Hut" tab
→ Frontend filters: products.filter(p => p.tenant_id === 2)
```

### 3. Add to Cart
```
User adds Pizza + Burger (Pizza Hut) + Coffee (Starbucks)
→ Cart stores items with tenant_id
```

### 4. Checkout - Split Order
```
Frontend → POST /api/orders/
{
    "items": [
        {"product_id": 1, "tenant_id": 2, "quantity": 1},  // Pizza (Pizza Hut)
        {"product_id": 2, "tenant_id": 2, "quantity": 1},  // Burger (Pizza Hut)
        {"product_id": 5, "tenant_id": 3, "quantity": 1}   // Coffee (Starbucks)
    ]
}

Backend:
→ Group by tenant_id
→ Create Order #1 for Pizza Hut (Pizza + Burger)
→ Create Order #2 for Starbucks (Coffee)
→ Send Order #1 to Pizza Hut kitchen display/printer
→ Send Order #2 to Starbucks kitchen display/printer

Response:
← {
    "orders": [
        {"id": 1, "tenant": "Pizza Hut", "total": 110000, "order_number": "FH001"},
        {"id": 2, "tenant": "Starbucks", "total": 35000, "order_number": "SB001"}
    ],
    "grand_total": 145000
}
```

---

## 🎯 Benefits

### For Users (Food Court Customers):
✅ Browse all menus at once
✅ Mix and match from different tenants
✅ Easy filtering by restaurant or category
✅ One checkout for multiple restaurants

### For Tenants (Restaurant Owners):
✅ Only see their own orders
✅ Own kitchen display
✅ Own printer
✅ Separate order numbers
✅ Own analytics

### For Food Court Operator:
✅ One kiosk for all tenants
✅ Centralized payment
✅ Easy tenant management
✅ Global analytics + per-tenant breakdown

---

## 🚀 Implementation Plan

### Step 1: Update Backend (30 mins)
- [ ] Remove tenant filter from Product API
- [ ] Add tenant info to Product serializer
- [ ] Update Order creation to split by tenant
- [ ] Add kitchen display routing by tenant

### Step 2: Update Frontend (45 mins)
- [ ] Remove tenant selector flow
- [ ] Add tenant filter tabs
- [ ] Add tenant badge on products
- [ ] Group cart by tenant
- [ ] Update checkout flow

### Step 3: Kitchen Display (1 hour)
- [ ] Create kitchen display screen per tenant
- [ ] WebSocket for real-time orders
- [ ] Printer integration per tenant

### Step 4: Testing (30 mins)
- [ ] Test mixed cart
- [ ] Test order splitting
- [ ] Test kitchen routing
- [ ] Test printer routing

---

## 🎨 UI Mockup

```
┌────────────────────────────────────────────────────────────────┐
│  🍽️ Food Court Kiosk                        🛒 Cart (3) Total │
├────────────────────────────────────────────────────────────────┤
│  RESTAURANTS:                                                   │
│  [All] [🍔 Burger King] [🍕 Pizza Hut] [☕ Starbucks] [🍜 Ramen]│
├────────────────────────────────────────────────────────────────┤
│  CATEGORIES:                                                     │
│  [All] [Main] [Snacks] [Drinks] [Desserts]                    │
├────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ 🍔 Whopper  │ │ 🍕 Pepperoni│ │ ☕ Latte    │              │
│  │ Burger King │ │ Pizza Hut   │ │ Starbucks   │              │
│  │ Rp 45,000   │ │ Rp 85,000   │ │ Rp 35,000   │              │
│  │ [+Add]      │ │ [+Add]      │ │ [+Add]      │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└────────────────────────────────────────────────────────────────┘
```

---

## 📝 Next Steps

Mau saya implement yang mana dulu?

1. **Backend**: Update Product API + Order split
2. **Frontend**: Remove tenant selector, add filter tabs
3. **Full Implementation**: Both backend + frontend

**Recommend**: Start with **Option 3 (Full)** - ~2 hours total

Silakan confirm, saya langsung implement! 🚀
