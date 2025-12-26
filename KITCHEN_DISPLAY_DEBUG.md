# 🔍 Kitchen Display Debugging Guide

## 🔴 Issue: Orders tidak muncul di Kitchen Display setelah checkout

### Expected Behavior:
1. User checkout di kiosk
2. Order created dengan status `confirmed`
3. Order muncul di Kitchen Display
4. Auto-refresh every 5 seconds

### Current Behavior:
- ✅ Checkout berhasil
- ❌ Order **TIDAK** muncul di Kitchen Display
- Empty state: "Tidak Ada Pesanan"

---

## 🔍 Debugging Steps

### Step 1: Pull Latest Code (dengan enhanced logging)
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
docker-compose restart frontend
```

### Step 2: Complete Checkout & Monitor Logs

1. **Open Kiosk**: http://localhost:5174/kiosk
2. **Open Console** (F12)
3. **Add items** dari tenant (contoh: Warung Makan Sedap)
4. **Checkout** dengan Cash
5. **Check Console Logs**:

Expected logs setelah checkout:
```javascript
✅ Checkout successful: {orders: Array(1), ...}
📦 Orders created: [
  {
    order_number: "ORD-20251227-0001",
    tenant_id: 1,
    tenant_name: "Warung Makan Sedap",
    status: "confirmed",        // ← MUST BE "confirmed"
    payment_status: "paid",      // ← MUST BE "paid"
    items_count: 3
  }
]
```

**Important Fields**:
- ✅ `tenant_id`: Must match Kitchen Display tenant
- ✅ `status`: Must be `"confirmed"` (Kitchen Display filters: `confirmed`, `preparing`, `ready`)
- ✅ `payment_status`: Should be `"paid"`

### Step 3: Open Kitchen Display & Monitor Logs

1. **Open Kitchen Display**: http://localhost:5174/kitchen
2. **Select tenant**: Warung Makan Sedap
3. **Open Console** (F12)
4. **Check Console Logs**:

Expected logs:
```javascript
📋 Loading orders for tenant: 1 (Warung Makan Sedap)
📡 Response status: 200
✅ Orders loaded: {
  tenantName: "Warung Makan Sedap",
  tenantId: 1,
  orderCount: 1,           // ← Should be > 0
  orders: [
    {
      order_number: "ORD-20251227-0001",
      status: "confirmed",
      created_at: "2024-12-27T10:30:00Z",
      items_count: 3
    }
  ]
}
```

**If orderCount: 0** → Problem!

### Step 4: Verify Backend API Directly

Test API with curl:

```bash
curl -X GET "http://localhost:8001/api/orders/kitchen_display/" \
  -H "X-Tenant-ID: 1" \
  | jq '.'
```

Expected response:
```json
[
  {
    "id": 1,
    "order_number": "ORD-20251227-0001",
    "status": "confirmed",
    "tenant": {
      "id": 1,
      "name": "Warung Makan Sedap"
    },
    "items": [...]
  }
]
```

**If empty array `[]`** → Check database!

---

## 🔎 Common Issues & Solutions

### Issue 1: Tenant ID Mismatch

**Symptom**: 
- Checkout creates order with `tenant_id: 1`
- Kitchen Display filters by `tenant_id: 2`
- Result: No orders shown

**Diagnosis**:
```javascript
// Checkout logs:
📦 Orders created: [{ tenant_id: 1, ... }]

// Kitchen Display logs:
📋 Loading orders for tenant: 2  // ← MISMATCH!
✅ Orders loaded: { orderCount: 0 }
```

**Solution**: Ensure Kitchen Display selects **same tenant** as checkout.

---

### Issue 2: Order Status Not `confirmed`

**Symptom**:
- Order created but status is `pending` or `draft`
- Kitchen Display filters: `['confirmed', 'preparing', 'ready']`
- Result: Order tidak muncul

**Diagnosis**:
```javascript
// Checkout logs:
📦 Orders created: [{ status: "pending", ... }]  // ← WRONG STATUS!
```

**Expected**:
```javascript
📦 Orders created: [{ status: "confirmed", ... }]  // ← CORRECT
```

**Backend Code** (should be correct):
```python
# backend/apps/orders/views.py - Line 113
if payment_method == 'cash':
    for order in orders:
        order.status = 'confirmed'  # ✅ Set to confirmed
        order.save()
```

**Solution**: Verify backend code sets `status = 'confirmed'` after cash payment.

---

### Issue 3: Database Empty

**Symptom**: No orders in database

**Diagnosis**:
```bash
# Check database
docker-compose exec backend python manage.py shell

>>> from apps.orders.models import Order
>>> Order.objects.count()
0  # ← NO ORDERS!
```

**Solution**: Create order via kiosk checkout and verify:
```python
>>> Order.objects.count()
1  # ← Order created!

>>> order = Order.objects.first()
>>> print(order.order_number, order.status, order.tenant_id)
ORD-20251227-0001 confirmed 1
```

---

### Issue 4: CORS Error (Already Fixed)

**Symptom**:
```
CORS policy: Request header field x-tenant-id is not allowed
```

**Solution**: Already fixed in commit `bfddf0c`
- Added `X-Tenant-ID` to `CORS_ALLOW_HEADERS`
- Restart backend required

---

### Issue 5: Auto-Refresh Not Working

**Symptom**: Orders tidak update automatically

**Diagnosis**:
- Check console for refresh logs every 5 seconds:
```javascript
📋 Loading orders for tenant: 1  // ← Should appear every 5s
```

**Solution**: Verify `refreshInterval` is running:
```javascript
// KitchenDisplay.svelte - Line 26
refreshInterval = setInterval(loadOrders, 5000);  // ✅ 5 seconds
```

---

## 🧪 Complete Testing Flow

### Test 1: Single Tenant Order

1. **Kiosk**: Add 2 items from **Warung Makan Sedap** (tenant_id: 1)
2. **Checkout**: Cash payment
3. **Console**: Verify logs show `tenant_id: 1, status: "confirmed"`
4. **Kitchen Display**: Select **Warung Makan Sedap**
5. **Expected**: Order muncul dengan status "✓ Dikonfirmasi"

### Test 2: Multi-Tenant Orders

1. **Kiosk**: Add items from **3 different tenants**:
   - Warung Makan Sedap (tenant_id: 1)
   - Mie Ayam & Bakso (tenant_id: 2)
   - Ayam Geprek Mantap (tenant_id: 3)
2. **Checkout**: Cash payment
3. **Console**: Verify logs show **3 orders** created
4. **Kitchen Display**: 
   - Select **Warung Makan Sedap** → Show 1 order
   - Select **Mie Ayam & Bakso** → Show 1 order
   - Select **Ayam Geprek Mantap** → Show 1 order

### Test 3: Status Update

1. **Kitchen Display**: Click status button on order
2. **Change**: Confirmed → Preparing → Ready
3. **Expected**: 
   - Status updates immediately
   - Color changes
   - Icon changes
   - Sound plays

---

## 📊 Expected Console Output

### Kiosk (Checkout):
```
🛒 Cart items: (3) [{...}]
💳 Processing checkout: {items: Array(3), payment_method: "cash"}
✅ Checkout successful: {orders: Array(1), payments: Array(1), ...}
📦 Orders created: [{
  order_number: "ORD-20251227-0001",
  tenant_id: 1,
  tenant_name: "Warung Makan Sedap",
  status: "confirmed",
  payment_status: "paid",
  items_count: 3
}]
```

### Kitchen Display (Load):
```
🏢 Tenants loaded: 5
📋 Loading orders for tenant: 1 (Warung Makan Sedap)
📡 Response status: 200
✅ Orders loaded: {
  tenantName: "Warung Makan Sedap",
  tenantId: 1,
  orderCount: 1,
  orders: [{
    order_number: "ORD-20251227-0001",
    status: "confirmed",
    created_at: "2024-12-27T10:30:00.123456Z",
    items_count: 3
  }]
}
```

### Kitchen Display (Auto-Refresh - every 5s):
```
🔄 Auto-refreshing...
📋 Loading orders for tenant: 1 (Warung Makan Sedap)
📡 Response status: 200
✅ Orders loaded: { orderCount: 1, ... }
```

---

## 🔧 Backend Verification

### Check Orders in Database:

```bash
docker-compose exec backend python manage.py shell
```

```python
from apps.orders.models import Order
from apps.tenants.models import Tenant

# List all orders
orders = Order.objects.all()
for o in orders:
    print(f"{o.order_number} | Tenant: {o.tenant_id} ({o.tenant.name}) | Status: {o.status} | Items: {o.items.count()}")

# Check specific tenant orders
tenant_id = 1
orders = Order.objects.filter(tenant_id=tenant_id, status__in=['confirmed', 'preparing', 'ready'])
print(f"Orders for tenant {tenant_id}: {orders.count()}")
```

### Check Kitchen Display API:

```bash
# Test API endpoint
curl -X GET "http://localhost:8001/api/orders/kitchen_display/" \
  -H "X-Tenant-ID: 1" \
  -H "Content-Type: application/json" \
  | jq '.'
```

Expected:
```json
[
  {
    "id": 1,
    "order_number": "ORD-20251227-0001",
    "status": "confirmed",
    "tenant": {
      "id": 1,
      "name": "Warung Makan Sedap"
    },
    "items": [
      {
        "product_name": "Rendang Sapi",
        "quantity": 2
      }
    ]
  }
]
```

---

## 📝 Checklist untuk User

Setelah pull code, test dengan checklist ini:

### Kiosk:
- [ ] Open http://localhost:5174/kiosk
- [ ] Open Console (F12)
- [ ] Add 2-3 items dari satu tenant
- [ ] Checkout dengan Cash
- [ ] **Verify Console Log**: `📦 Orders created` dengan `tenant_id`, `status: "confirmed"`
- [ ] **Note**: `tenant_id` dan `order_number`

### Kitchen Display:
- [ ] Open http://localhost:5174/kitchen (new tab)
- [ ] Open Console (F12)
- [ ] Select **same tenant** dari checkout
- [ ] **Verify Console Log**: `✅ Orders loaded` dengan `orderCount > 0`
- [ ] **Verify UI**: Order muncul dengan order number yang sama
- [ ] Wait 5 seconds
- [ ] **Verify**: Console log `📋 Loading orders` (auto-refresh)

### If Orders NOT Showing:
- [ ] Share **both** console screenshots (Kiosk + Kitchen)
- [ ] Share tenant_id dari checkout
- [ ] Share tenant_id dari Kitchen Display
- [ ] Run curl command dan share output
- [ ] Check backend logs: `docker-compose logs backend --tail 100`

---

## ✅ Status

- **Status**: 🔍 **DEBUGGING MODE ACTIVE**
- **Commit**: `f16d31c` - debug: Add detailed logging for Kitchen Display
- **Enhanced Logging**:
  - ✅ Checkout logs order details
  - ✅ Kitchen Display logs API calls
  - ✅ Kitchen Display logs loaded orders
  - ✅ Console shows tenant_id, status, counts
- **GitHub**: https://github.com/dadinjaenudin/kiosk-svelte

---

## 🎯 NEXT STEPS

1. ✅ Pull latest code: `git pull origin main`
2. ✅ Restart frontend: `docker-compose restart frontend`
3. ✅ Test checkout dengan console open
4. ✅ Copy console logs dari **Kiosk**
5. ✅ Test Kitchen Display dengan console open
6. ✅ Copy console logs dari **Kitchen Display**
7. ✅ **Share BOTH console logs!** 📸

**Console logs akan menunjukkan exactly mana yang salah!** 🔍

---

## 🆘 Share These Details

Untuk troubleshoot lebih lanjut, share:

1. **Kiosk Console Logs** (full, dari checkout start sampai success)
2. **Kitchen Display Console Logs** (full, dari load tenants sampai load orders)
3. **Screenshot Kitchen Display UI** (showing "Tidak Ada Pesanan")
4. **Curl output** dari backend API test
5. **Backend logs** (optional): `docker-compose logs backend --tail 50`

**Dengan logs ini, kita bisa identify exact issue!** 🎯
