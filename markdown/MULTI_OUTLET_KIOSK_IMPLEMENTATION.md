# 🏪 Multi-Store Multi-Outlet Kiosk System - Implementation Guide (OPSI 2)

## 📋 Overview

Sistem kiosk multi-store untuk retail chain dengan multiple brands:
✅ **Store-based configuration** (Physical retail location)
✅ **Multi-outlet shopping cart** (order dari beberapa brand dalam 1 transaksi)
✅ QR code setup per store
✅ Combined payment
✅ Order distribution per outlet/brand
✅ Kitchen display routing per brand

**Architecture:** Tenant (Company) → Store (Physical Location) → Outlet (Brand at Store)

---

## 🔄 Recent Updates (January 8, 2026)

### ✅ Phase 3.1: Kitchen Backend APIs - COMPLETE
**Status:** All Kitchen Display System backend APIs implemented and tested

**New API Endpoints:**
1. **Order Listing APIs**
   - `GET /api/kitchen/orders/` - List all kitchen orders with filters
   - `GET /api/kitchen/orders/pending/` - New orders waiting to be prepared
   - `GET /api/kitchen/orders/preparing/` - Orders currently in progress
   - `GET /api/kitchen/orders/ready/` - Orders completed and ready for pickup
   
2. **Order Status Management**
   - `POST /api/kitchen/orders/{id}/start/` - Start preparing (pending → preparing)
   - `POST /api/kitchen/orders/{id}/complete/` - Mark as ready (preparing → ready)
   - `POST /api/kitchen/orders/{id}/serve/` - Mark as served (ready → served)
   - `POST /api/kitchen/orders/{id}/cancel/` - Cancel order with notes
   
3. **Statistics & Analytics**
   - `GET /api/kitchen/orders/stats/` - Real-time kitchen statistics
     - Pending count, preparing count, ready count
     - Completed orders today
     - Average preparation time
     - Total orders today

**Features Implemented:**
- **Multi-tenant Filtering**: Query by outlet (brand), store, or status
- **Wait Time Tracking**: Auto-calculate order wait time in minutes
- **Urgent Order Detection**: Flag orders waiting >15 minutes as urgent
- **Today Filter**: Default to today's orders only (configurable)
- **Order Workflow**: Proper status transitions with validation
- **Detailed Order Info**: Includes items, modifiers, customer info, totals

**Serializers Created:**
- `KitchenOrderSerializer` - Full order data with calculated fields
- `KitchenOrderItemSerializer` - Product details with modifiers display
- `KitchenStatsSerializer` - Dashboard statistics
- `KitchenOrderStatusUpdateSerializer` - Status change validation

**Middleware Update:**
- Added `/api/kitchen/` to tenant middleware exclusion list
- Kitchen APIs bypass X-Tenant-ID requirement (filters applied via query params)

**Testing Results:**
```bash
# Statistics
GET /api/kitchen/orders/stats/?outlet=519
Response: {pending: 0, preparing: 0, ready: 1, completed_today: 0, avg_prep_time: 0.0}

# Pending Orders
GET /api/kitchen/orders/pending/?outlet=519
Response: [Order ORD-20260108-8646 with wait_time: 7 min, is_urgent: false]

# Start Preparing
POST /api/kitchen/orders/595/start/
Response: {message: "Order started", order: {status: "preparing"}}

# Mark Ready
POST /api/kitchen/orders/595/complete/
Response: {message: "Order marked as ready", completed_at: "2026-01-08T20:41:30"}

# Ready Orders
GET /api/kitchen/orders/ready/?outlet=519
Response: [Order ORD-20260108-8646, status: "ready"]
```

**Files Created:**
- `backend/apps/orders/serializers_kitchen.py` (138 lines)
- `backend/apps/orders/views_kitchen.py` (250 lines)

**Files Modified:**
- `backend/apps/orders/urls.py` - Added kitchen router
- `backend/apps/tenants/middleware.py` - Excluded kitchen endpoints

**Next Steps:**
- Socket.IO integration for real-time updates (commented placeholders ready)
- Kitchen Display frontend (Phase 3.2)
- Customer notification on order ready

---

### ✅ Phase 2.3: Kiosk UX Enhancements - COMPLETE (Earlier Today)
**Status:** All navigation, session management, and accessibility features implemented

**New Components Created:**
1. **Idle/Welcome Screen** (`/kiosk/idle/+page.svelte`)
   - Attractive gradient background with animations
   - Store name and tenant display from kioskConfig
   - Promotional carousel with 4 slides (auto-rotate every 4 seconds)
   - "Tap to Start" CTA with full-screen tap overlay
   - Features showcase (Multiple Brands, One Cart, Single Payment)
   - Responsive design (mobile, tablet, desktop)
   - Smooth animations (fadeIn, wave, pulse, blink)

2. **Navigation Store** (`lib/stores/navigationStore.ts`)
   - Path tracking and breadcrumb generation
   - Cart item count management
   - Back navigation with cart confirmation
   - **Session Management:**
     - 15-minute session timeout (auto-clear and redirect to idle)
     - 2-minute idle timeout (redirect to idle if inactive)
     - Activity detection (mouse, keyboard, touch, scroll)
     - Clear session event dispatcher
   - Breadcrumb label mapping (products → "Browse Products", etc.)

3. **Kiosk Header Component** (`lib/components/kiosk/KioskHeader.svelte`)
   - **Back Button:** Shows when canGoBack, with confirmation if cart has items
   - **Breadcrumb Navigation:** Auto-generated from current path, clickable
   - **Store Info:** Centered display of tenant + store name
   - **Cart Badge:** Floating button with item count, fixed bottom-right on mobile
   - **Responsive:** Grid layout for desktop, stacked for mobile
   - Touch-friendly sizes (56px desktop, 64px mobile)
   - Hides on idle screen

4. **Kiosk Layout** (`routes/kiosk/+layout.svelte`)
   - Wraps all kiosk pages with KioskHeader
   - Flex column layout (header + main content)

**Enhanced Features:**
- **Main Kiosk Page** (`routes/kiosk/+page.svelte`)
  - Simplified: Shows setup if not configured, else redirects to idle screen
  - After configuration, goes to idle instead of old welcome screen
  
- **Accessibility Enhancements** (`app.css`)
  - Touch-friendly button classes (.btn-touch, .btn-kiosk-touch)
  - High contrast mode support (prefers-contrast media query + .high-contrast class)
  - Font size control classes (font-size-small/normal/large/xlarge)
  - Reduced motion support (prefers-reduced-motion)
  - Focus-visible improvements (3px solid outline, 2px offset)
  - Screen reader utilities (.sr-only-custom with focus reveal)
  - Dark mode support (prefers-color-scheme: dark)
  - Skip-to-main link for keyboard navigation

**User Experience Flow:**
```
1. First Visit → Kiosk Setup (/kiosk)
2. After Setup → Idle Screen (/kiosk/idle)
3. Tap Anywhere → Browse Products (/kiosk/products)
4. Navigation → Breadcrumbs + Back Button visible
5. Cart Badge → Always visible (floating on mobile)
6. Inactivity (2 min) → Back to Idle Screen
7. Session Timeout (15 min) → Clear cart + Back to Idle
```

**Files Modified:**
- `frontend/src/routes/kiosk/idle/+page.svelte` (NEW)
- `frontend/src/lib/stores/navigationStore.ts` (NEW)
- `frontend/src/lib/components/kiosk/KioskHeader.svelte` (NEW)
- `frontend/src/routes/kiosk/+layout.svelte` (NEW)
- `frontend/src/routes/kiosk/+page.svelte` (Updated)
- `frontend/src/app.css` (Enhanced accessibility)

**Verification:**
- ✅ HTTP 200 on /kiosk/idle
- ✅ HTTP 200 on /kiosk
- ✅ Carousel auto-rotates
- ✅ Session manager initializes on mount
- ✅ Header shows/hides correctly
- ✅ Cart badge updates with item count
- ✅ Breadcrumbs generate correctly
- ✅ Back button confirms if cart has items
- ✅ Responsive on mobile/tablet/desktop

---

### ✅ Receipt Page Implementation - COMPLETE (Earlier Today)
**Status:** Fully functional with all data displaying correctly

**Issues Fixed:**
1. **X-Tenant-ID Header Missing** 
   - Problem: Receipt API returned "No tenant ID provided" error
   - Solution: Added `X-Tenant-ID` header from `kioskConfig.tenantId` to receipt fetch request
   
2. **Data Structure Mismatch**
   - Problem: Receipt template expected wrong field names (e.g., `location_name` vs `location.name`)
   - Solution: Updated all field mappings to match API response:
     - `orderGroup.location?.name` (store name)
     - `orderGroup.customer?.name` (customer name)
     - `order.tenant` (tenant name)
     - `order.outlet` (brand name)
     - `item.name` (product name)
     - `item.total` (item price)
     - `order.tax`, `order.total` (order totals)
     - `orderGroup.payment?.total`, `orderGroup.payment?.method`

3. **HTML Structure Errors**
   - Problem: Multiple Svelte compilation errors - "</div> attempted to close an element that was not open"
   - Root Cause: Extra closing `</div>` after `{/each}` loop (line 196), missing proper closing for receipt-orders and receipt divs
   - Solution: 
     - Removed extra `</div>` after `{/each}` loop
     - Added proper closing comments: `</div> <!-- End receipt-orders -->` and `</div> <!-- End receipt -->` after payment-info section
     - Added Grand Total section between orders loop and payment info
     - Fixed all div nesting structure

4. **Vite Cache Issues**
   - Problem: Changes not reflected due to aggressive Vite caching
   - Solution: Cleared cache with `docker exec kiosk_pos_frontend rm -rf /app/node_modules/.vite` and restarted frontend container

**Files Modified:**
- `frontend/src/routes/kiosk/success/[groupNumber]/+page.svelte`
  - Added `kioskConfig` import and X-Tenant-ID header
  - Fixed all data field mappings
  - Fixed HTML structure (proper div closing, added Grand Total section)
  - Added console.log debugging statements

**Verification:**
- ✅ HTTP 200 response on receipt page load
- ✅ No Svelte compilation errors
- ✅ Proper HTML structure validated
- ✅ Receipt displays all order data (store, customer, items, totals, payment)

**Testing:**
```bash
# Test receipt page
http://localhost:5174/kiosk/success/GRP-20260108-7407

# Check backend API
curl -H "X-Tenant-ID: 147" http://localhost:8001/api/order-groups/GRP-20260108-7407/receipt/

# Expected: Full receipt with all order data, no undefined/RpNaN values
```

---

## 🏗️ Architecture (OPSI 2)

```
┌─────────────────────────────────────────────────────────────────┐
│              MULTI-STORE MULTI-OUTLET KIOSK FLOW                 │
└─────────────────────────────────────────────────────────────────┘

DATA HIERARCHY:
🏢 YOGYA (Tenant/Company)
  │
  ├─ 🏪 OUTLETS (Brands - Owned by YOGYA)
  │    ├─ 🍗 Chicken Sumo (Outlet ID: 423)
  │    │    └─ Kitchen Stations: MAIN, GRILL
  │    ├─ 🍞 Magic Oven (Outlet ID: 424)
  │    │    └─ Kitchen Stations: MAIN, OVEN
  │    └─ 🍕 Magic Pizza (Outlet ID: 425)
  │         └─ Kitchen Stations: MAIN, PIZZA
  │
  └─ 📍 STORES (Physical Locations - Owned by YOGYA)
       ├─ Yogya Kapatihan (Store ID: 1)
       │    ├─ Has Brands: Chicken Sumo, Magic Oven, Magic Pizza
       │    └─ Opening: 08:00 - 21:00
       │
       ├─ Yogya Sunda (Store ID: 2)
       │    ├─ Has Brands: Chicken Sumo, Magic Oven
       │    └─ Opening: 09:00 - 22:00
       │
       └─ Yogya Riau (Store ID: 3)
            ├─ Has Brands: Magic Pizza only
            └─ Opening: 10:00 - 21:00

🏢 BORMA (Tenant/Company)
  │
  ├─ 🏪 OUTLETS (Brands - Owned by BORMA)
  │    ├─ ☕ Borma Cafe (Outlet ID: 426)
  │    ├─ 🥐 Borma Bakery (Outlet ID: 427)
  │    └─ 🥗 Borma Fresh (Outlet ID: 428)
  │
  └─ 📍 STORES (Physical Locations - Owned by BORMA)
       ├─ Borma Dago, Borma Pasteur, etc.

⚠️ MANY-TO-MANY RELATIONSHIP (SAME TENANT ONLY):
- One Brand (Outlet) can be in multiple Stores (same tenant)
- One Store can have multiple Brands (Outlets) (same tenant)
- Junction Table: StoreOutlet (with unique constraint)
- ⚠️ IMPORTANT: Store can only assign outlets from the same tenant

📋 MENU/PRODUCT HIERARCHY:
- Categories belong to Outlet (each brand has own categories)
- Products belong to Outlet (each brand has own menu)
- Example:
  * Chicken Sumo → Categories: Fried Chicken, Combos, Drinks
  * Magic Oven → Categories: Breads, Pastries, Cakes
  * Magic Pizza → Categories: Pizza, Pasta, Desserts

STEP 1: KIOSK SETUP (One-time, Admin Only)
┌──────────────────────────────────────────┐
│   Enter Store Code: YOGYA-KAPATIHAN      │
│   ↓                                        │
│   Validate with Backend                   │
│   ↓                                        │
│   Save to localStorage:                   │
│   - storeCode (YOGYA-KAPATIHAN)           │
│   - storeName (Yogya Kapatihan)           │
│   - storeId                               │
│   - tenantName (YOGYA)                    │
│   - deviceId (generated)                  │
│   - enableMultiOutlet (true)              │
└──────────────────────────────────────────┘
         ↓
         
STEP 2: CUSTOMER - BROWSE ALL PRODUCTS AT STORE
┌──────────────────────────────────────────┐
│   Load ALL products from ALL brands at store  │
│   ↓                                          │
│   Display products with brand labels:        │
│   - Chicken Sumo Original (Chicken Sumo)     │
│   - Margherita Pizza (Magic Pizza)           │
│   - Croissant (Magic Oven)                   │
│   - etc...                                   │
│   ↓                                          │
│   Customer can filter by:                    │
│   - Brand (Chicken Sumo, Magic Oven, etc)    │
│   - Category (Fried Chicken, Pizza, etc)     │
│   - Search by name                           │
│   ↓                                          │
│   Add to cart (auto-group by brand)          │
└──────────────────────────────────────────┘
         ↓
         
STEP 3: MULTI-BRAND SHOPPING (AUTO-GROUPED)
┌──────────────────────────────────────────┐
│   Cart Structure (Auto-grouped by brand): │
│   {                                        │
│     carts: {                              │
│       1: { // Outlet ID (Chicken Sumo)    │
│         outletId: 1,                      │
│         brandName: "Chicken Sumo",        │
│         tenantName: "YOGYA",              │
│         items: [...],                     │
│         subtotal, tax, total              │
│       },                                   │
│       3: { // Outlet ID (Magic Pizza)     │
│         outletId: 3,                      │
│         brandName: "Magic Pizza",         │
│         tenantName: "YOGYA",              │
│         items: [...],                     │
│         subtotal, tax, total              │
│       }                                    │
│     },                                     │
│     totalAmount: 150000                   │
│   }                                        │
│                                            │
│   ✅ Products automatically grouped by    │
│      brand when added to cart              │
│   ✅ Customer can mix products from any   │
│      brand without selecting outlet first  │
└──────────────────────────────────────────┘
         ↓
         
STEP 4: CHECKOUT & PAYMENT
┌──────────────────────────────────────────┐
│   Create OrderGroup:                      │
│   - group_number: GRP-20260107-ABCD       │
│   - store_id: 1 (Yogya Kapatihan)        │
│   - carts: [outlet1_cart, outlet2_cart]   │
│   ↓                                        │
│   Backend creates:                        │
│   - 1 OrderGroup                          │
│   - Multiple Orders (one per outlet)      │
│   - OrderItems per order                  │
│   ↓                                        │
│   Payment:                                │
│   - Single payment for all brands         │
│   - Total = sum of all outlet totals      │
│   ↓                                        │
│   Mark OrderGroup as paid                 │
│   → All orders marked as paid             │
│   → Sent to kitchen displays per brand    │
└──────────────────────────────────────────┘
         ↓
         
STEP 5: KITCHEN DISPLAY (Per Brand at Store)
┌──────────────────────────────────────────┐
│   🍗 Chicken Sumo Kitchen @ Yogya Kapatihan│
│   ↓                                        │
│   Receives Order #1:                      │
│   - Store: Yogya Kapatihan                │
│   - Brand: Chicken Sumo (Global)          │
│   - 2x Chicken Sumo Original              │
│   - 1x Chicken Sumo Combo                 │
│   Status: Pending → Preparing → Ready     │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│   🍕 Magic Pizza Kitchen @ Yogya Kapatihan │
│   ↓                                        │
│   Receives Order #2:                      │
│   - Store: Yogya Kapatihan                │
│   - Brand: Magic Pizza (Global)           │
│   - 1x Margherita Pizza                   │
│   - 1x Hawaiian Pizza                     │
│   Status: Pending → Preparing → Ready     │
└──────────────────────────────────────────┘

NOTE: Kitchen routing requires store + outlet (brand) + kitchen station
- Each brand has own kitchen stations (outlet-level)
- Same brand at different stores uses same station setup
- Example: Chicken Sumo GRILL station exists at all Chicken Sumo locations
```

---

## 📊 Database Models (OPSI 2)

### 1. Tenant Model
```python
class Tenant(models.Model):
    name = CharField(max_length=200)  # YOGYA, BORMA, MATAHARI, CARREFOUR
    slug = SlugField(unique=True)  # yogya, borma, matahari, carrefour
    description = TextField()
    primary_color = CharField(max_length=7)  # #E74C3C
    secondary_color = CharField(max_length=7)  # #C0392B
```

**Purpose:** Retail company/chain that owns multiple stores

### 2. Store Model (Previously Location)
```python
class Store(models.Model):
    tenant = ForeignKey(Tenant, on_delete=CASCADE)  # YOGYA
    code = CharField(max_length=50, unique=True)  # YOGYA-KAPATIHAN
    name = CharField(max_length=200)  # Yogya Kapatihan
    address = TextField()  # Jl. Ahmad Yani No. 288
    city = CharField()  # Bandung
    province = CharField()  # Jawa Barat
    kiosk_qr_code = CharField(unique=True)  # For QR setup
    latitude, longitude = DecimalField()  # Geo coordinates
    
    # Operating hours (NEW - moved from Outlet)
    opening_time = TimeField(null=True, blank=True)  # 08:00:00
    closing_time = TimeField(null=True, blank=True)  # 21:00:00
    
    # Many-to-Many relationship with Outlets (Brands)
    outlets = ManyToManyField('Outlet', through='StoreOutlet', related_name='stores')
```

**Purpose:** Physical retail store location (Yogya Kapatihan, Borma Dago, etc.)
**Change:** Operating hours moved here from Outlet, M2M relationship with Outlets

### 3. Outlet Model (Brand - Per Tenant)
```python
class Outlet(models.Model):
    tenant = ForeignKey(Tenant)  # YOGYA, BORMA, MATAHARI, CARREFOUR
    brand_name = CharField(max_length=200)  # Chicken Sumo, Borma Cafe, Matahari FC
    name = CharField()  # Same as brand_name (e.g., "Chicken Sumo")
    slug = SlugField(max_length=200)
    
    # Contact (Brand contact)
    phone = CharField(max_length=20, blank=True)
    email = EmailField(blank=True)
    
    # Network Configuration (for kitchen sync - Socket.IO)
    websocket_url = CharField(
        max_length=255, 
        blank=True, 
        default='http://localhost:3001',
        help_text='Socket.IO server URL (use http:// protocol, port 3001)'
    )
    
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    # Relations:
    # - kitchen_stations (reverse FK from KitchenStation)
    # - categories (reverse FK from Category)
    # - products (reverse FK from Product)
```

**Purpose:** Brand/Business Unit (Owned by specific tenant)
**Change:** Each tenant has their own outlets/brands
**Examples:**
- YOGYA tenant → Chicken Sumo, Magic Oven, Magic Pizza
- BORMA tenant → Borma Cafe, Borma Bakery, Borma Fresh
- MATAHARI tenant → Matahari Food Court, Matahari Coffee, Matahari Snack Bar
- CARREFOUR tenant → Carrefour Bistro, Carrefour Bakery, Carrefour Express
**Kitchen:** Each brand has own kitchen stations (e.g., Chicken Sumo → MAIN, GRILL)

### 4. StoreOutlet Model (Junction Table - NEW)
```python
class StoreOutlet(models.Model):
    """
    Junction table for Many-to-Many relationship between Store and Outlet
    Represents which brands are available at which stores
    ⚠️ IMPORTANT: Store and Outlet must belong to the same tenant
    """
    store = ForeignKey(Store, on_delete=CASCADE, related_name='store_outlets')
    outlet = ForeignKey(Outlet, on_delete=CASCADE, related_name='store_outlets')
    is_active = BooleanField(default=True)
    
    # Optional: Per-store customization
    custom_opening_time = TimeField(null=True, blank=True)  # Override store hours
    custom_closing_time = TimeField(null=True, blank=True)
    display_order = IntegerField(default=0)  # Sort order in kiosk UI
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'store_outlets'
        unique_together = ['store', 'outlet']  # ⚠️ No duplicate brand in same store
        ordering = ['store', 'display_order', 'outlet__brand_name']
    
    def __str__(self):
        return f"{self.outlet.brand_name} at {self.store.name}"
```

**Purpose:** Link brands to stores (M2M relationship - same tenant only)
**Constraint:** 
- `unique_together` prevents duplicate brand in same store
- Store can only assign outlets from the same tenant (enforced in admin UI)
**Example:**
- ✅ YOGYA Store → YOGYA Outlets (Chicken Sumo, Magic Oven, Magic Pizza)
- ❌ YOGYA Store → BORMA Outlets (Not allowed - different tenant)

### 5. OrderGroup Model
```python
class OrderGroup(models.Model):
    group_number = CharField(unique=True)  # GRP-20260107-ABCD
    store = ForeignKey(Store)  # Yogya Kapatihan
    
    # Customer info
    customer_name, customer_phone, customer_email
    
    # Payment
    payment_status = CharField()  # unpaid/paid/refunded
    payment_method = CharField()  # cash/card/qris/ewallet
    total_amount = DecimalField()
    paid_amount = DecimalField()
    
    # Tracking
    source = CharField()  # kiosk/web
    device_id = CharField()  # KIOSK-YOGYA-KAPATIHAN-001
    session_id = CharField()
    
    # Relations:
    orders = ForeignKey('Order', related_name='order_group')
```

**Purpose:** Group multiple outlet/brand orders in single payment transaction

### 6. Category Model (NEW - Per Outlet/Brand)
```python
class Category(models.Model):
    outlet = ForeignKey(Outlet, on_delete=CASCADE)  # Chicken Sumo
    name = CharField(max_length=200)  # Fried Chicken, Combos, Drinks
    description = TextField(blank=True)
    image = ImageField(upload_to='categories/', null=True, blank=True)
    sort_order = IntegerField(default=0)
    is_active = BooleanField(default=True)
    
    # Kitchen Station Routing
    kitchen_station_code = CharField(
        max_length=20,
        default='MAIN',
        help_text='Auto-route products to kitchen station'
    )
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**Purpose:** Product categories per brand (each outlet has own menu structure)
**Change:** Moved from Tenant to Outlet - each brand manages own categories

### 7. Product Model (Per Outlet/Brand)
```python
class Product(models.Model):
    outlet = ForeignKey(Outlet, on_delete=CASCADE)  # Chicken Sumo
    category = ForeignKey(Category, on_delete=SET_NULL, null=True)
    
    # Kitchen Station Override (optional)
    kitchen_station_code_override = CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='Override category routing'
    )
    
    sku = CharField(max_length=50, unique=True)
    name = CharField(max_length=200)  # Chicken Sumo Original
    description = TextField(blank=True)
    image = ImageField(upload_to='products/', null=True, blank=True)
    
    # Pricing
    price = DecimalField(max_digits=10, decimal_places=2)
    cost = DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Stock
    track_stock = BooleanField(default=False)
    stock_quantity = IntegerField(default=0)
    low_stock_alert = IntegerField(default=10)
    
    # Flags
    is_active = BooleanField(default=True)
    is_featured = BooleanField(default=False)
    is_available = BooleanField(default=True)
    is_popular = BooleanField(default=False)
    has_promo = BooleanField(default=False)
    promo_price = DecimalField(null=True, blank=True)
    
    # Metadata
    preparation_time = IntegerField(default=10)  # minutes
    calories = IntegerField(null=True, blank=True)
    tags = CharField(max_length=500, blank=True)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**Purpose:** Menu items per brand (each outlet has own products)
**Change:** Moved from Tenant to Outlet - each brand manages own menu
**Note:** Pricing is same across all stores for now, can be customized per store later via StoreOutlet or OutletProduct table

### 8. ProductModifier Model (Per Product/Outlet)
```python
class ProductModifier(models.Model):
    MODIFIER_TYPES = (
        ('size', 'Size'),
        ('topping', 'Topping'),
        ('spicy', 'Spicy Level'),
        ('extra', 'Extra'),
        ('sauce', 'Sauce'),
    )
    
    product = ForeignKey(Product, on_delete=CASCADE, related_name='modifiers')
    outlet = ForeignKey(Outlet, on_delete=CASCADE)  # NEW - for global modifiers
    name = CharField(max_length=200)  # Extra Cheese, Large Size, Level 5
    type = CharField(max_length=20, choices=MODIFIER_TYPES)
    price_adjustment = DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = BooleanField(default=True)
    sort_order = IntegerField(default=0)
```

**Purpose:** Product modifiers/add-ons per outlet
**Change:** Can be product-specific or outlet-wide (global modifiers)

### 9. KitchenStation Model (Per Outlet/Brand)
```python
class KitchenStation(models.Model):
    outlet = ForeignKey(Outlet, on_delete=CASCADE, related_name='kitchen_stations')
    name = CharField(max_length=100)  # Main Kitchen, Grill Station, Beverage Bar
    code = CharField(max_length=20)  # MAIN, GRILL, BEVERAGE, PIZZA, OVEN
    description = TextField(blank=True)
    
    is_active = BooleanField(default=True)
    sort_order = IntegerField(default=0)
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['outlet', 'code']  # No duplicate station per outlet
```

**Purpose:** Kitchen stations per brand (each outlet has own kitchen setup)
**Change:** Moved from being store-specific to outlet-specific
**Example:** 
- Chicken Sumo outlets have: MAIN, GRILL stations
- Magic Oven outlets have: MAIN, OVEN stations
- Magic Pizza outlets have: MAIN, PIZZA stations

### 10. Order Model
```python
class Order(models.Model):
    tenant = ForeignKey(Tenant)  # YOGYA
    store = ForeignKey(Store)  # Yogya Kapatihan (NEW - for kitchen routing)
    outlet = ForeignKey(Outlet)  # Chicken Sumo (Global brand)
    order_group = ForeignKey(OrderGroup, null=True)  # Link to group
    
    order_number = CharField(unique=True)  # ORD-20260107-XYZ1
    status = CharField()  # pending/preparing/ready/completed/cancelled
    
    # Amounts
    subtotal, tax, service_charge, total_amount
    
    # Kitchen routing (station belongs to outlet, not store)
    kitchen_station = ForeignKey(KitchenStation, null=True)
    
    # Timestamps
    created_at, updated_at, completed_at
```

**Purpose:** Individual order per outlet/brand, linked to OrderGroup
**Kitchen Routing:** Order routes to specific outlet's kitchen station at specific store

---

## 🔌 API Endpoints (OPSI 2)

### Store Endpoints

#### 1. List Stores (Public)
```http
GET /api/public/stores/
```
Response:
```json
[
  {
    "id": 1,
    "code": "YOGYA-KAPATIHAN",
    "name": "Yogya Kapatihan",
    "tenant_name": "YOGYA",
    "address": "Jl. Ahmad Yani No. 288, Kapatihan",
    "city": "Bandung",
    "outlets_count": 3,
    "active_outlets_count": 3
  },
  {
    "id": 4,
    "code": "BORMA-DAGO",
    "name": "Borma Dago",
    "tenant_name": "BORMA",
    "address": "Jl. Ir. H. Juanda No. 135 (Dago)",
    "city": "Bandung",
    "outlets_count": 3,
    "active_outlets_count": 3
  }
]
```

#### 2. Validate Store Code
```http
GET /api/public/stores/{code}/validate/
```
Response:
```json
{
  "valid": true,
  "store": {
    "id": 1,
    "code": "YOGYA-KAPATIHAN",
    "name": "Yogya Kapatihan",
    "tenant_name": "YOGYA",
    "address": "Jl. Ahmad Yani No. 288, Kapatihan",
    "city": "Bandung"
  },
  "outlets_count": 3
}
```

#### 3. Get Outlets for Store
```http
GET /api/public/stores/{code}/outlets/
```
Response:
```json
{
  "store": "YOGYA-KAPATIHAN",
  "store_name": "Yogya Kapatihan",
  "store_opening_time": "08:00:00",
  "store_closing_time": "21:00:00",
  "tenant_name": "YOGYA",
  "outlets_count": 3,
  "outlets": [
    {
      "id": 1,
      "name": "Chicken Sumo",
      "brand_name": "Chicken Sumo",
      "tenant": {
        "id": 1,
        "name": "YOGYA",
        "slug": "yogya",
        "logo": "/media/tenants/yogya.png",
        "primary_color": "#E74C3C"
      },
      "is_active": true,
      "store_outlet": {
        "is_active": true,
        "display_order": 1,
        "custom_opening_time": null,
        "custom_closing_time": null
      }
    },
    {
      "id": 2,
      "name": "Magic Oven",
      "brand_name": "Magic Oven",
      "tenant": {
        "id": 1,
        "name": "YOGYA",
        "slug": "yogya",
        "primary_color": "#E74C3C"
      },
      "is_active": true,
      "store_outlet": {
        "is_active": true,
        "display_order": 2,
        "custom_opening_time": null,
        "custom_closing_time": null
      }
    },
    {
      "id": 3,
      "name": "Magic Pizza",
      "brand_name": "Magic Pizza",
      "tenant": {
        "id": 1,
        "name": "YOGYA",
        "slug": "yogya",
        "primary_color": "#E74C3C"
      },
      "is_active": true,
      "store_outlet": {
        "is_active": true,
        "display_order": 3,
        "custom_opening_time": "10:00:00",
        "custom_closing_time": "20:00:00"
      }
    }
  ]
}
```

**Note:** Query uses StoreOutlet junction table to get only brands available at this store

#### 4. Get Store by QR Code
```http
GET /api/public/stores/by-qr/{qr_code}/
```
Response: Same as validate endpoint

#### 5. Get All Products at Store (NEW)
```http
GET /api/public/stores/{code}/products/
```
Response:
```json
{
  "store": "YOGYA-KAPATIHAN",
  "store_name": "Yogya Kapatihan",
  "tenant_name": "YOGYA",
  "products_count": 27,
  "outlets": [
    {
      "id": 1,
      "brand_name": "Chicken Sumo",
      "products_count": 9
    },
    {
      "id": 2,
      "brand_name": "Magic Oven",
      "products_count": 9
    },
    {
      "id": 3,
      "brand_name": "Magic Pizza",
      "products_count": 9
    }
  ],
  "products": [
    {
      "id": 1,
      "name": "Chicken Sumo Original",
      "price": 25000,
      "image": "/media/products/chicken-original.jpg",
      "category": "Fried Chicken",
      "outlet": {
        "id": 1,
        "brand_name": "Chicken Sumo",
        "tenant": {
          "name": "YOGYA",
          "primary_color": "#E74C3C"
        }
      },
      "is_available": true,
      "preparation_time": 10
    },
    {
      "id": 7,
      "name": "Margherita Pizza",
      "price": 65000,
      "image": "/media/products/margherita.jpg",
      "category": "Pizza",
      "outlet": {
        "id": 3,
        "brand_name": "Magic Pizza",
        "tenant": {
          "name": "YOGYA",
          "primary_color": "#E74C3C"
        }
      },
      "is_available": true,
      "preparation_time": 15
    }
  ],
  "categories": [
    "Fried Chicken",
    "Combos",
    "Drinks",
    "Pizza",
    "Pasta",
    "Breads",
    "Pastries",
    "Cakes"
  ]
}
```

**Note:** Returns ALL products from ALL brands available at this store

---

### Order Group Endpoints

#### 1. Create Multi-Outlet Order Group
```http
POST /api/public/order-groups/
Content-Type: application/json
```

Request Body:
```json
{
  "store_id": 1,
  "customer_name": "Budi Santoso",
  "customer_phone": "081234567890",
  "customer_email": "budi@example.com",
  "source": "kiosk",
  "device_id": "KIOSK-YOGYA-KAPATIHAN-001",
  "session_id": "SESS-ABC123",
  "carts": [
    {
      "outlet_id": 1,
      "items": [
        {
          "product_id": 1,
          "quantity": 2,
          "modifiers": [],
          "notes": "Extra spicy please"
        },
        {
          "product_id": 3,
          "quantity": 1,
          "modifiers": [],
          "notes": ""
        }
      ]
    },
    {
      "outlet_id": 3,
      "items": [
        {
          "product_id": 7,
          "quantity": 1,
          "modifiers": [],
          "notes": "No olives"
        }
      ]
    }
  ]
}
```

Response:
```json
{
  "id": 1,
  "group_number": "GRP-20260107-ABCD",
  "store_name": "Yogya Kapatihan",
  "tenant_name": "YOGYA",
  "payment_status": "unpaid",
  "total_amount": 165000,
  "orders": [
    {
      "id": 1,
      "order_number": "ORD-20260107-XYZ1",
      "tenant_name": "YOGYA",
      "store_name": "Yogya Kapatihan",
      "outlet_name": "Chicken Sumo",
      "brand_name": "Chicken Sumo",
      "total_amount": 85000,
      "items": [
        {
          "product_name": "Chicken Sumo Original",
          "quantity": 2,
          "price": 25000,
          "subtotal": 50000
        },
        {
          "product_name": "Chicken Sumo Combo",
          "quantity": 1,
          "price": 35000,
          "subtotal": 35000
        }
      ]
    },
    {
      "id": 2,
      "order_number": "ORD-20260107-XYZ2",
      "tenant_name": "YOGYA",
      "store_name": "Yogya Kapatihan",
      "outlet_name": "Magic Pizza",
      "brand_name": "Magic Pizza",
      "total_amount": 75000,
      "items": [
        {
          "product_name": "Pepperoni Pizza",
          "quantity": 1,
          "price": 75000,
          "subtotal": 75000
        }
      ]
    }
  ],
  "outlet_breakdown": {
    "Chicken Sumo": {
      "amount": 85000,
      "items_count": 3
    },
    "Magic Pizza": {
      "amount": 75000,
      "items_count": 1
    }
  }
}
```

#### 2. Mark Order Group as Paid
```http
POST /api/public/order-groups/{group_number}/mark-paid/
Content-Type: application/json
```

Request:
```json
{
  "payment_method": "qris"
}
```

Response:
```json
{
  "message": "Payment successful",
  "order_group": {
    "id": 1,
    "group_number": "GRP-20260107-ABCD",
    "store_name": "Yogya Kapatihan",
    "payment_status": "paid",
    "payment_method": "qris",
    "paid_amount": 165000,
    "paid_at": "2026-01-07T10:30:00Z"
  },
  "orders_sent_to_kitchen": [
    "ORD-20260107-XYZ1",
    "ORD-20260107-XYZ2"
  ]
}
```

#### 3. Get Receipt
```http
GET /api/public/order-groups/{group_number}/receipt/
```

---

## 💻 Frontend Implementation

### 1. Kiosk Store (`kioskStore.ts`)

```typescript
// Config
export const kioskConfig = writable<KioskConfig>({
  storeCode: null,        // YOGYA-KAPATIHAN
  storeName: null,        // Yogya Kapatihan
  storeId: null,          // 1
  tenantName: null,       // YOGYA
  deviceId: string,       // KIOSK-YOGYA-KAPATIHAN-001
  isConfigured: boolean,
  enableMultiOutlet: boolean
});

// Multi-Cart
export const multiCart = writable<MultiCart>({
  carts: {
    1: { // Outlet ID
      outletId: 1,
      brandName: "Chicken Sumo",
      tenantName: "YOGYA",
      items: [...],
      subtotal, tax, serviceCharge, total
    },
    3: { // Another outlet
      outletId: 3,
      brandName: "Magic Pizza",
      tenantName: "YOGYA",
      items: [...],
      subtotal, tax, serviceCharge, total
    }
  },
  totalAmount: 165000,
  itemsCount: 4,
  outletsCount: 2
});

// Methods
multiCart.addItem(outletId, product, quantity, modifiers, notes);
multiCart.updateQuantity(outletId, itemId, newQuantity);
multiCart.removeItem(outletId, itemId);
multiCart.clearOutlet(outletId);
multiCart.clearAll();
multiCart.getCheckoutData(); // Format for API
```

### 2. Components

#### `KioskSetup.svelte`
- Enter store code or scan QR (e.g., YOGYA-KAPATIHAN)
- Validate with backend `/api/public/stores/{code}/validate/`
- Display: "Yogya Kapatihan - 3 brands available"
- Save to localStorage: storeCode, storeName, storeId, tenantName
- Auto-redirect to outlet selection

#### `ProductBrowse.svelte` (Main Shopping Page)
- Load ALL products from ALL brands at store: `/api/public/stores/{code}/products/`
- Display product grid:
  * Product image, name, price
  * Brand badge (Chicken Sumo, Magic Oven, etc)
  * Category tag (Fried Chicken, Pizza, etc)
- Filter options:
  * Brand filter (multi-select: Chicken Sumo, Magic Oven, Magic Pizza)
  * Category filter (Fried Chicken, Combos, Drinks, Pizza, Breads, etc)
  * Search bar (search by product name)
- Click product → Product detail modal
  * Show modifiers (size, toppings, spicy level)
  * Quantity selector
  * Add to cart button
- Cart badge shows total items across all brands
- Products automatically grouped by brand/outlet in cart

**Responsive Design (Mobile, iPad, Desktop):**
- Product images: Full-width within card container
- Grid layout:
  * Mobile: 1 column (full width)
  * Tablet/iPad: 2-3 columns
  * Desktop: 3-4 columns
- Touch-friendly controls (min 44px tap targets)
- Adaptive font sizes and spacing
- Single codebase for all devices

#### `MultiCart.svelte`
- Display items grouped by brand
- Show store context in header: "Yogya Kapatihan"
- Breakdown per brand:
  ```
  🍗 Chicken Sumo
    2x Chicken Sumo Original    Rp 50,000
    1x Chicken Sumo Combo       Rp 35,000
    Subtotal:                   Rp 85,000
  
  🍕 Magic Pizza
    1x Pepperoni Pizza          Rp 75,000
    Subtotal:                   Rp 75,000
  
  TOTAL:                        Rp 165,000
  ```
- Quantity controls per item
- Remove brand button
- Checkout button → `/kiosk/checkout`

---

## 📱 Responsive Design Requirements

### Device Support
**Single Application for All Devices:**
- 📱 **Mobile Phones** (320px - 480px)
  - Portrait mode primary
  - Full-width product cards
  - Single column layout
  - Bottom navigation
  - Touch-optimized (44px min tap targets)

- 📱 **Tablets/iPad** (768px - 1024px)
  - Portrait & landscape support
  - 2-3 column product grid
  - Side navigation option
  - Touch-optimized (44px min tap targets)
  - Larger product images

- 💻 **Desktop/Kiosk** (1280px+)
  - 3-4 column product grid
  - Mouse + touch support
  - Larger tap targets (60px+ for kiosk)
  - Maximum image quality
  - Full-screen mode option

### Layout Guidelines

#### Product Cards
```css
/* Product Image - Full Width */
.product-card {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.product-image {
  width: 100%;           /* Full-width image */
  aspect-ratio: 1 / 1;   /* Square ratio */
  object-fit: cover;     /* Cover container */
  border-radius: 8px;
}

/* Responsive Grid */
.product-grid {
  display: grid;
  gap: 1rem;
  
  /* Mobile: 1 column */
  grid-template-columns: 1fr;
  
  /* Tablet: 2-3 columns */
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (min-width: 900px) {
    grid-template-columns: repeat(3, 1fr);
  }
  
  /* Desktop: 3-4 columns */
  @media (min-width: 1280px) {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

#### Touch Targets
```css
/* Buttons & Interactive Elements */
.btn-touch {
  min-height: 44px;  /* Mobile minimum */
  min-width: 44px;
  padding: 12px 24px;
}

.btn-kiosk {
  min-height: 60px;  /* Kiosk/Desktop */
  min-width: 60px;
  padding: 16px 32px;
  font-size: 18px;
}
```

#### Typography
```css
/* Responsive Font Sizes */
.product-name {
  font-size: clamp(14px, 2vw, 18px);
}

.product-price {
  font-size: clamp(16px, 2.5vw, 24px);
  font-weight: bold;
}

.heading {
  font-size: clamp(20px, 4vw, 32px);
}
```

### Implementation Strategy
1. **Mobile-First CSS** - Start with mobile styles, enhance for larger screens
2. **CSS Grid/Flexbox** - Modern layout techniques for flexibility
3. **Viewport Units** - Use vw, vh for fluid sizing
4. **Media Queries** - Breakpoints: 768px (tablet), 1024px (desktop), 1280px (large)
5. **Touch Events** - Support both touch and mouse interactions
6. **Performance** - Lazy load images, optimize for mobile networks
7. **Testing** - Test on real devices (iPhone, iPad, Android, Desktop)

### Svelte Implementation Example
```svelte
<script>
  import { onMount } from 'svelte';
  
  let isMobile = false;
  let isTablet = false;
  let isDesktop = false;
  
  onMount(() => {
    const checkDevice = () => {
      const width = window.innerWidth;
      isMobile = width < 768;
      isTablet = width >= 768 && width < 1280;
      isDesktop = width >= 1280;
    };
    
    checkDevice();
    window.addEventListener('resize', checkDevice);
    
    return () => window.removeEventListener('resize', checkDevice);
  });
</script>

<div class="product-grid" class:mobile={isMobile} class:tablet={isTablet} class:desktop={isDesktop}>
  {#each products as product}
    <div class="product-card">
      <img 
        src={product.image} 
        alt={product.name}
        class="product-image"
        loading="lazy"
      />
      <h3 class="product-name">{product.name}</h3>
      <p class="product-price">Rp {product.price.toLocaleString('id-ID')}</p>
      <button class="btn-touch btn-add-cart">Add to Cart</button>
    </div>
  {/each}
</div>

<style>
  .product-grid {
    display: grid;
    gap: 1rem;
    padding: 1rem;
    grid-template-columns: 1fr; /* Mobile default */
  }
  
  .product-grid.tablet {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
  
  .product-grid.desktop {
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
  }
  
  .product-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s;
  }
  
  .product-card:hover {
    transform: translateY(-4px);
  }
  
  .product-image {
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: cover;
  }
  
  .product-name {
    font-size: clamp(14px, 2vw, 18px);
    padding: 0.5rem 1rem 0;
  }
  
  .product-price {
    font-size: clamp(16px, 2.5vw, 24px);
    font-weight: bold;
    padding: 0.25rem 1rem;
    color: #E74C3C;
  }
  
  .btn-add-cart {
    width: 100%;
    min-height: 44px;
    margin: 1rem 0 0;
    background: #E74C3C;
    color: white;
    border: none;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
  }
  
  @media (min-width: 1280px) {
    .btn-add-cart {
      min-height: 60px;
      font-size: 18px;
    }
  }
</style>
```

---

## 🎯 Key Features

### 1. **Multi-Brand Cart** ✨
```
Customer Journey:
1. Enter store → See ALL products from ALL brands
2. Filter/Search: "Chicken" → Shows Chicken Sumo products
3. Add: Chicken Sumo Original (25k) → Auto-added to Chicken Sumo cart
4. Filter: "Pizza" → Shows Magic Pizza products
5. Add: Margherita Pizza (65k) → Auto-added to Magic Pizza cart
6. Filter: "Bread" → Shows Magic Oven products
7. Add: Croissant (15k) → Auto-added to Magic Oven cart
8. View Cart:
   ├─ Chicken Sumo: 25k (1 item)
   ├─ Magic Pizza: 65k (1 item)
   └─ Magic Oven: 15k (1 item)
   TOTAL: 105k + taxes
9. Single Payment → 3 separate orders created
10. Each order routes to correct brand kitchen

Note: Customer never explicitly "selects" a brand/outlet.
Products are automatically grouped by their outlet when added to cart.
```

### 2. **Payment Aggregation**
- Single payment transaction for all brands
- Backend distributes to multiple orders
- Each order maintains outlet/brand association
- Kitchen displays receive individual orders per brand
- Customer gets single receipt with breakdown

### 3. **Order Tracking**
```
OrderGroup: GRP-20260107-ABCD
├─ Order 1: ORD-20260107-XYZ1 (Chicken Sumo)
│  └─ Kitchen Display: Chicken Sumo Station
├─ Order 2: ORD-20260107-XYZ2 (Magic Pizza)
│  └─ Kitchen Display: Magic Pizza Station
└─ Order 3: ORD-20260107-XYZ3 (Magic Oven)
   └─ Kitchen Display: Magic Oven Station
```

### 4. **Receipt Generation**
```
┌─────────────────────────────────────────┐
│         YOGYA - Yogya Kapatihan         │
│      GROUP: GRP-20260107-ABCD           │
├─────────────────────────────────────────┤
│ 🍗 Chicken Sumo                       │
│   2x Chicken Sumo Original  50,000     │
│   1x Chicken Sumo Combo     35,000     │
│   Subtotal:                 85,000     │
│   Tax (10%):                 8,500     │
│   Total:                    93,500     │
├─────────────────────────────────────────┤
│ 🍕 Magic Pizza                        │
│   1x Pepperoni Pizza        75,000     │
│   Subtotal:                 75,000     │
│   Tax (10%):                 7,500     │
│   Total:                    82,500     │
├─────────────────────────────────────────┤
│ TOTAL PAYMENT:            176,000     │
│ Payment Method: QRIS                  │
│ Date: 2026-01-07 10:30                │
└─────────────────────────────────────────┘
```

---

## � Admin Interface

### Manage Store Outlets
**Location:** Admin → Stores → Manage Outlets button

**Features:**
1. **View Store Details**
   - Store name, location, tenant
   - Current outlet count

2. **Outlet Assignment**
   - Displays all outlets from the same tenant
   - Visual indicators:
     * Green border + "✓ Assigned" badge for assigned outlets
     * White border for unassigned outlets
   - Real-time button toggle:
     * "➕ Add to Store" (blue button)
     * "❌ Remove from Store" (red button)

3. **Filtering**
   - Automatically filters outlets by store's tenant
   - YOGYA stores only see YOGYA outlets
   - BORMA stores only see BORMA outlets
   - etc.

4. **UI Features**
   - Responsive grid layout (1-3 columns)
   - SweetAlert2 confirmation dialogs
   - Instant UI updates (no page refresh)
   - Back button to stores list

**Usage Flow:**
1. Go to Stores page
2. Click "Manage Outlets" button on any store
3. See available outlets for that store's tenant
4. Click "Add to Store" to assign outlet
5. Button immediately changes to "Remove from Store"
6. Card border turns green with "✓ Assigned" badge
7. Click "Remove from Store" to unassign
8. Button changes back to "Add to Store"

**API Endpoints Used:**
- `GET /api/admin/stores/{id}/` - Get store details
- `GET /api/admin/settings/outlets/?tenant={id}` - Get outlets for tenant
- `GET /api/admin/stores/{id}/outlets/` - Get assigned outlets
- `POST /api/admin/stores/{id}/add_outlet/` - Assign outlet
- `POST /api/admin/stores/{id}/remove_outlet/` - Remove outlet

---

## �🚀 Setup & Usage

### Backend Setup (OPSI 2)

1. **Run Sample Data Script:**
```bash
docker-compose exec backend python setup_complete_test_data.py
```

This creates:
- **4 Tenants:** YOGYA, BORMA, MATAHARI, CARREFOUR (retail companies)
- **12 Stores:** 3 per tenant (physical locations)
  * Each store has opening/closing times, address, city, coordinates
- **12 Outlets/Brands:** 3 per tenant (owned by specific tenant)
  * YOGYA: Chicken Sumo, Magic Oven, Magic Pizza
  * BORMA: Borma Cafe, Borma Bakery, Borma Fresh
  * MATAHARI: Matahari Food Court, Matahari Coffee, Matahari Snack Bar
  * CARREFOUR: Carrefour Bistro, Carrefour Bakery, Carrefour Express
- **StoreOutlet junction entries:** Links brands to stores (same tenant only)
  * Example: YOGYA stores have YOGYA brands assigned
- **Kitchen Stations:** Per outlet (e.g., Chicken Sumo → MAIN, GRILL)
- **Categories & Products:** Sample data for YOGYA outlets only (Chicken Sumo, Magic Oven, Magic Pizza)

2. **Verify Data:**
```python
from apps.tenants.models import Store, Outlet, StoreOutlet

# Get Yogya Kapatihan store
store = Store.objects.get(code='YOGYA-KAPATIHAN')
print(f"Store: {store.name}")
print(f"Tenant: {store.tenant.name}")
print(f"QR Code: {store.kiosk_qr_code}")
print(f"Opening: {store.opening_time} - {store.closing_time}")

# List brands at this store (via M2M)
print(f"Brands available: {store.outlets.count()}")
for outlet in store.outlets.all():
    print(f"  - {outlet.brand_name}")

# Check junction table
print("\nStoreOutlet entries:")
for so in StoreOutlet.objects.filter(store=store):
    print(f"  - {so.outlet.brand_name} (active: {so.is_active})")

# Check outlets assigned to store
print("\nOutlets at this store:")
for so in StoreOutlet.objects.filter(store=store):
    print(f"  - {so.outlet.brand_name} (Tenant: {so.outlet.tenant.name})")

# Check which stores have Chicken Sumo
chicken = Outlet.objects.get(brand_name='Chicken Sumo')
print(f"\n{chicken.brand_name} (Tenant: {chicken.tenant.name}) available at:")
for so in StoreOutlet.objects.filter(outlet=chicken):
    print(f"  - {so.store.name} (Tenant: {so.store.tenant.name})")
```

### Kiosk Setup

1. **Initial Configuration (Admin):**
   - Navigate to: `http://localhost:5174/kiosk/setup`
   - Enter store code: `YOGYA-KAPATIHAN`
   - System validates and displays:
     * Store: Yogya Kapatihan
     * Tenant: YOGYA
     * Brands: 3 (Chicken Sumo, Magic Oven, Magic Pizza)
   - Click "Save Configuration"
   - System saves to localStorage and redirects to kiosk home

2. **Alternative: QR Code Setup**
   - Scan store QR code
   - Auto-fills store code
   - One-click setup

### Customer Flow

1. **Start Order:**
   - Kiosk displays: "Welcome to Yogya Kapatihan"
   - Shows ALL products from ALL brands at this store
   - Product cards show: Image, Name, Price, Brand badge

2. **Browse & Add to Cart:**
   - Customer can:
     * Filter by brand (Chicken Sumo, Magic Oven, Magic Pizza)
     * Filter by category (Fried Chicken, Pizza, Breads, Drinks)
     * Search by product name
   - Select product → Choose quantity/modifiers
   - Add to cart → Automatically grouped by brand
   - Example:
     * Add: 2x Chicken Sumo Original (auto-grouped to Chicken Sumo cart)
     * Add: 1x Margherita Pizza (auto-grouped to Magic Pizza cart)
     * Add: 1x Croissant (auto-grouped to Magic Oven cart)

3. **Review Cart:**
   - Cart shows 2 brands
   - Chicken Sumo: 50k (2 items)
   - Magic Pizza: 65k (1 item)
   - Total: 115k + tax

4. **Checkout:**
   - Enter customer name (optional)
   - Select payment method: QRIS
   - Review order summary
   - Click "Pay Now"

5. **Payment:**
   - Display QRIS QR code
   - Show order details
   - Wait for payment confirmation
   - Auto-redirect on success

6. **Receipt:**
   - Show order group number: GRP-20260107-ABCD
   - Display 2 separate orders:
     * Order 1: Chicken Sumo (ORD-20260107-XYZ1)
     * Order 2: Magic Pizza (ORD-20260107-XYZ2)
   - Print receipt button
   - "Start New Order" button

### Kitchen Display Setup

1. **Kitchen Login:**
   - Navigate to: `http://localhost:5174/kitchen/login`
   - Select store: Yogya Kapatihan
   - Select brand: Chicken Sumo
   - Enter PIN (optional)
   - Save configuration

2. **Kitchen Display:**
   - Opens full-screen kitchen display
   - Shows 3 columns: Pending, Preparing, Ready
   - Receives orders for Chicken Sumo only
   - Audio alert on new order

3. **Order Flow:**
   - New order appears in "Pending"
   - Click "Start" → moves to "Preparing"
   - Check off items as completed
   - Click "Mark Ready" → moves to "Ready"
   - Customer notified
   - Auto-archive after 10 minutes

---

## 🔧 Admin Panel

### Store Management
```
Admin → Stores → Add New Store

Fields:
- Tenant: YOGYA (dropdown)
- Code: YOGYA-KAPATIHAN (unique)
- Name: Yogya Kapatihan
- Address: Jl. Ahmad Yani No. 288, Kapatihan
- City: Bandung
- Province: Jawa Barat
- Postal Code: 40271
- Latitude/Longitude: Geo coordinates

Actions:
- Regenerate QR Code for kiosk setup
- View Outlets/Brands at this store
- View Order Groups for this store
- Analytics: Revenue, orders, popular products
```

### Outlet/Brand Management
```
Admin → Outlets → Add New Outlet

Fields:
- Tenant: YOGYA (dropdown)
- Brand Name: Chicken Sumo
- Phone: 0812-3456-7890 (optional)
- Email: info@chickensumo.com (optional)
- WebSocket URL: ws://localhost:3001 (kitchen sync)
- Is Active: ✅

Actions:
- Assign to Stores (Many-to-Many)
- Manage Products for this brand
- View all Orders across all stores
- Global Kitchen Display Configuration

Note: Outlet is now GLOBAL per tenant, not per store
```

### Store-Outlet Assignment (NEW)
```
Admin → Stores → Yogya Kapatihan → Manage Brands

OR

Admin → Store-Outlets → Add Brand to Store

Fields:
- Store: Yogya Kapatihan (dropdown)
- Outlet/Brand: Chicken Sumo (dropdown - from available brands)
- Is Active: ✅
- Display Order: 1 (for sorting in kiosk)
- Custom Opening Time: (optional override store hours)
- Custom Closing Time: (optional override store hours)

Available Brands to Add:
- Shows only brands not yet assigned to this store
- Prevents duplicate assignments

Current Brands at Store:
1. Chicken Sumo (Active, Order: 1)
2. Magic Oven (Active, Order: 2)
3. Magic Pizza (Inactive, Order: 3)

Actions:
- Activate/Deactivate brand at store
- Change display order
- Remove brand from store
```

### Category & Product Management (Per Brand)
```
Admin → Outlets → Chicken Sumo → Menu Management

Categories Section:
- Add Category: Name, Description, Sort Order, Kitchen Station
- Example:
  * Fried Chicken (station: MAIN)
  * Combos (station: MAIN)
  * Drinks (station: BEVERAGE)
  
Products Section (filtered by category):
- Add Product: Name, SKU, Price, Category, Image
- Modifiers: Size, Toppings, Spicy Level
- Stock tracking (optional)
- Kitchen routing (auto from category or override)

Example for Chicken Sumo:
📦 Fried Chicken Category
  - Chicken Sumo Original (Rp 25,000)
  - Chicken Sumo Spicy (Rp 27,000)
  - Chicken Wings 5pcs (Rp 20,000)

📦 Combos Category
  - Chicken Combo + Fries + Drink (Rp 35,000)
  - Family Meal 8pcs (Rp 85,000)

🥤 Drinks Category
  - Iced Tea (Rp 5,000)
  - Orange Juice (Rp 8,000)

Note: Each brand (outlet) manages own menu independently
```

### Order Group Management
```
Admin → Order Groups

Filters:
- Store: All / YOGYA-KAPATIHAN / etc.
- Payment Status: All / Unpaid / Paid / Refunded
- Date Range: Today / This Week / Custom
- Search: Group number, customer name

List View:
- Group Number: GRP-20260107-ABCD
- Store: Yogya Kapatihan
- Brands: Chicken Sumo, Magic Pizza (2 outlets)
- Items: 4 items
- Total: Rp 165,000
- Payment: QRIS (Paid)
- Status: Completed
- Created: 2026-01-07 10:30

Detail View:
- Full customer information
- Payment details & receipt
- Individual orders breakdown:
  * Order 1: Chicken Sumo - Rp 85,000
  * Order 2: Magic Pizza - Rp 80,000
- Kitchen status per order
- Timeline: Ordered → Preparing → Ready → Completed
- Refund option (if applicable)
```

---

## ✅ Checklist for Implementation

### Backend Refactoring (Many-to-Many) 🔄
- [ ] Update Outlet model (remove store FK, opening_time, closing_time, address fields)
- [ ] Update Store model (add opening_time, closing_time)
- [ ] Create StoreOutlet model (junction table with unique_together constraint)
- [ ] Update Category model (change tenant FK to outlet FK)
- [ ] Update Product model (change tenant FK to outlet FK)
- [ ] Update ProductModifier model (add outlet FK for global modifiers)
- [ ] Update KitchenStation model (confirm outlet FK, not store FK)
- [ ] Create migration (data migration from old to new structure)
- [ ] Update serializers (all affected models)
- [ ] Update API endpoints to query via junction table and outlet-based menu
- [ ] Rewrite sample data script (global brands, outlet-based menus, kitchen stations per brand)
- [ ] Update Order model to include store FK

### Backend APIs ✅ (Need update for M2M)
- [x] Location → Store model rename
- [x] OrderGroup model & migration
- [ ] Update outlets API to use StoreOutlet junction
- [x] Update Order with order_group field
- [x] Store API endpoints
- [x] OrderGroup API endpoints
- [x] Serializers for Store & OrderGroup
- [x] URL routing
- [ ] Update to StoreOutlet junction queries

### Frontend Admin Panel 🔄
- [x] Tenants page (completed)
- [x] Stores page (completed with filters and alerts)
- [ ] Update Outlets page (manage global brands without store FK)
- [ ] Add Categories management per outlet (menu structure per brand)
- [ ] Add Products management per outlet (menu items per brand)
- [ ] Add StoreOutlet management page (brand-to-store assignment)
- [ ] Add brand assignment UI in store detail page

### Frontend Kiosk ✅
- [x] Kiosk store (config & multi-cart)
- [x] KioskSetup component
- [x] OutletSelection component
- [x] MultiCart component
- [x] Checkout/Payment component
- [x] Receipt component (with X-Tenant-ID header)
- [x] Kiosk main page routing

### Testing 🔄
- [ ] Create test locations
- [ ] Create test outlets with location
- [ ] Test kiosk setup flow
- [ ] Test multi-outlet cart
- [ ] Test order group creation
- [ ] Test payment flow
- [ ] Test kitchen display routing

---

## �️ COMPLETE ROADMAP - KIOSK & KITCHEN IMPLEMENTATION

### 🎯 Phase 1: Backend Foundation ✅ COMPLETE
**Status:** 100% Complete - Many-to-Many Architecture Implemented
**Duration:** Week 1-2
**Completed:** January 8, 2026

- [x] **Database Refactoring (OPSI 2 - Many-to-Many)** ✅
  - [x] Remove store FK from Outlet (brands are global)
  - [x] Remove opening_time/closing_time/address from Outlet
  - [x] Add opening_time/closing_time to Store
  - [x] Create StoreOutlet junction table (M2M with unique constraint)
  - [x] Move Category from Tenant to Outlet (menu per brand)
  - [x] Move Product from Tenant to Outlet (menu per brand)
  - [x] Update ProductModifier with outlet FK (global modifiers)
  - [x] Add store FK to Order model (kitchen routing)
  - [x] Verify KitchenStation has outlet FK (confirmed)

- [x] **Django Migrations** ✅
  - [x] `tenants.0014_storeoutlet_alter_outlet_options_and_more`
  - [x] `orders.0007_order_store`
  - [x] `products.0007_alter_category_options_alter_product_options_and_more`
  - [x] All migrations created and ready to apply

- [x] **Sample Data Script** ✅
  - [x] Create 4 tenants (YOGYA, BORMA, MATAHARI, CARREFOUR)
  - [x] Create 12 stores with opening hours (3 per tenant)
  - [x] Create 3 global brands (Chicken Sumo, Magic Oven, Magic Pizza)
  - [x] Create 30 StoreOutlet entries (M2M links)
  - [x] Create 9 categories (3 per brand)
  - [x] Create 27 products (9 per brand)
  - [x] Create 6 kitchen stations (2 per brand)
  - [x] Script: `setup_complete_test_data.py` - COMPLETE
  - [x] BAT script: `setup_multi_outlet_test_docker.bat` - Updated

- [x] **Admin Panel Updates** ✅
  - [x] Store admin with operating hours
  - [x] Outlet admin (global brands)
  - [x] StoreOutlet admin (junction table management)
  - [x] Fixed field references for new model structure

- [ ] **API Endpoints (Need Update)** 🔄 NEXT PRIORITY
  - [x] `/api/public/stores/` - List all stores
  - [x] `/api/public/stores/{code}/validate/` - Validate store code
  - [ ] `/api/public/stores/{code}/outlets/` - Update to query via StoreOutlet
  - [ ] `/api/public/stores/{code}/products/` - Get all products at store (NEW)
  - [ ] `/api/public/outlets/{id}/categories/` - Get categories per brand (NEW)
  - [ ] `/api/public/outlets/{id}/products/` - Get products per brand (NEW)
  - [x] `/api/public/stores/by-qr/{qr_code}/` - QR code lookup
  - [x] `/api/public/order-groups/` - Create multi-outlet order

**Verification:** ✅ COMPLETED
```bash
# Test data - WORKING
.\setup_multi_outlet_test_docker.bat
# OR
docker-compose exec backend python setup_complete_test_data.py

# Results:
# - 4 Tenants created
# - 12 Stores with operating hours
# - 3 Global Brands (Outlets)
# - 30 Store-Brand Assignments (M2M)
# - 6 Kitchen Stations
# - 9 Categories
# - 27 Products

# Test Store Codes:
# YOGYA-KAPATIHAN, YOGYA-RIAU, YOGYA-SUNDA
# BORMA-DAGO, BORMA-CIBIRU, BORMA-KEBON-WARU
# MATAHARI-BIP, MATAHARI-TSM, MATAHARI-PVJ
# CARREFOUR-CIHAMPELAS, CARREFOUR-FESTIVAL, CARREFOUR-PASTEUR

# Verify structure (NEEDS SERIALIZER UPDATE)
# curl http://localhost:8000/api/public/stores/YOGYA-KAPATIHAN/outlets/
```

---

### 📱 Phase 2: Kiosk Frontend ✅ COMPLETE
**Status:** 100% Complete
**Duration:** Week 3-4
**Priority:** HIGH
**Completed:** January 8, 2026

#### 2.1 Update Existing Components (Week 3) ✅ COMPLETE
- [x] **Update kioskStore.ts** ✅
  - [x] Change `locationCode` → `storeCode`
  - [x] Change `locationName` → `storeName`
  - [x] Change `locationId` → `storeId`
  - [x] Added `tenantName` field
  - [x] Renamed `setLocation()` → `setStore()`
  - [x] Update `getCheckoutData()` to use `store_id`
  - [x] Update types/interfaces

- [x] **Update KioskSetup.svelte** ✅
  - [x] Update placeholder text: "Enter Store Code (e.g., YOGYA-KAPATIHAN)"
  - [x] Update validation API call to `/api/public/stores/{code}/validate/`
  - [x] Display tenant name + store name
  - [x] Updated all UI text (store instead of location)
  - [x] Updated function names and variables

- [x] **Update OutletSelection.svelte** ✅
  - [x] Fetch outlets from `/api/public/stores/{code}/outlets/`
  - [x] Display brand cards with tenant branding
  - [x] Show brand_name prominently (switched h3 from tenant to brand)
  - [x] Cart badge per outlet already implemented
  - [x] Header shows tenant + store name context

- [x] **Verify MultiCart.svelte** ✅
  - [x] Already groups items by brand/outlet
  - [x] Already displays store context via tenantName
  - [x] Already shows breakdown per brand
  - [x] Total calculation already correct
  - [x] Clear outlet functionality already exists
  
**📄 See:** `PHASE2_UPDATE_LOG.md` for detailed changes

#### 2.2 New Kiosk Pages (Week 4) ✅ COMPLETE
- [x] **Product Browse Page** (`/kiosk/products` - Main shopping page)
  - [x] Load ALL products from ALL brands at store
  - [x] Display product grid with brand badges
  - [x] Filter by brand (multi-select)
  - [x] Filter by category
  - [x] Search by product name
  - [x] Product detail modal with modifiers
  - [x] Add to cart (auto-group by brand)
  - [x] Quantity selector
  - [x] Cart badge showing total items
  - [x] **Responsive Design:**
    - [x] Full-width product images within cards
    - [x] Grid: 1 col (mobile), 2-3 cols (tablet), 3-4 cols (desktop)
    - [x] Touch-friendly controls (44px min)
    - [x] Adaptive layouts for all screen sizes
    - [x] Single app for mobile/iPad/desktop

- [x] **Cart Page** (`/kiosk/cart`)
  - [x] Uses MultiCart.svelte component
  - [x] Groups items by brand/outlet
  - [x] Shows total per brand
  - [x] Grand total calculation
  - [x] Remove items functionality
  - [x] Clear entire brand cart
  - [x] Proceed to checkout button

- [x] **Checkout Page** (`/kiosk/checkout`)
  - [x] Review multi-brand cart
  - [x] Customer info form (name, phone, email)
  - [x] Payment method selection
    - [x] Cash
    - [x] Card
    - [x] QRIS
    - [x] E-Wallet (GoPay, OVO, Dana)
  - [x] Submit order to OrderGroup API
  - [x] Loading state & error handling
  - [x] Auto mark as paid (test mode)

- [x] **Receipt Page** (`/kiosk/success/[groupNumber]`) ✅ COMPLETE
  - [x] Display order group details
  - [x] Show breakdown per brand
  - [x] List all items with quantities
  - [x] Display totals (subtotal, tax, service, total)
  - [x] Show payment method & status
  - [x] Payment info with Grand Total section
  - [x] Print receipt button
  - [x] "Start New Order" button
  - [x] Auto-countdown to home (10 seconds)
  - [x] Fixed HTML structure errors (div closing tags)
  - [x] Added X-Tenant-ID header for API requests
  - [x] Fixed data mapping (location.name, customer.name, item.name, etc.)
  - [x] Proper {#each} loops for orders and items
  - [x] Verified Svelte compilation without errors

#### 2.3 Kiosk UX Enhancements ✅ COMPLETE
- [x] **Idle Screen** (`/kiosk/idle`) ✅
  - [x] Attractive welcome screen
  - [x] Store name & brands showcase
  - [x] "Tap to Start" call-to-action
  - [x] Promotional carousel (4 slides with auto-rotate)
  - [x] Auto-detect inactivity (managed by sessionManager)

- [x] **Navigation & Flow** ✅
  - [x] Breadcrumb navigation (KioskHeader component)
  - [x] Back button with confirmation (if cart has items)
  - [x] Cart badge in header (always visible with count)
  - [x] Floating cart button (mobile: fixed bottom-right)
  - [x] Session timeout handling (15 minutes via sessionManager)
  - [x] Clear session on completion (event-based)

- [x] **Responsive Design (Critical)** ✅
  - [x] Mobile-first approach (320px - 480px)
  - [x] Tablet optimization (iPad: 768px - 1024px)
  - [x] Desktop support (1280px+)
  - [x] Product images: Full-width in cards (already implemented)
  - [x] Flexible grid layouts (CSS Grid/Flexbox)
  - [x] Touch and mouse input support
  - [x] Orientation support (portrait/landscape)
  - [x] Single codebase for all devices

- [x] **Accessibility** ✅
  - [x] Large touch targets (min 44px mobile, 60px kiosk - btn-touch, btn-kiosk-touch)
  - [x] High contrast mode (CSS prefers-contrast media query + .high-contrast class)
  - [x] Font size controls (font-size-small/normal/large/xlarge classes)
  - [x] Reduced motion support (prefers-reduced-motion)
  - [x] Focus-visible improvements (3px outline)
  - [x] Screen reader support (sr-only classes, aria-labels)
  - [ ] Voice feedback option (future)
  - [ ] Language selection (ID/EN - future)

**Testing Checklist:**
```
✅ Enter store code YOGYA-KAPATIHAN
✅ View 3 outlets: Chicken Sumo, Magic Oven, Magic Pizza
✅ Add items from Chicken Sumo
✅ Add items from Magic Pizza
✅ View multi-brand cart
✅ Proceed to checkout
✅ Complete payment (test mode)
✅ View receipt with 2 orders (fixed HTML structure)
✅ Receipt displays properly without undefined/RpNaN
✅ All receipt data fields mapped correctly (location, customer, items, totals)
□ Print/download receipt (button exists, print function needs testing)
□ Start new order (button exists, navigation needs testing)
```

---

### 🍳 Phase 3: Kitchen Display System (NEXT 🔜)
**Status:** 0% Complete
**Duration:** Week 5-7
**Priority:** HIGH

#### 3.1 Backend - Kitchen APIs (Week 5) ✅ COMPLETE
- [x] **Kitchen Station Setup** ✅
  - [x] Link KitchenStation to Outlet/Brand (already exists)
  - [x] Station types: MAIN, GRILL, FRY, BEVERAGE, DESSERT (KitchenStationType model)
  - [ ] Auto-assign products to stations by category (future)
  - [ ] Override mechanism per product (future)

- [x] **Kitchen Order APIs** ✅
  - [x] `GET /api/kitchen/orders/pending/` - New orders waiting
  - [x] `GET /api/kitchen/orders/preparing/` - In progress
  - [x] `GET /api/kitchen/orders/ready/` - Completed orders
  - [x] `POST /api/kitchen/orders/{id}/start/` - Start preparing (pending → preparing)
  - [x] `POST /api/kitchen/orders/{id}/complete/` - Mark ready (preparing → ready)
  - [x] `POST /api/kitchen/orders/{id}/serve/` - Mark served (ready → served)
  - [x] `POST /api/kitchen/orders/{id}/cancel/` - Cancel order
  - [x] `GET /api/kitchen/orders/stats/` - Kitchen statistics
  - [x] Filter by outlet/brand, store, status
  - [x] Wait time calculation & urgent detection (>15 min)
  - [x] Today-only filter (default)

- [ ] **Socket.IO Real-time Communication** (Phase 3.3 - NEXT 🔜)
  - [ ] Socket.IO server on port 3001 (local-sync-server)
  - [ ] Push new orders to kitchen displays
  - [ ] Broadcast status changes
  - [ ] Audio notification on new order
  - [ ] Room-based connection per outlet/brand
  - [ ] Auto-reconnect with exponential backoff
  - [ ] Fallback to HTTP polling if WebSocket unavailable
  - [ ] Connection URL: `http://localhost:3001` or `http://192.168.1.10:3001`
  - [ ] TODO: Integrate with views_kitchen.py emit_order_update()

#### 3.2 Kitchen Display Frontend (Week 6-7)
**Status:** ✅ COMPLETE (January 8, 2026 - Accelerated)
**Testing:** ✅ All features tested and working

- ✅ **Kitchen Login** (`/kitchen/login`)
  - ✅ Select store (YOGYA-KAPATIHAN)
  - ✅ Select outlet/brand (Chicken Sumo)
  - ✅ Fixed pagination handling for stores/outlets API
  - 🔄 Optional: PIN authentication (Future enhancement)
  - ✅ Save to localStorage (kitchenConfig store)
  - ✅ Auto-reconnect on refresh (isKitchenConfigured check)

- ✅ **Main Kitchen Display** (`/kitchen/display`)
  - ✅ **Pending Orders Column**
    - ✅ New orders queue from `/api/kitchen/orders/pending/`
    - ✅ Order number, time, items with modifiers
    - ✅ Visual/audio alert for new orders (Web Audio API beep)
    - ✅ "Start Preparing" button (calls `/api/kitchen/orders/{id}/start/`)
    - ✅ Priority indicator (urgent red border if >15min wait time)
    - ✅ HTTP Polling (10-second interval)
    - ✅ Sound notifications working
  
  - ✅ **Preparing Orders Column**
    - ✅ Active orders in progress from `/api/kitchen/orders/preparing/`
    - ✅ Timer per order (wait_time updates every minute)
    - ✅ Item list with quantities and modifiers
    - ✅ "Mark Ready" button (calls `/api/kitchen/orders/{id}/complete/`)
    - ✅ Status updates working correctly
  
  - ✅ **Ready Orders Column**
    - ✅ Completed orders waiting pickup from `/api/kitchen/orders/ready/`
    - ✅ Order number prominent display
    - ✅ Green border visual indicator
    - ✅ "Serve Order" button (calls `/api/kitchen/orders/{id}/serve/`)
    - 🔄 Customer notification sent (Future: Socket.IO integration)


- ✅ **Kitchen Display Features**
  - ✅ Large, readable fonts (for distance viewing)
  - ✅ Color coding: Red (urgent), Blue (normal), Green (ready)
  - ✅ Source badge display: 🖥️ Kiosk / 🌐 Online Order
  - ✅ Sound toggle (via localStorage)
  - ✅ Statistics panel: Pending, preparing, ready, completed today counts
  - ✅ Logout functionality
  - 🔄 Full-screen mode (Future enhancement)
  - 🔄 Drag & drop between columns (Future enhancement)

- [ ] **Order Detail Modal**
  - [ ] Full order information
  - [ ] Item quantities & modifiers
  - [ ] Special instructions/notes
  - [ ] Customer name/number
  - [ ] Order group context (multi-brand orders)
  - [ ] Edit preparation time
  - [ ] Add internal notes

#### 3.3 Kitchen Management (Week 7)
- [ ] **Kitchen Admin** (`/admin/kitchen`)
  - [ ] Station configuration
  - [ ] Product-to-station mapping
  - [ ] Operating hours per station
  - [ ] Performance analytics
  - [ ] Order history & reports

- [ ] **Multi-Station Setup**
  - [ ] Support multiple stations per brand
  - [ ] Route items to correct station
  - [ ] Consolidate ready items before customer notification

**Kitchen Display Testing:**
```
✅ Login to Chicken Sumo kitchen
✅ Receive new order from kiosk
✅ Hear audio notification
✅ View order details (fixed undefined badge)
✅ Start preparing order
✅ Move to preparing column
✅ Mark order as ready
✅ Verify order in ready column
✅ Serve order (moves to served status)
✅ HTTP Polling works (10s interval)
✅ Sound notifications work
✅ Wait time calculation working
✅ Urgent indicator (>15min) working
```

**Known Issues Fixed:**
- ✅ Order status not 'pending' after payment → Fixed `mark_as_paid()` in models.py
- ✅ Orders not appearing in Kitchen Display → Fixed status='pending' instead of 'confirmed'
- ✅ Undefined badge in order card → Fixed to show source (Kiosk/Web)
- ✅ Login page pagination error → Fixed to handle paginated API response

---

### 📊 Phase 4: Admin Dashboard (FUTURE 📅)
**Status:** 0% Complete
**Duration:** Week 8-10
**Priority:** MEDIUM

#### 4.1 Store Management
- [ ] **Store CRUD** (`/admin/stores`)
  - [ ] List all stores with search/filter
  - [ ] Create new store
  - [ ] Edit store details
  - [ ] Deactivate/delete store
  - [ ] Generate QR code for kiosk setup
  - [ ] View outlets at store
  - [ ] Analytics: orders, revenue per store

#### 4.2 Outlet/Brand Management
- [ ] **Outlet CRUD** (`/admin/outlets`)
  - [ ] List outlets with store grouping
  - [ ] Create new outlet/brand
  - [ ] Assign to store
  - [ ] Update operating hours
  - [ ] Activate/deactivate
  - [ ] Kitchen station assignment
  - [ ] Product catalog management

#### 4.3 Order Management
- [ ] **OrderGroup List** (`/admin/order-groups`)
  - [ ] View all order groups
  - [ ] Filter: store, date, status, payment method
  - [ ] Search by group number, customer
  - [ ] Export to CSV/Excel
  - [ ] Refund management
  - [ ] View individual orders in group

- [ ] **Order Detail View**
  - [ ] Full order information
  - [ ] Customer details
  - [ ] Payment information
  - [ ] Kitchen status tracking
  - [ ] Timeline: ordered → preparing → ready
  - [ ] Print receipt reprint

#### 4.4 Analytics & Reports
- [ ] **Dashboard Overview**
  - [ ] Today's revenue (total & per store)
  - [ ] Orders count (completed, pending, cancelled)
  - [ ] Average order value
  - [ ] Top-selling products
  - [ ] Revenue by brand
  - [ ] Peak hours chart
  - [ ] Customer return rate

- [ ] **Detailed Reports**
  - [ ] Sales report (daily/weekly/monthly)
  - [ ] Product performance
  - [ ] Brand/outlet comparison
  - [ ] Kitchen efficiency: avg prep time
  - [ ] Payment method breakdown
  - [ ] Customer analytics
  - [ ] Export all reports

---

### 🔧 Phase 5: Advanced Features (FUTURE 📅)
**Status:** 0% Complete
**Duration:** Week 11-14
**Priority:** LOW

#### 5.1 Customer Features
- [ ] **Customer Account System**
  - [ ] Registration & login
  - [ ] Order history
  - [ ] Favorite items
  - [ ] Loyalty points
  - [ ] Saved payment methods
  - [ ] Delivery addresses

- [ ] **Mobile App Integration**
  - [ ] Pre-order from mobile
  - [ ] Pick up at kiosk/store
  - [ ] Order tracking
  - [ ] Push notifications

#### 5.2 Operational Features
- [ ] **Inventory Management**
  - [ ] Stock tracking per outlet
  - [ ] Low stock alerts
  - [ ] Auto-disable out-of-stock items
  - [ ] Purchase orders
  - [ ] Supplier management

- [ ] **Promotion Engine**
  - [ ] Discount codes
  - [ ] Buy X Get Y
  - [ ] Time-based promotions
  - [ ] Bundle deals
  - [ ] First-time customer offer

- [ ] **Multi-Language Support**
  - [ ] Indonesian (default)
  - [ ] English
  - [ ] Product translations
  - [ ] Dynamic language switching

#### 5.3 Integration & DevOps
- [ ] **Payment Gateway Integration**
  - [ ] Midtrans/Xendit integration
  - [ ] Real-time payment verification
  - [ ] Auto-mark paid on callback
  - [ ] Refund API integration

- [ ] **Printing Services**
  - [ ] Receipt printer integration
  - [ ] Kitchen order printer
  - [ ] Label printer for packaging
  - [ ] USB/Network printer support

- [ ] **Monitoring & Logging**
  - [ ] Error tracking (Sentry)
  - [ ] Performance monitoring
  - [ ] User behavior analytics
  - [ ] Audit logs
  - [ ] Uptime monitoring

---

### 📋 Priority Task List (Next 2 Weeks)

#### Week 3: Frontend Updates (Kiosk)
**Days 1-2:**
- [ ] Update kioskStore.ts (location → store)
- [ ] Fix all API endpoints
- [ ] Update types/interfaces

**Days 3-4:**
- [ ] Update KioskSetup.svelte
- [ ] Update OutletSelection.svelte
- [ ] Test store code validation

**Day 5:**
- [ ] Update MultiCart.svelte
- [ ] Test multi-brand cart flow

#### Week 4: New Kiosk Pages
**Days 1-2:**
- [ ] Create Product Browse page
- [ ] Implement add to cart
- [ ] Test product selection

**Days 3-4:**
- [ ] Create Checkout page
- [ ] Implement payment method selection
- [ ] Test order creation API

**Day 5:**
- [ ] Create Receipt page
- [ ] Test complete kiosk flow
- [ ] Bug fixes & polish

---

### 🎯 Success Metrics

#### Kiosk Performance:
- ✅ Setup time: < 2 minutes (admin)
- ✅ Order completion: < 3 minutes (customer)
- ✅ Cart abandonment: < 10%
- ✅ Payment success rate: > 95%
- ✅ System uptime: 99.9%

#### Kitchen Performance:
- ✅ Order acknowledgment: < 30 seconds
- ✅ Average prep time: Display on screen
- ✅ Order accuracy: > 98%
- ✅ Ready notification: Instant
- ✅ Customer pickup time: < 2 minutes

#### Business Metrics:
- ✅ Orders per day per store: Track
- ✅ Revenue per brand: Track
- ✅ Average order value: Track
- ✅ Customer satisfaction: > 4.5/5
- ✅ Staff efficiency: Track prep times

---

### 🚀 Quick Start Guide

#### For Developers:
```bash
# 1. Run sample data script
docker-compose exec backend python setup_complete_test_data.py

# 2. Verify data
docker-compose exec backend python manage.py shell -c "
from apps.tenants.models import Tenant, Store, Outlet
print(f'Tenants: {Tenant.objects.count()}')
print(f'Stores: {Store.objects.count()}')
print(f'Outlets: {Outlet.objects.count()}')
"

# 3. Test API
curl http://localhost:8000/api/public/stores/YOGYA-KAPATIHAN/outlets/

# 4. Start frontend
cd frontend
npm run dev
# Visit: http://localhost:5174/kiosk
```

#### For Testing:
1. **Kiosk Setup:**
   - Enter code: `YOGYA-KAPATIHAN`
   - Verify: Shows Yogya Kapatihan with 3 brands

2. **Order Flow:**
   - Select: Chicken Sumo
   - Add: 2x Chicken Sumo Original (25k each)
   - Select: Magic Pizza
   - Add: 1x Margherita Pizza (65k)
   - Cart total: Should show 115k + taxes

3. **Kitchen Display:**
   - Login: Chicken Sumo kitchen
   - Receive: Order with 2x Chicken Sumo Original
   - Login: Magic Pizza kitchen (separate tab)
   - Receive: Order with 1x Margherita Pizza

---

### 📞 Support & Documentation

**Documentation:**
- Backend API: `http://localhost:8000/api/docs/`
- Database Schema: See models in `backend/apps/`
- Sample Data: `backend/setup_complete_test_data.py`

**Database Tables:**
- `tenants` - Retail companies (YOGYA, BORMA, etc.)
- `stores` - Physical retail locations
- `outlets` - Brands at stores
- `order_groups` - Multi-brand order groups
- `orders` - Individual brand orders
- `kitchen_stations` - Kitchen stations per outlet

**Useful Commands:**
```bash
# Reset and regenerate all data
docker-compose exec backend python setup_complete_test_data.py

# Check specific store
docker-compose exec backend python manage.py shell -c "
from apps.tenants.models import Store
store = Store.objects.get(code='YOGYA-KAPATIHAN')
print(f'Store: {store.name}')
print(f'Tenant: {store.tenant.name}')
print(f'Outlets: {store.outlets.count()}')
[print(f'  - {o.brand_name}') for o in store.outlets.all()]
"

# View recent orders
docker-compose exec backend python manage.py shell -c "
from apps.orders.models import OrderGroup
groups = OrderGroup.objects.order_by('-created_at')[:5]
[print(f'{g.group_number}: {g.store.name} - Rp {g.total_amount}') for g in groups]
"
```

---

## 🎉 Project Status Summary

| Component | Status | Progress | Priority |
|-----------|--------|----------|----------|
| **Backend Models** | ✅ Complete | 100% | - |
| **Sample Data** | ✅ Complete | 100% | - |
| **Backend API/Serializers** | 🔄 In Progress | 0% | 🔴 CRITICAL |
| **Kiosk Frontend** | 📅 Blocked | 80% | 🔴 HIGH |
| **Kitchen Display** | 📅 Planned | 0% | 🔴 HIGH |
| **Admin Dashboard** | 📅 Planned | 0% | 🟡 MEDIUM |
| **Advanced Features** | 📅 Future | 0% | 🟢 LOW |

**Current Focus:** API Serializers & Views Update (Phase 1.5)  
**Next Milestone:** Kiosk Frontend Updates (Phase 2)  
**After That:** Kitchen Display System (Phase 3)  
**Target Launch:** Kitchen + Kiosk Full Integration (Week 7)

**Recent Completion (Jan 8, 2026):**
- ✅ Phase 1: Backend Foundation - Many-to-Many Architecture
- ✅ Database models refactored (Store, Outlet, StoreOutlet junction)
- ✅ Migrations created (tenants.0014, orders.0007, products.0007)
- ✅ Sample data script complete with 4 tenants, 12 stores, 3 brands
- ✅ Admin panel updated for new models

---

**Last Updated:** January 8, 2026  
**Version:** OPSI 2 - Many-to-Many Multi-Store Multi-Outlet Architecture  
**Repository:** kiosk-svelte
**Phase 1 Status:** ✅ COMPLETE (Backend Models & Sample Data)
