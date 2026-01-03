# 🐛 Login 400 Bad Request - Debugging Guide

## 📋 Issue

**Error**: `POST http://localhost:5175/api/auth/login/ 400 (Bad Request)`  
**Status**: Login page loads but authentication fails  
**Warning**: `unknown prop 'params'` (can be ignored - SvelteKit internal)

---

## 🔍 Diagnosis Steps

### Step 1: Pull Latest Code with Logging
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
docker-compose restart admin
```

### Step 2: Open Browser Console
1. Open http://localhost:5175/
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Try to login with: **admin / admin123**

### Step 3: Check Console Logs
You should see detailed logs like:
```
🔐 Attempting login: {username: "admin"}
🔄 Proxying: POST /api/auth/login/ → http://backend:8000/api/auth/login/
📡 Proxy response: 400 /api/auth/login/
📡 Login response status: 400
❌ Login error response: [error message here]
```

### Step 4: Check Container Logs
```bash
# Admin container logs (proxy)
docker-compose logs admin --tail=50

# Backend container logs (API)
docker-compose logs backend --tail=50
```

---

## 🔧 Common Causes & Fixes

### Cause 1: Backend Not Ready
**Symptoms**: 
- 502 Bad Gateway
- Connection refused

**Check**:
```bash
docker-compose ps backend
# Should show: Up (healthy)

curl http://localhost:8001/api/health/
# Should return: {"status":"ok","service":"POS Backend"}
```

**Fix**:
```bash
docker-compose restart backend
timeout /t 20
```

---

### Cause 2: User Not Created
**Symptoms**:
- 400 Bad Request
- Error: "Invalid credentials" or "User not found"

**Check**:
```bash
docker-compose exec backend python manage.py shell
```

Then in Python shell:
```python
from apps.users.models import User

# Check if admin user exists
admin = User.objects.filter(username='admin').first()
if admin:
    print(f"✅ Admin exists: {admin.username}, role: {admin.role}")
else:
    print("❌ Admin user does not exist!")
    
# List all users
print("\nAll users:")
for u in User.objects.all():
    print(f"  - {u.username} ({u.role})")
    
exit()
```

**Fix (Create Admin)**:
```bash
docker-compose exec backend python manage.py shell
```

```python
from apps.users.models import User

# Create super admin
admin = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123',
    first_name='Super',
    last_name='Admin',
    role='admin'
)
print(f"✅ Admin created: {admin.username}")
exit()
```

---

### Cause 3: Migration Not Run
**Symptoms**:
- 500 Internal Server Error
- Database table doesn't exist

**Check**:
```bash
docker-compose logs backend | grep -i "migration\|error"
```

**Fix**:
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose restart backend
```

---

### Cause 4: CORS Issue
**Symptoms**:
- CORS error in browser console
- OPTIONS preflight failed

**Check Browser Console** for:
```
Access to fetch at 'http://localhost:8001/api/auth/login/' 
from origin 'http://localhost:5175' has been blocked by CORS policy
```

**Fix** (backend already has CORS config, but restart to apply):
```bash
docker-compose restart backend
```

---

### Cause 5: Proxy Configuration
**Symptoms**:
- 404 Not Found
- Wrong URL being called

**Check vite logs**:
```bash
docker-compose logs admin | grep -i "proxyreq\|proxyres"
```

**Expected**:
```
🔄 Proxying: POST /api/auth/login/ → http://backend:8000/api/auth/login/
📡 Proxy response: 200 /api/auth/login/
```

**If target is wrong**, check `docker-compose.yml`:
```yaml
admin:
  environment:
    - VITE_API_URL=http://backend:8000  # Should be 'backend' in Docker
```

---

## 📊 Request/Response Debug

### Expected Request (from Browser):
```http
POST http://localhost:5175/api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

### Expected Proxy (to Backend):
```http
POST http://backend:8000/api/auth/login/
Content-Type: application/json
Origin: http://localhost:5175

{
  "username": "admin",
  "password": "admin123"
}
```

### Expected Response (Success):
```json
{
  "token": "abc123def456...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "tenant_id": null,
    "tenant": null,
    "outlet_id": null,
    "full_name": "Super Admin"
  }
}
```

### Expected Response (Error):
```json
{
  "error": "Invalid credentials",
  "detail": "Username or password is incorrect"
}
```

---

## 🧪 Manual API Test (Bypass Proxy)

### Test Backend Directly:
```bash
# From Windows PowerShell
curl -X POST http://localhost:8001/api/auth/login/ `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"admin123\"}'
```

### Expected Success:
```json
{
  "token": "...",
  "user": {...}
}
```

### Expected Error:
```json
{
  "error": "Invalid credentials"
}
```

**If this works** → Proxy issue  
**If this fails** → Backend issue

---

## 🔍 Detailed Backend Logs

### Enable Django Debug Logging:
```bash
docker-compose exec backend python manage.py shell
```

```python
import logging
logging.basicConfig(level=logging.DEBUG)
exit()
```

### Watch Backend Logs:
```bash
docker-compose logs backend -f
```

### Try Login Again
You should see:
```
[INFO] POST /api/auth/login/ HTTP/1.1
[DEBUG] User authentication attempt: admin
[DEBUG] Password check: [result]
[INFO] Login successful: admin
```

Or:
```
[ERROR] Authentication failed: Invalid credentials
[ERROR] User not found: admin
```

---

## ✅ Success Checklist

After fixing, verify:

### 1. Backend Health
```bash
curl http://localhost:8001/api/health/
# ✅ {"status":"ok","service":"POS Backend"}
```

### 2. Admin User Exists
```bash
docker-compose exec backend python manage.py shell
>>> from apps.users.models import User
>>> User.objects.filter(username='admin').exists()
True  # ✅
>>> exit()
```

### 3. Migrations Applied
```bash
docker-compose exec backend python manage.py showmigrations
# ✅ All should have [X] checkmarks
```

### 4. Proxy Working
```
Browser Console:
🔐 Attempting login: {username: "admin"}
🔄 Proxying: POST /api/auth/login/ → http://backend:8000/api/auth/login/
📡 Proxy response: 200 /api/auth/login/  # ✅ 200, not 400!
✅ Login successful: {username: "admin", role: "admin"}
```

### 5. Dashboard Loads
```
After login:
✅ Redirects to /dashboard
✅ Shows "Welcome back, admin!"
✅ Stats cards display
✅ No errors in console
```

---

## 🐛 Troubleshooting Script

Create `DEBUG_LOGIN.bat`:
```batch
@echo off
echo ========================================
echo   Login Debugging Script
echo ========================================

echo.
echo [1/5] Checking backend health...
curl -s http://localhost:8001/api/health/

echo.
echo [2/5] Checking admin user...
docker-compose exec -T backend python manage.py shell << EOF
from apps.users.models import User
admin = User.objects.filter(username='admin').first()
if admin:
    print(f"Admin exists: {admin.username}, role: {admin.role}")
else:
    print("Admin user NOT FOUND!")
exit()
EOF

echo.
echo [3/5] Testing login API directly...
curl -X POST http://localhost:8001/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

echo.
echo [4/5] Checking migrations...
docker-compose exec -T backend python manage.py showmigrations | grep auth

echo.
echo [5/5] Checking recent backend logs...
docker-compose logs backend --tail=20

echo.
echo ========================================
echo   Diagnostic Complete
echo ========================================
pause
```

---

## 📝 Quick Fixes Reference

| Error | Quick Fix |
|-------|-----------|
| **Connection refused** | `docker-compose restart backend` |
| **Admin not found** | Run `CREATE_USERS.bat` |
| **Table doesn't exist** | `docker-compose exec backend python manage.py migrate` |
| **CORS error** | `docker-compose restart backend` (CORS already configured) |
| **Proxy 404** | Check `VITE_API_URL=http://backend:8000` |
| **500 Internal Error** | Check `docker-compose logs backend --tail=50` |

---

## 🎯 Most Likely Cause

Based on your symptoms (login page loads, 400 error):

**#1: Admin user not created**

**Quick Fix**:
```bash
# Run this:
CREATE_USERS.bat

# OR manually:
docker-compose exec backend python manage.py shell
```

```python
from apps.users.models import User
User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123',
    role='admin'
)
exit()
```

**Then try login again!**

---

## 📚 Related Files

- `admin/src/lib/api/auth.js` - Login logic with logging
- `admin/vite.config.js` - Proxy configuration with logging
- `backend/apps/users/auth_views.py` - Backend login endpoint
- `backend/config/settings.py` - CORS and auth settings
- `CREATE_USERS.bat` - Script to create users

---

**Next Step**: Run the diagnostic commands above and share the output! 🔍
