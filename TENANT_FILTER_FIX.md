# 🔧 TENANT FILTER NOT SHOWING - FIX

## ❌ Problem

Tenant filter tabs tidak muncul di kiosk, hanya category filter yang terlihat.

---

## 🔍 Root Causes

### 1. Condition: `tenants.length > 1` 
**Before**: Filter hanya muncul jika ada **2+ tenants**  
**Issue**: Jika cuma 1 tenant, filter tidak muncul  
**Fixed**: Changed to `tenants.length > 0`

### 2. Backend belum restart setelah update
Products di API mungkin belum ada `tenant_id`, `tenant_name`, `tenant_color`

### 3. Frontend belum di-reload
Old cached JavaScript di browser

---

## ✅ Fix Applied

### 1. Update Condition
```svelte
<!-- Before -->
{#if tenants.length > 1}
  <div class="tenant-filters">...</div>
{/if}

<!-- After -->
{#if tenants.length > 0}
  <div class="tenant-filters">...</div>
{/if}
```

### 2. Add Debug Logs
```javascript
console.log('✅ Products loaded:', products.length);
console.log('📦 First product:', products[0]);
console.log('Product: X, Tenant ID: X, Tenant Name: X');  // for each
console.log('✅ Tenants extracted:', tenants.length);
console.log('🏪 Tenants:', tenants);
```

---

## 🚀 Deploy Fix

```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
docker-compose restart frontend backend
```

Wait 15 seconds, then:

1. **Clear browser cache**: Ctrl+Shift+Delete or Cmd+Shift+Delete
2. **Hard reload**: Ctrl+F5 or Cmd+Shift+R
3. Open: http://localhost:5174/kiosk
4. **Open DevTools Console**: F12 → Console tab

---

## 🧪 Verification Steps

### Step 1: Check Backend API
```bash
curl http://localhost:8001/api/products/products/ | jq '.results[0] | {name, tenant_id, tenant_name, tenant_color}'

# Expected output:
{
  "name": "Nasi Goreng Spesial",
  "tenant_id": 1,
  "tenant_name": "Warung Makan Sedap",
  "tenant_color": "#FF6B35"
}
```

**If tenant_id is null or missing:**
→ Backend tidak di-restart atau serializer belum update  
→ Run: `docker-compose restart backend`

### Step 2: Check Frontend Console
Open browser DevTools (F12) → Console tab

**Expected logs:**
```
✅ Products loaded: 20
📦 First product: {id: 1, name: "...", tenant_id: 1, tenant_name: "...", ...}
Product: Nasi Goreng, Tenant ID: 1, Tenant Name: Warung Makan Sedap
Product: Mie Goreng, Tenant ID: 1, Tenant Name: Warung Makan Sedap
...
✅ Tenants extracted: 1
🏪 Tenants: [{id: 1, name: "Warung Makan Sedap", color: "#FF6B35"}]
```

**If logs show:**
- `tenant_id: undefined` → Backend issue
- `Tenants extracted: 0` → No tenant_id in products
- No logs at all → Frontend not loaded

### Step 3: Check UI
After fix, you should see:

```
┌────────────────────────────────────────┐
│ FILTER BY RESTAURANT:                  │
│ [All Restaurants] [Warung Makan Sedap] │
└────────────────────────────────────────┘
```

**If still not showing:**
- Check browser console for errors
- Try hard reload (Ctrl+F5)
- Check if `tenants.length > 0` in console: type `tenants` in console

---

## 🐛 Common Issues & Solutions

### Issue 1: Filter not showing
**Cause**: `tenants` array is empty  
**Check**: Console → type `tenants`  
**Fix**: Check backend API returns tenant info

### Issue 2: `tenant_id` is null
**Cause**: Backend serializer not updated  
**Fix**: 
```bash
docker-compose restart backend
# Wait 10 seconds
curl http://localhost:8001/api/products/products/
```

### Issue 3: Old cached frontend
**Cause**: Browser cache  
**Fix**: Hard reload (Ctrl+F5) or clear cache

### Issue 4: Backend not responding
**Cause**: Container not running  
**Fix**:
```bash
docker-compose ps
docker-compose restart backend
docker-compose logs backend --tail 20
```

---

## 📊 Debug Checklist

Run these in order:

- [ ] 1. Backend running: `docker-compose ps`
- [ ] 2. Backend API works: `curl http://localhost:8001/api/products/products/`
- [ ] 3. Products have tenant_id: Check curl output
- [ ] 4. Frontend loads: Open http://localhost:5174/kiosk
- [ ] 5. Console shows logs: F12 → Console tab
- [ ] 6. Tenants extracted: Check "Tenants extracted: X" log
- [ ] 7. Filter appears: Look for "FILTER BY RESTAURANT:" section

---

## 🔍 Manual Debug Commands

### Check if products have tenant info:
```bash
curl -s http://localhost:8001/api/products/products/ | \
  jq '.results[0] | {name, tenant_id, tenant_name, tenant_color}'
```

### Check tenant count in database:
```bash
docker-compose exec backend python manage.py shell << 'EOF'
from apps.tenants.models import Tenant
print(f"Tenants: {Tenant.objects.count()}")
for t in Tenant.objects.all():
    print(f"  - {t.id}: {t.name} ({t.primary_color})")
EOF
```

### Check products in database:
```bash
docker-compose exec backend python manage.py shell << 'EOF'
from apps.products.models import Product
products = Product.all_objects.select_related('tenant').all()[:5]
for p in products:
    print(f"{p.name} - Tenant: {p.tenant.name if p.tenant else 'None'}")
EOF
```

---

## ✅ Expected Result After Fix

### Backend API Response:
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "name": "Nasi Goreng Spesial",
      "tenant_id": 1,
      "tenant_name": "Warung Makan Sedap",
      "tenant_slug": "warung-makan-sedap",
      "tenant_color": "#FF6B35",
      ...
    }
  ]
}
```

### Frontend Console:
```
✅ Products loaded: 20
📦 First product: {id: 1, name: "Nasi Goreng Spesial", tenant_id: 1, ...}
Product: Nasi Goreng Spesial, Tenant ID: 1, Tenant Name: Warung Makan Sedap
Product: Mie Goreng, Tenant ID: 1, Tenant Name: Warung Makan Sedap
...
✅ Tenants extracted: 1
🏪 Tenants: [{id: 1, name: "Warung Makan Sedap", slug: "warung-makan-sedap", color: "#FF6B35"}]
```

### UI:
```
┌──────────────────────────────────────────────┐
│ 🍽️ Food Court Kiosk              🛒 Cart    │
├──────────────────────────────────────────────┤
│ FILTER BY RESTAURANT:                        │
│ [All Restaurants] [Warung Makan Sedap]       │
├──────────────────────────────────────────────┤
│ FILTER BY CATEGORY:                          │
│ [All Items] [Makanan Utama] [Minuman] ...    │
└──────────────────────────────────────────────┘
```

---

## 🚀 Quick Fix Commands

```bash
# 1. Pull latest code
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main

# 2. Restart services
docker-compose restart frontend backend

# 3. Wait and test
sleep 15
curl http://localhost:8001/api/health/

# 4. Open kiosk (hard reload)
# Browser: Ctrl+F5 on http://localhost:5174/kiosk
```

---

## 📝 Files Changed

- `frontend/src/routes/kiosk/+page.svelte` - Changed condition and added debug logs
- `debug_tenant_filter.sh` - Debug script (optional)

---

## 🎯 Success Criteria

After fix, you should have:

✅ Tenant filter section appears  
✅ Shows "All Restaurants" button  
✅ Shows tenant button(s) with correct name  
✅ Tenant buttons have colored borders  
✅ Console shows debug logs  
✅ Clicking tenant filters products  
✅ Products show tenant badge  

---

## 📞 Still Not Working?

If still having issues:

1. **Share console logs**: Copy all logs from console
2. **Share API response**: 
   ```bash
   curl http://localhost:8001/api/products/products/ > products.json
   ```
3. **Check backend logs**:
   ```bash
   docker-compose logs backend --tail 50
   ```

---

**GitHub**: https://github.com/dadinjaenudin/kiosk-svelte  
**Latest Commit**: e7ff78a  
**Status**: ✅ FIXED

**Silakan deploy dan check console logs! 🚀**
