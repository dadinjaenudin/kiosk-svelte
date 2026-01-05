# Kitchen Station Type & Kitchen Station Relationship

## 📊 Hubungan Antar Komponen

```
┌─────────────────────────────────────────────────────────────────┐
│                    KITCHEN ROUTING SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

1️⃣ KITCHEN STATION TYPE (Master Data)
   ┌──────────────────────────────────────┐
   │ • Name: "Main Kitchen"                │
   │ • Code: "MAIN" ← KUNCI PENTING       │
   │ • Icon: 🍳                            │
   │ • Color: #FF6B35                      │
   │ • Global/Tenant-specific              │
   └──────────────────────────────────────┘
            ↓ digunakan oleh
            
2️⃣ KITCHEN STATION (Physical Station per Outlet)
   ┌──────────────────────────────────────┐
   │ • Name: "Main Kitchen"                │
   │ • Code: "MAIN" ← HARUS SAMA!         │
   │ • Outlet: Burger Station - Central   │
   └──────────────────────────────────────┘
            ↑ filter berdasarkan code
            
3️⃣ CATEGORY (Product Grouping)
   ┌──────────────────────────────────────┐
   │ • Name: "Burgers"                     │
   │ • kitchen_station_code: "MAIN"       │
   └──────────────────────────────────────┘
            ↓ mewariskan ke
            
4️⃣ PRODUCT
   ┌──────────────────────────────────────┐
   │ • Name: "Big Mac"                     │
   │ • Category: Burgers                   │
   │ • kitchen_station_code_override:      │
   │   null (optional override)            │
   │ • kitchen_station_code (property):    │
   │   → returns override OR category code │
   │   → "MAIN" from category              │
   └──────────────────────────────────────┘
            ↓ muncul di order
            
5️⃣ ORDER ITEM
   ┌──────────────────────────────────────┐
   │ • Product: "Big Mac"                  │
   │ • kitchen_station_code: "MAIN"       │
   │   (dari product property)             │
   └──────────────────────────────────────┘
            ↓ ditampilkan di
            
6️⃣ KITCHEN DISPLAY
   ┌──────────────────────────────────────┐
   │ Outlet: Burger Station - Central      │
   │ Station: Main Kitchen (code: MAIN)    │
   │                                        │
   │ Filter: WHERE code = "MAIN"           │
   │ ↓                                      │
   │ Shows: Big Mac order ✅               │
   └──────────────────────────────────────┘
```

## 🔑 Kenapa Code Harus Match?

### ❌ SALAH - Code Tidak Match
```
Kitchen Station Type:
  - Code: "MAIN"

Kitchen Station di Outlet A:
  - Code: "KITCHEN" ← BEDA!

Category Burgers:
  - kitchen_station_code: "MAIN"

Order Item (Big Mac):
  - kitchen_station_code: "MAIN"

Kitchen Display (Outlet A):
  - Filter: station.code = "KITCHEN"
  - Result: Order TIDAK MUNCUL ❌
```

### ✅ BENAR - Code Match
```
Kitchen Station Type:
  - Code: "MAIN"

Kitchen Station di Outlet A:
  - Code: "MAIN" ← SAMA!

Category Burgers:
  - kitchen_station_code: "MAIN"

Order Item (Big Mac):
  - kitchen_station_code: "MAIN"

Kitchen Display (Outlet A):
  - Filter: station.code = "MAIN"
  - Result: Order MUNCUL ✅
```

## 📝 Contoh Skenario

### Skenario 1: Food Court dengan 3 Station Types

**Kitchen Station Types (Global):**
1. MAIN - Main Kitchen 🍳
2. BEVERAGE - Beverage Station ☕
3. DESSERT - Dessert Station 🍰

**Outlet: Pizza Paradise**
- Station 1: Main Kitchen (code: MAIN)
- Station 2: Beverage Counter (code: BEVERAGE)
- Station 3: Dessert Bar (code: DESSERT)

**Categories:**
- Pizza → kitchen_station_code: MAIN
- Pasta → kitchen_station_code: MAIN
- Soft Drinks → kitchen_station_code: BEVERAGE
- Ice Cream → kitchen_station_code: DESSERT

**Routing:**
```
Order: 1x Margherita Pizza + 1x Coke + 1x Vanilla Ice Cream

Kitchen Display 1 (MAIN):
  ✅ Shows: Margherita Pizza

Kitchen Display 2 (BEVERAGE):
  ✅ Shows: Coke

Kitchen Display 3 (DESSERT):
  ✅ Shows: Vanilla Ice Cream
```

### Skenario 2: Tenant-Specific Station Types

**Pizza Paradise - Custom Types:**
1. PIZZA - Pizza Oven 🍕 (tenant-specific)
2. SIDES - Sides Station 🥖 (tenant-specific)

**Outlet: Pizza Paradise - Central**
- Station 1: Pizza Oven (code: PIZZA)
- Station 2: Sides Counter (code: SIDES)

**Categories:**
- Main Pizza → kitchen_station_code: PIZZA
- Appetizers → kitchen_station_code: SIDES

**Routing:**
```
Order: 1x Pepperoni Pizza + 1x Garlic Bread

Kitchen Display 1 (PIZZA):
  ✅ Shows: Pepperoni Pizza

Kitchen Display 2 (SIDES):
  ✅ Shows: Garlic Bread
```

## 🎨 UI Features & Implementation

### 1. Kitchen Station Types Management
**Location**: Admin Panel → System → Kitchen Station Types

**Grid Card Display:**
- Visual cards showing icon, name, code, and color badge
- Global indicator (🌐) for global types
- Active/Inactive status toggle
- Sort order for display priority

**Create/Edit Modal:**
- Icon picker with 20 emoji options (🍳☕🍰🍕🥗🍜🥤🍱🌮🍔🍟🥙🌭🥪🍝🍛🥘🍲🥟🧆)
- Color picker with hex input and live preview
- Global vs Tenant selector
- Name and Code validation (uppercase alphanumeric)
- Sort order management
- Active/Inactive toggle

**Delete Protection:**
- System checks if type is used by categories or products
- Shows error message with usage count if deletion blocked
- Prevents orphaned references

### 2. Kitchen Stations Management
**Location**: Admin Panel → System → Kitchen Stations

**Key Features:**
- Code dropdown (replaces text input for validation)
- Dropdown shows: icon + name + code for each type
- Visual indicators: icon and color-coded badges
- Helper text: "Must match Kitchen Station Type for routing to work"
- Station cards display type icon and color

**Benefits:**
- No more typos in station codes
- Guaranteed matching with station types
- Visual confirmation at a glance

### 3. Categories Management
**Location**: Admin Panel → Menu → Categories

**Kitchen Station Field:**
- Dropdown selector for kitchen_station_code
- Shows all active station types with icon + name + code
- Default value: MAIN
- Helper text: "Products in this category will route to this station type"

**Table Display:**
- Kitchen Station column with visual indicators
- Icon + color-coded badge for each category
- Quick identification of routing configuration

### 4. Products Management
**Location**: Admin Panel → Menu → Products

**Kitchen Station Override (Optional):**
- Dropdown with "Use category default" as first option
- Override selector for special routing needs
- Live preview showing effective routing code
- Visual indicator showing source:
  - "(From category)" - inherited from category
  - "(Override)" + ⚙️ - custom override set

**Table Display:**
- Kitchen Station column showing effective code
- Icon + color-coded badge
- ⚙️ gear icon if product uses override
- Tooltip on hover showing override status

**Use Cases for Override:**
- Special drinks that need beverage station despite being in food category
- Limited-time items with different preparation area
- Custom routing for specific products

## 🛠️ Setup Flow

### Step 1: Create Kitchen Station Types
```
Admin Panel → System → Kitchen Station Types → Add New

Create:
- Name: "Main Kitchen"
- Code: "MAIN" (uppercase, alphanumeric only)
- Icon: 🍳 (select from 20 emoji options)
- Color: #FF6B35 (color picker with live preview)
- Global: Yes (available to all tenants)
- Active: Yes
- Sort Order: 1

Features:
✅ Visual card display with icon, color, and code
✅ Create/Edit modal with icon picker and color selector
✅ Delete protection (can't delete if used by categories/products)
✅ Active/Inactive toggle
✅ Global vs Tenant-specific selection
```

### Step 2: Create Kitchen Stations per Outlet
```
Admin Panel → System → Kitchen Stations → Add New

Create:
- Outlet: Burger Station - Central (dropdown)
- Name: "Main Kitchen"
- Code: (dropdown) → Select "🍳 Main Kitchen (MAIN)"
  * Dropdown shows all active Kitchen Station Types
  * Visual: icon + name + code
  * Enforces code matching - no typos!
- Description: "Main cooking station"
- Active: Yes
- Sort Order: 1

Features:
✅ Code dropdown replaces text input
✅ Visual indicators with icon and color-coded badges
✅ Helper text: "Must match Kitchen Station Type for routing to work"
✅ Real-time validation
```

### Step 3: Assign Station Codes to Categories
```
Admin Panel → Menu → Categories → Edit Category

Edit Category "Burgers":
- Name: Burgers
- Description: Burger items
- Kitchen Station: (dropdown) → Select "🍳 Main Kitchen (MAIN)"
  * Shows: icon + name + code for each type
  * Helper text: "Products in this category will route to this station type"
  * Default: MAIN

Features:
✅ Kitchen Station dropdown with visual indicators
✅ Color-coded badge in table view (icon + code)
✅ Live preview of effective routing
✅ All products in category inherit this code
```

### Step 4: Products (Optional Override)
```
Admin Panel → Menu → Products → Edit Product

Option 1: Use Category Default (Recommended)
- Kitchen Station Override: "Use category default"
- Effective routing: Shows inherited code from category
- Visual indicator: "(From category)"

Option 2: Override for Specific Product
- Kitchen Station Override: (dropdown) → Select "☕ Beverage Station (BEVERAGE)"
- Effective routing: Shows override code
- Visual indicator: "(Override)" + ⚙️ icon
- Use case: Special routing for one product in category

Features:
✅ Optional override dropdown
✅ Live preview showing effective routing
✅ Visual feedback with icon + color
✅ Clear "Use category default" option
✅ Override indicator (⚙️) in products table
```

### Step 5: Orders Route Automatically
```
When customer orders:
1. Order created with item "Big Mac"
2. System reads: Product.kitchen_station_code property
   - Returns override if set
   - Otherwise returns category.kitchen_station_code
3. OrderItem.kitchen_station_code = "MAIN"
4. Kitchen Display filters: WHERE station.code = "MAIN"
5. Order appears in correct station display

No manual intervention required! ✨
```

## 🎯 Key Benefits

### 1. Consistency
- Station codes guaranteed to match station types
- No typos or manual errors
- Dropdown enforces valid codes only
- Visual confirmation with icon + color

### 2. Visual Feedback
- 🎨 Station cards show type icon and color
- 🏷️ Color-coded badges throughout UI
- 👁️ Easy to identify station type at a glance
- ⚙️ Override indicator for special routing
- 📊 Live preview of effective routing

### 3. Flexibility
- 🎯 Category-level defaults for bulk routing
- ⚙️ Product-level overrides for exceptions
- 🌐 Global types for common stations
- 🏢 Tenant-specific types for custom needs
- 🔄 Easy switching between inherited and override

### 4. Scalability
- ➕ Add new station type → immediately available in all dropdowns
- 🎨 Change type icon/color → all stations update visually
- 🏢 Tenant-specific types don't pollute other tenants
- 🔍 Filters automatically apply to new types

### 5. Routing Reliability
- ✅ Orders always route to correct stations
- 🚫 No "missing orders" due to code mismatches
- 👨‍🍳 Kitchen staff see exactly what they need to prepare
- 📍 Location-aware routing (per outlet)
- 🔄 Real-time updates across system

## ⚠️ Important Notes

1. **Code is Case-Sensitive**: "MAIN" ≠ "main"
2. **Code Must Be Unique**: Can't have two types with same code (global scope)
3. **Active Types Only**: Only active station types appear in dropdowns
4. **Can't Delete Used Types**: System prevents deletion if type code is in use by categories or products
5. **Dropdown Validation**: All code inputs use dropdowns to prevent typos
6. **Visual Indicators**: Icon and color help identify types at a glance
7. **Override Priority**: Product override takes precedence over category default
8. **Property vs Field**: 
   - `kitchen_station_code` = computed property (read-only)
   - `kitchen_station_code_override` = database field (writable)
9. **Inheritance**: Products without override inherit from category
10. **Real-time Updates**: Changes to station types reflect immediately in UI

## 🔍 Troubleshooting

### Orders not showing in Kitchen Display?
1. ✅ Check Kitchen Station code matches Station Type code
2. ✅ Check Category has correct kitchen_station_code
3. ✅ Check Product doesn't have wrong override
4. ✅ Check Station Type is active
5. ✅ Check Kitchen Station is active
6. ✅ Verify outlet assignment is correct
7. 🔍 Check console logs for routing information

### Station Type not appearing in dropdown?
1. ✅ Verify Station Type `is_active = True`
2. ✅ Check if global type or tenant matches current tenant
3. ✅ Reload page to fetch latest types
4. ✅ Check browser console for API errors
5. ✅ Verify user has proper permissions

### Product override not saving?
1. ✅ Check ProductAdminSerializer includes `kitchen_station_code_override`
2. ✅ Verify field is sent in form submit (check console logs)
3. ✅ Reload product to confirm value persisted
4. ✅ Check backend logs for validation errors
5. ✅ Ensure field allows null/blank values

### Visual indicators not showing?
1. ✅ Verify Station Types loaded (check stationTypes array)
2. ✅ Check getStationType() function returns correct type
3. ✅ Ensure station type has icon and color defined
4. ✅ Reload page to refresh station types cache
5. ✅ Check browser console for JavaScript errors

### Category changes not reflecting in products?
1. ⚠️ Product `kitchen_station_code` is computed property
2. ✅ Property reads from override OR category (priority to override)
3. ✅ If product has override, category change won't affect it
4. ✅ Remove override to use category default
5. ✅ Check product detail to see effective routing
