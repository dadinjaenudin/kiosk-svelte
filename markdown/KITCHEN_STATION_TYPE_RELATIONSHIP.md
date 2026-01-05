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
   │ • kitchen_station_code (property)     │
   │   → returns "MAIN" dari category      │
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

## 🛠️ Setup Flow

### Step 1: Create Kitchen Station Types
```
Admin Panel → System → Kitchen Station Types

Create:
- Name: "Main Kitchen"
- Code: "MAIN"
- Icon: 🍳
- Color: #FF6B35
- Global: Yes (available to all tenants)
```

### Step 2: Create Kitchen Stations per Outlet
```
Admin Panel → System → Kitchen Stations

Create:
- Outlet: Burger Station - Central
- Name: "Main Kitchen"
- Code: (dropdown) → Select "🍳 Main Kitchen (MAIN)"
```

### Step 3: Assign Station Codes to Categories
```
Admin Panel → Menu → Categories

Edit Category "Burgers":
- kitchen_station_code: (dropdown) → Select "MAIN"
```

### Step 4: Products Inherit Automatically
```
No action needed!
All products in "Burgers" category will automatically have:
  kitchen_station_code = "MAIN"
```

### Step 5: Orders Route Automatically
```
When customer orders:
1. Order created with item "Big Mac"
2. OrderItem.kitchen_station_code = "MAIN" (from product property)
3. Kitchen Display at Outlet with station.code = "MAIN" shows the order
```

## 🎯 Key Benefits

### 1. Consistency
- Station codes guaranteed to match station types
- No typos or manual errors
- Dropdown enforces valid codes only

### 2. Visual Feedback
- Station cards show type icon and color
- Easy to identify station type at a glance
- Color-coded badges for quick recognition

### 3. Scalability
- Add new station type → immediately available in all station forms
- Change type icon/color → all stations using that code update visually
- Tenant-specific types don't pollute other tenants

### 4. Routing Reliability
- Orders always route to correct stations
- No "missing orders" due to code mismatches
- Kitchen staff see exactly what they need to prepare

## ⚠️ Important Notes

1. **Code is Case-Sensitive**: "MAIN" ≠ "main"
2. **Code Must Be Unique**: Can't have two stations with same code in one outlet
3. **Active Types Only**: Only active station types appear in dropdown
4. **Can't Delete Used Types**: System prevents deletion if type code is in use

## 🔍 Troubleshooting

### Orders not showing in Kitchen Display?
1. Check Kitchen Station code matches Station Type code
2. Check Category has correct kitchen_station_code
3. Check Station Type is active
4. Check Kitchen Station is active

### Station Type not appearing in dropdown?
1. Verify Station Type is_active = True
2. Check if global type or tenant matches current tenant
3. Reload page to fetch latest types
