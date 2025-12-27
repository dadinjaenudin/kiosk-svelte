# 🔧 ERROR FIXES - 500 & Client Warning

## ❌ Issue 1: 500 Internal Server Error

### Symptoms
```
Failed to load resource: the server responded with a status of 500 
```

### Diagnosis Steps

#### 1. Check Backend Logs
**Windows**:
```batch
cd D:\YOGYA-Kiosk\kiosk-svelte
check_backend_logs.bat
```

**Or manually**:
```batch
docker logs kiosk-svelte-backend-1 --tail 50
```

#### 2. Look For These Errors
- `500 Internal Server Error`
- `Traceback (most recent call last):`
- `SyntaxError`
- `ImportError`
- `NameError`
- `AttributeError`

### Common Causes & Fixes

#### Cause A: Database Migration Needed
```batch
docker-compose exec backend python manage.py migrate
```

#### Cause B: Missing Environment Variables
```batch
# Check .env file exists
dir .env

# Restart backend
docker-compose restart backend
```

#### Cause C: Code Error in Backend
```bash
# Check recent backend changes
git log --oneline -5

# Rollback if needed
git checkout <previous-commit>
docker-compose restart backend
```

#### Cause D: Database Connection Issue
```batch
# Restart all services
docker-compose restart
```

---

## ⚠️ Issue 2: Client Warning - Unknown prop 'params'

### Symptoms
```
<Error> was created with unknown prop 'params'
```

### Root Cause
SvelteKit expects `export let data` not `export let params` in +page.svelte

### Fix Applied (Already in Code)
```javascript
// ❌ BEFORE
export let params = undefined;

// ✅ AFTER (already fixed)
export let data = undefined;
```

### Clear Browser Cache
```
Method 1: Hard Refresh
Ctrl + Shift + R (Chrome/Edge)
Ctrl + F5 (Firefox)

Method 2: Clear Cache
1. F12 → Application
2. Clear storage → Clear site data
3. Refresh page

Method 3: Incognito
Ctrl + Shift + N
Test in clean state
```

---

## 🚀 COMPLETE FIX PROCEDURE

### Step 1: Pull Latest Code
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
```

### Step 2: Check Backend Logs
```batch
check_backend_logs.bat
```

### Step 3: Restart Services
```batch
docker-compose restart
```

### Step 4: Wait & Check
```
Wait 10-15 seconds for backend to start
Check: http://localhost:8001/api/docs/
Should see: Swagger API docs
```

### Step 5: Clear Browser Cache
```
Ctrl + Shift + R (Hard refresh)
Or use Incognito mode
```

### Step 6: Test Kiosk
```
http://localhost:5174/kiosk
Should load without errors
```

---

## 📊 Error Diagnosis Matrix

| Error Code | Meaning | Check |
|------------|---------|-------|
| 500 | Backend crash | Backend logs |
| 502 | Backend not running | `docker ps` |
| 503 | Backend starting | Wait 10s, retry |
| 404 | Endpoint not found | API URL correct? |
| CORS | Cross-origin | Backend CORS config |

---

## 🔍 Backend Health Check

### Command
```batch
curl http://localhost:8001/api/docs/
```

### Expected Response
```html
<!DOCTYPE html>
<html>
  <head>
    <title>API Documentation</title>
    ...
```

### If No Response
```batch
# Check if backend running
docker ps | findstr backend

# Check backend logs
docker logs kiosk-svelte-backend-1 --tail 50

# Restart backend
docker-compose restart backend
```

---

## 🎯 Quick Troubleshooting

### Issue: 500 Error on /kiosk
```batch
# 1. Check backend logs
check_backend_logs.bat

# 2. Restart backend
docker-compose restart backend

# 3. Wait 10 seconds
timeout /t 10

# 4. Test again
# Open: http://localhost:5174/kiosk
```

### Issue: Client Warning Persists
```
# Clear browser cache:
Ctrl + Shift + R

# Or test in incognito:
Ctrl + Shift + N
```

### Issue: Backend Won't Start
```batch
# Check logs
docker logs kiosk-svelte-backend-1

# Full restart
docker-compose down
docker-compose up -d

# Check status
docker-compose ps
```

---

## 📝 What to Share

**If errors persist, please share:**

1. **Backend Logs**:
   ```batch
   docker logs kiosk-svelte-backend-1 --tail 100 > backend_error.txt
   ```

2. **Browser Console** (F12):
   - Full error message
   - Network tab → Failed request
   - Response body

3. **Docker Status**:
   ```batch
   docker-compose ps > docker_status.txt
   ```

4. **Recent Changes**:
   ```bash
   git log --oneline -10
   ```

---

## 🚀 DEPLOY NOW

```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
docker-compose restart
timeout /t 15
check_backend_logs.bat
```

**Then clear browser cache and test!**

---

## 📊 Status

- **Warning `params`**: Already fixed in code ✅
- **500 Error**: Need backend logs to diagnose 🔍
- **Fix Script**: check_backend_logs.bat created ✅

---

**Please run check_backend_logs.bat and share the output!** 🔍
