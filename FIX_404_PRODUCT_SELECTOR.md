# 🔴 404 Error on Product Selector Endpoint - TROUBLESHOOTING

## Error Details
```
GET http://localhost:5175/api/promotions/product-selector/?is_available=true
Status: 404 Not Found
```

## Root Cause Analysis

### What We Checked ✅
1. **URLs Configuration** - ✅ Correct
   - `backend/config/urls.py` line 36: `path('api/', include('apps.promotions.urls'))`
   - `backend/apps/promotions/urls.py` line 8: `router.register(r'product-selector', ProductSelectorViewSet)`

2. **ViewSet Exists** - ✅ Correct
   - `backend/apps/promotions/views.py` line 224: `class ProductSelectorViewSet`

3. **App Installed** - ✅ Correct
   - `backend/config/settings.py` line 55: `'apps.promotions'` in INSTALLED_APPS

4. **Middleware Fixed** - ✅ Applied (commit f48365b)

### Why 404 Still Happens

**Most Likely Cause**: **Backend container NOT restarted after middleware fix**

Django loads URLs and middleware at startup. Changes to these files require a **full backend restart** to take effect.

## 🔧 Solution: Restart Backend Properly

### Step 1: Stop All Services
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
docker-compose down
```

### Step 2: Rebuild Backend (Important!)
```bash
docker-compose build backend
```

### Step 3: Start All Services
```bash
docker-compose up -d
```

### Step 4: Watch Logs to Confirm Startup
```bash
# Watch all logs
docker-compose logs -f

# Or just backend logs
docker-compose logs -f backend

# Look for these messages:
# ✅ "Performing system checks..."
# ✅ "System check identified no issues"
# ✅ "Django version X.X.X, using settings 'config.settings'"
# ✅ "Starting ASGI/HTTP/Socket application running on..."
# ✅ "Booting worker with pid: XXX"
```

## 🧪 Verify Endpoint is Available

### Test 1: List All Promotion Endpoints
```bash
# Access backend container
docker-compose exec backend bash

# Inside container, test URLs
python manage.py shell

# In Python shell:
from django.urls import get_resolver
resolver = get_resolver()
patterns = []

def collect_patterns(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            collect_patterns(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            patterns.append(prefix + str(pattern.pattern))

collect_patterns(resolver.url_patterns)
promo_patterns = [p for p in patterns if 'promot' in p.lower() or 'product-selector' in p.lower()]
for p in promo_patterns:
    print(p)

# Expected output should include:
# api/promotions/
# api/product-selector/
# api/promotion-usage/
```

### Test 2: Direct Backend API Call
```bash
# Get a valid token first
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Copy the token from response, then test endpoint:
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://localhost:8001/api/promotions/product-selector/?is_available=true

# Expected: 200 OK with product list
# If 404: Backend needs rebuild/restart
```

### Test 3: Check Backend is Using Latest Code
```bash
# Check git commit inside backend container
docker-compose exec backend git log --oneline -1

# Should show: f48365b fix: Allow super admin to bypass tenant middleware
# If different: Container using old code, rebuild needed
```

## 🔍 Alternative Checks

### Check if Container Has Latest Code
```bash
# View middleware file inside container
docker-compose exec backend cat apps/tenants/middleware.py | grep -A 5 "Super admin"

# Should see:
# if request.user.role == 'admin':
#     logger.debug(f"Super admin user: {request.user.username} - tenant not required")
#     return None
```

### Check URL Registration
```bash
# Try browsing to the API root
curl http://localhost:8001/api/

# DRF should show available endpoints including promotions
```

## 🚨 Common Issues & Fixes

### Issue 1: Container Using Old Code
**Symptom**: Container doesn't have latest middleware changes  
**Fix**: 
```bash
docker-compose down
docker-compose build backend --no-cache
docker-compose up -d
```

### Issue 2: Django Not Loading URLs
**Symptom**: URLs don't appear in routing  
**Fix**:
```bash
# Check for syntax errors
docker-compose exec backend python manage.py check

# If errors, check:
# - backend/apps/promotions/urls.py
# - backend/apps/promotions/views.py
# - Import statements
```

### Issue 3: Migration Issues
**Symptom**: Backend won't start due to DB errors  
**Fix**:
```bash
docker-compose exec backend python manage.py migrate
```

### Issue 4: Port Conflicts
**Symptom**: Backend not accessible on 8001  
**Fix**:
```bash
# Check if port is in use
netstat -ano | findstr :8001  # Windows
lsof -i :8001                 # Mac/Linux

# If in use, either:
# 1. Kill the process using that port
# 2. Change port in docker-compose.yml
```

## 📋 Complete Restart Checklist

Run these commands in order:

```bash
# 1. Navigate to project
cd D:\YOGYA-Kiosk\kiosk-svelte

# 2. Pull latest code (if not done)
git pull origin main

# 3. Stop all services
docker-compose down

# 4. Remove old volumes (optional, if DB issues)
# docker-compose down -v

# 5. Rebuild backend
docker-compose build backend

# 6. Start all services
docker-compose up -d

# 7. Wait for backend ready (~30 seconds)
docker-compose logs -f backend
# Press Ctrl+C when you see "Booting worker"

# 8. Check backend is healthy
curl http://localhost:8001/api/health/
# Should return: {"status":"ok","service":"POS Backend"}

# 9. Test promotions endpoint
# (Get token first, then test product-selector)

# 10. Open admin and test
# http://localhost:5175/promotions/create
```

## 🎯 Expected Behavior After Restart

### Backend Logs Should Show:
```
backend_1  | Performing system checks...
backend_1  | System check identified no issues (0 silenced).
backend_1  | Django version X.X.X, using settings 'config.settings'
backend_1  | Starting ASGI/HTTP/Socket application
backend_1  | Quit the server with CONTROL-C.
backend_1  | Booting worker with pid: XXX
```

### API Should Respond:
```bash
# Health check
curl http://localhost:8001/api/health/
{"status":"ok","service":"POS Backend"}

# Promotions (with valid token)
curl -H "Authorization: Token TOKEN" http://localhost:8001/api/promotions/
{"count":0,"next":null,"previous":null,"results":[]}

# Product selector (with valid token)
curl -H "Authorization: Token TOKEN" http://localhost:8001/api/promotions/product-selector/
{"count":X,"next":null,"previous":null,"results":[...]}
```

### Frontend Should Work:
- No 404 errors in console
- Product selector loads products
- Can select products
- Can create promotion

## 🔗 Related Documentation
- [FIX_TENANT_MIDDLEWARE.md](./FIX_TENANT_MIDDLEWARE.md) - Middleware fix details
- [FIX_PRODUCT_SELECTOR.md](./FIX_PRODUCT_SELECTOR.md) - Endpoint fix details

## ✨ TL;DR - Quick Fix

```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
docker-compose down
docker-compose build backend
docker-compose up -d
docker-compose logs -f backend  # Wait for "Booting worker"
# Then test: http://localhost:5175/promotions/create
```

**If still 404**: Share backend logs with error details.
