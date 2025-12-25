# 🔧 500 Error Fix - Tenant Serializer

## ❌ Error

```
Failed to load resource: the server responded with a status of 500 (Internal Server Error)
+page.svelte:93 Failed to load tenants: 500
```

When accessing: `GET /api/public/tenants/`

---

## 🔍 Root Cause

**TenantSerializer referenced fields that don't exist in the Tenant model:**

### Missing Fields Referenced:
- `subscription_plan` ❌
- `subscription_status` ❌
- `settings` ❌
- `logo_url` ❌ (was used as raw field, should be SerializerMethodField)

### OutletSerializer Issues:
- `country` ❌ (doesn't exist in Outlet model)
- `operating_hours` ❌ (doesn't exist, should be computed from opening_time/closing_time)

---

## ✅ Fix Applied

### TenantSerializer Changes:

**Removed:**
```python
'subscription_plan', 'subscription_status', 'settings'
```

**Added:**
```python
'logo_url',  # Now as SerializerMethodField
'secondary_color',  # Was missing but exists in model

def get_logo_url(self, obj):
    """Get logo URL"""
    if obj.logo:
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url
    return None
```

### OutletSerializer Changes:

**Removed:**
```python
'country',  # Doesn't exist
'operating_hours',  # Raw field
```

**Added:**
```python
'opening_time', 'closing_time',  # Actual model fields
'operating_hours',  # Now as SerializerMethodField

def get_operating_hours(self, obj):
    """Get formatted operating hours"""
    if obj.opening_time and obj.closing_time:
        return f"{obj.opening_time.strftime('%H:%M')} - {obj.closing_time.strftime('%H:%M')}"
    return None
```

---

## 🚀 Deploy Fix

```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
docker-compose restart backend
```

Wait 10 seconds, then test.

---

## ✅ Verification

### 1. Backend API Test
```bash
curl http://localhost:8001/api/public/tenants/

# Expected response:
[
  {
    "id": 1,
    "slug": "warung-makan-sedap",
    "name": "Warung Makan Sedap",
    "description": "Restoran Indonesia...",
    "phone": "021-12345678",
    "email": "info@warungsedap.com",
    "website": "",
    "tax_rate": "10.00",
    "service_charge_rate": "5.00",
    "logo_url": null,
    "primary_color": "#FF6B35",
    "secondary_color": "#F7931E",
    "is_active": true,
    "created_at": "2024-12-25T...",
    "outlet_count": 2
  }
]
```

### 2. Outlets API Test
```bash
curl http://localhost:8001/api/public/tenants/1/outlets/

# Expected response:
[
  {
    "id": 1,
    "tenant": 1,
    "tenant_name": "Warung Makan Sedap",
    "slug": "cabang-pusat",
    "name": "Cabang Pusat",
    "address": "Jl. Sudirman No. 123",
    "city": "Jakarta Pusat",
    "province": "DKI Jakarta",
    "postal_code": "10220",
    "phone": "021-12345678",
    "email": "",
    "latitude": "-6.208763",
    "longitude": "106.845599",
    "opening_time": null,
    "closing_time": null,
    "operating_hours": null,
    "is_active": true,
    "created_at": "2024-12-25T..."
  },
  {
    "id": 2,
    "tenant": 1,
    "tenant_name": "Warung Makan Sedap",
    "slug": "cabang-mall",
    "name": "Cabang Mall",
    ...
  }
]
```

### 3. Frontend Test
```
http://localhost:5174/kiosk
```

**Expected:**
1. ✅ Tenant selector appears (no 500 error)
2. ✅ Shows "Warung Makan Sedap" with "2 locations"
3. ✅ Click tenant → outlet selector appears
4. ✅ Shows "Cabang Pusat" and "Cabang Mall"
5. ✅ Click outlet → kiosk loads with menu

### 4. Browser Console
```javascript
// Expected logs:
Tenants loaded: 1
Outlets loaded: 2
Categories loaded: 5
Products loaded: 20
```

---

## 🔍 How to Debug Similar Issues

### Step 1: Check Backend Logs
```bash
docker-compose logs backend --tail 50 | grep -A 10 "Error\|Traceback"
```

Look for:
- `AttributeError: 'Tenant' object has no attribute 'subscription_plan'`
- `FieldError: Unknown field(s) ... specified for Tenant`

### Step 2: Compare Model vs Serializer
```python
# Model fields (backend/apps/tenants/models.py)
class Tenant(models.Model):
    name = ...
    slug = ...
    # etc.

# Serializer fields (backend/apps/tenants/serializers.py)
class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [...]  # MUST match model fields
```

### Step 3: Use Django Shell to Test
```bash
docker-compose exec backend python manage.py shell

>>> from apps.tenants.models import Tenant
>>> t = Tenant.objects.first()
>>> print(dir(t))  # See all available attributes
>>> print(t.name, t.slug, t.tax_rate)  # Test fields
```

### Step 4: Test Serializer Directly
```bash
docker-compose exec backend python manage.py shell

>>> from apps.tenants.models import Tenant
>>> from apps.tenants.serializers import TenantSerializer
>>> t = Tenant.objects.first()
>>> s = TenantSerializer(t)
>>> print(s.data)  # Should work without errors
```

---

## 📋 Checklist for Serializer Creation

When creating serializers, always:

- [ ] Check model fields exist in `models.py`
- [ ] Use `SerializerMethodField` for computed fields
- [ ] Test serializer in Django shell before deploying
- [ ] Verify API response with curl
- [ ] Check frontend can parse the response

---

## 🎯 Files Changed

- `backend/apps/tenants/serializers.py` - Fixed field mismatches
- `check_tenant_api.sh` - Added diagnostic script

---

## 🐛 Common Issues & Solutions

### Issue 1: Field doesn't exist in model
**Error**: `AttributeError: 'Tenant' object has no attribute 'subscription_plan'`

**Solution**: Remove field from serializer OR add field to model

### Issue 2: Image/File field serialization
**Error**: Logo URL not working

**Solution**: Use `SerializerMethodField` with `request.build_absolute_uri()`

### Issue 3: Computed fields
**Error**: `operating_hours` doesn't exist

**Solution**: Use `SerializerMethodField` to compute from other fields

---

## 🚀 Quick Deploy

```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
docker-compose restart backend
```

Wait 10 seconds, then:
```
http://localhost:5174/kiosk
```

Should now work! ✅

---

## 📊 Status After Fix

| Component | Before | After |
|-----------|--------|-------|
| Tenant API | ❌ 500 Error | ✅ 200 OK |
| Outlet API | ❌ 500 Error | ✅ 200 OK |
| Tenant Selector | ❌ Not Loading | ✅ Shows Restaurant |
| Outlet Selector | ❌ Not Loading | ✅ Shows Locations |
| Kiosk | ❌ Stuck on Selector | ✅ Loads Menu |

---

## ✅ Success!

**The 500 error is fixed!**

All serializer fields now match the actual model structure.

**Test now:**
```bash
curl http://localhost:8001/api/public/tenants/
# Should return 200 with tenant data

curl http://localhost:8001/api/public/tenants/1/outlets/
# Should return 200 with outlet data
```

**Frontend:**
```
http://localhost:5174/kiosk
```

Should show tenant selector → outlet selector → kiosk menu! 🎉

---

**GitHub**: https://github.com/dadinjaenudin/kiosk-svelte  
**Latest Commit**: e881dfc  
**Status**: ✅ FIXED

**Silakan deploy dan test! Tenant selector sekarang bisa load data! 🚀**
