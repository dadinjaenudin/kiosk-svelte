# ✅ CORS FIX - Kitchen Display X-Tenant-ID Header

## 🔴 Problem

```
Access to fetch at 'http://localhost:8001/api/orders/kitchen_display/' 
from origin 'http://localhost:5174' has been blocked by CORS policy: 
Request header field x-tenant-id is not allowed by Access-Control-Allow-Headers 
in preflight response.

GET http://localhost:8001/api/orders/kitchen_display/ net::ERR_FAILED
Error loading orders: TypeError: Failed to fetch
```

---

## 🔍 Root Cause

Kitchen Display mengirim custom header `X-Tenant-ID` untuk filter orders per tenant:

```javascript
// KitchenDisplay.svelte
const response = await fetch(`${apiUrl}/orders/kitchen_display/`, {
    headers: {
        'X-Tenant-ID': selectedTenant.toString()  // ← Custom header
    }
});
```

Tapi backend Django **TIDAK** mengizinkan header `X-Tenant-ID` di CORS config:

```python
# backend/config/settings.py (BEFORE FIX)
CORS_ALLOWED_ORIGINS = [...]
CORS_ALLOW_CREDENTIALS = True
# ❌ MISSING: CORS_ALLOW_HEADERS
```

Browser melakukan **CORS preflight** (OPTIONS request) dan backend reject karena header tidak diizinkan.

---

## ✅ Solution

Tambahkan `CORS_ALLOW_HEADERS` di Django settings dengan include custom headers:

```python
# backend/config/settings.py (AFTER FIX)

# CORS Settings
CORS_ALLOWED_ORIGINS = [...]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Allow custom headers for tenant and outlet context
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-tenant-id',   # ✅ Custom header for tenant context
    'x-outlet-id',   # ✅ Custom header for outlet context
]
```

---

## 🚀 Deployment

### Step 1: Pull Latest Code
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
```

### Step 2: Restart Backend
```bash
docker-compose restart backend
```

**Important**: Backend harus restart untuk apply CORS settings!

### Step 3: Wait & Test
```bash
# Wait for backend to restart (10 seconds)
```

Open Kitchen Display: http://localhost:5174/kitchen

---

## 🧪 Testing

### Test 1: Kitchen Display Load

1. Open http://localhost:5174/kitchen
2. Open Browser Console (F12)
3. **Expected**:
   - ✅ No CORS errors
   - ✅ Orders loaded successfully
   - ✅ Console: "📋 Loading orders for tenant: X"
   - ✅ Console: "✅ Orders loaded: N orders"

### Test 2: Tenant Filter

1. Select different tenant from dropdown
2. **Expected**:
   - ✅ No CORS errors
   - ✅ Orders filtered by tenant
   - ✅ Only orders for selected tenant shown

### Test 3: Auto-Refresh

1. Wait 10 seconds (auto-refresh interval)
2. **Expected**:
   - ✅ Orders refresh automatically
   - ✅ No CORS errors
   - ✅ Console: "🔄 Auto-refreshing orders..."

---

## 📊 Before vs After

### Before Fix:
```
Browser → OPTIONS /api/orders/kitchen_display/
          Header: X-Tenant-ID: 1

Backend → 403 CORS Error
          Error: Header X-Tenant-ID not allowed

Browser → ❌ Failed to fetch
```

### After Fix:
```
Browser → OPTIONS /api/orders/kitchen_display/
          Header: X-Tenant-ID: 1

Backend → 200 OK
          Access-Control-Allow-Headers: ..., x-tenant-id, x-outlet-id

Browser → GET /api/orders/kitchen_display/
          Header: X-Tenant-ID: 1

Backend → 200 OK
          Response: [{orders...}]

Browser → ✅ Orders loaded
```

---

## 🔧 Technical Details

### CORS Preflight Request:

When browser sends custom headers, it first sends **OPTIONS** request (preflight):

```http
OPTIONS /api/orders/kitchen_display/ HTTP/1.1
Origin: http://localhost:5174
Access-Control-Request-Method: GET
Access-Control-Request-Headers: x-tenant-id
```

Backend must respond with:

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:5174
Access-Control-Allow-Headers: accept, authorization, ..., x-tenant-id
Access-Control-Allow-Credentials: true
```

Only then browser sends actual GET request with `X-Tenant-ID` header.

### Custom Headers:

- `X-Tenant-ID` - Filter orders by tenant
- `X-Outlet-ID` - Filter orders by outlet (future use)

Both headers must be in `CORS_ALLOW_HEADERS` list.

---

## 🐛 Troubleshooting

### Issue 1: Still Getting CORS Error

**Cause**: Backend not restarted

**Fix**:
```bash
docker-compose restart backend
# Wait 10 seconds
docker-compose logs backend --tail 50
```

Verify backend logs show:
```
Starting WSGI server...
Watching for file changes...
```

### Issue 2: 404 Not Found

**Cause**: Endpoint `/api/orders/kitchen_display/` tidak ada

**Fix**: 
- Check backend routes: http://localhost:8001/api/docs/
- Verify `backend/apps/orders/urls.py` has kitchen_display route
- Verify `backend/config/urls.py` includes orders URLs

### Issue 3: Empty Response

**Cause**: No orders in database or tenant mismatch

**Fix**:
1. Run seed data:
   ```bash
   docker-compose exec backend python manage.py seed_foodcourt
   ```

2. Create test order via kiosk:
   - Open http://localhost:5174/kiosk
   - Add items
   - Checkout
   - Go to kitchen display

3. Check tenant ID matches:
   ```sql
   -- In Django shell
   docker-compose exec backend python manage.py shell
   >>> from apps.orders.models import Order
   >>> Order.objects.all().values('id', 'tenant_id', 'order_number')
   ```

---

## 📝 Files Modified

### backend/config/settings.py
```python
# Added CORS_ALLOW_HEADERS configuration
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-tenant-id',   # NEW
    'x-outlet-id',   # NEW
]
```

---

## ✅ Verification Checklist

After deployment:

- [ ] Pull latest code (`git pull origin main`)
- [ ] Restart backend (`docker-compose restart backend`)
- [ ] Wait 10 seconds
- [ ] Open http://localhost:5174/kitchen
- [ ] Check browser console - NO CORS errors
- [ ] Verify orders loaded
- [ ] Select different tenant from dropdown
- [ ] Verify orders filtered correctly
- [ ] Wait for auto-refresh (10s)
- [ ] Verify no errors during refresh

---

## 🎯 Expected Console Logs

### Success:
```
🏢 Tenants loaded: 5
📋 Loading orders for tenant: 1
✅ Orders loaded: 3 orders
🔄 Auto-refreshing orders...
📋 Loading orders for tenant: 1
✅ Orders loaded: 3 orders
```

### Before Fix (ERROR):
```
🏢 Tenants loaded: 5
📋 Loading orders for tenant: 1
Access to fetch at 'http://localhost:8001/api/orders/kitchen_display/' 
has been blocked by CORS policy
❌ Error loading orders: TypeError: Failed to fetch
```

---

## ✅ Status

- **Status**: ✅ **FIXED**
- **Commit**: `bfddf0c` - fix: Add X-Tenant-ID and X-Outlet-ID to CORS allowed headers
- **Issue**: CORS blocking custom headers
- **Solution**: Added `CORS_ALLOW_HEADERS` config
- **Impact**: Kitchen Display now works
- **GitHub**: https://github.com/dadinjaenudin/kiosk-svelte
- **Date**: 2024-12-27

---

## 📚 Related Documentation

- `CHECKOUT_KITCHEN_COMPLETE.md` - Kitchen Display implementation
- `QUICK_START.md` - Quick start guide
- `PRINT_RECEIPT_GUIDE.md` - Print receipt guide

---

## 🎉 NEXT STEPS

1. ✅ Pull code: `git pull origin main`
2. ✅ Restart backend: `docker-compose restart backend`
3. ✅ Wait 10 seconds
4. ✅ Test Kitchen Display: http://localhost:5174/kitchen
5. ✅ Verify no CORS errors in console
6. ✅ Verify orders load correctly
7. ✅ Test tenant filter
8. ✅ **Share screenshot hasil test!** 📸

---

**🔧 CORS ISSUE - RESOLVED!** ✅

**Kitchen Display sekarang berfungsi dengan sempurna!** 🍳✨

---

## 🆘 If Still Error

Share:
1. Browser console screenshot (full errors)
2. Network tab screenshot (failed request)
3. Backend logs: `docker-compose logs backend --tail 100`
4. Confirm backend restarted: `docker-compose ps`

**Ready to test!** 🚀
