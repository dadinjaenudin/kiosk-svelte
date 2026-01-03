# 🧪 Quick Test Commands - Windows PowerShell

## ✅ Backend Health Check

### PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:8001/api/health/
```

**Expected**:
```
status  service
------  -------
ok      POS Backend
```

### CMD (curl):
```cmd
curl -s http://localhost:8001/api/health/
```

**Expected**:
```json
{"status": "ok", "service": "POS Backend"}
```

---

## 🔐 Login Test (Without Docker Hostname)

### PowerShell (One-liner):
```powershell
Invoke-RestMethod -Uri http://localhost:8001/api/auth/login/ -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"username":"admin","password":"admin123"}'
```

**Expected** (SUCCESS):
```
token                          user
-----                          ----
abc123def456...               @{id=1; username=admin; email=admin@example.com; role=admin; ...}
```

### CMD (curl - One-liner):
```cmd
curl -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

**Expected** (SUCCESS):
```json
{
  "token": "abc123def456...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

---

## 🐳 Login Test (With Docker Hostname) - THE FIX!

### PowerShell (One-liner):
```powershell
Invoke-RestMethod -Uri http://localhost:8001/api/auth/login/ -Method Post -Headers @{"Content-Type"="application/json";"Host"="backend"} -Body '{"username":"admin","password":"admin123"}'
```

**Expected** (FIXED):
```
token                          user
-----                          ----
abc123def456...               @{id=1; username=admin; ...}
```

**Before Fix** (DisallowedHost):
```
Invoke-RestMethod: The remote server returned an error: (400) Bad Request.
```

### CMD with curl.exe (One-liner - USE THIS!):
```cmd
curl.exe -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -H "Host: backend" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

**Note**: Use `curl.exe` (not `curl`) in PowerShell to use real curl, not the PowerShell alias!

**Expected** (FIXED):
```json
{
  "token": "abc123def456...",
  "user": {...}
}
```

**Before Fix** (DisallowedHost):
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>DisallowedHost at /api/auth/login/</title>
...
```

---

## 🎯 Quick Test Script

Just run this:
```cmd
TEST_LOGIN.bat
```

Or copy-paste these PowerShell commands:

```powershell
# Test 1: Health
Write-Host "`n[1/3] Backend Health:" -ForegroundColor Cyan
Invoke-RestMethod http://localhost:8001/api/health/

# Test 2: Login (localhost)
Write-Host "`n[2/3] Login with localhost:" -ForegroundColor Cyan
Invoke-RestMethod -Uri http://localhost:8001/api/auth/login/ -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"username":"admin","password":"admin123"}' | Select-Object -First 1

# Test 3: Login (Docker hostname) - THE FIX!
Write-Host "`n[3/3] Login with Docker hostname:" -ForegroundColor Cyan
Invoke-RestMethod -Uri http://localhost:8001/api/auth/login/ -Method Post -Headers @{"Content-Type"="application/json";"Host"="backend"} -Body '{"username":"admin","password":"admin123"}' | Select-Object -First 1

Write-Host "`n✅ If all 3 tests show 'token', backend is fixed!" -ForegroundColor Green
```

---

## 📊 Interpretation Guide

### Test Results Matrix:

| Health | Login (localhost) | Login (Host: backend) | Diagnosis |
|--------|-------------------|-----------------------|-----------|
| ✅ OK | ✅ Token | ✅ Token | **PERFECT!** ✅ |
| ✅ OK | ✅ Token | ❌ DisallowedHost | Need REBUILD_BACKEND.bat |
| ✅ OK | ❌ Invalid credentials | ❌ Invalid credentials | Need CREATE_USERS.bat |
| ❌ Fail | ❌ Fail | ❌ Fail | Backend not running |

---

## 🔧 Troubleshooting

### PowerShell: `curl` is actually `Invoke-WebRequest` alias
**Problem**: PowerShell has `curl` as alias for `Invoke-WebRequest`, not real curl  
**Solution**: Use `curl.exe` to use real curl:
```powershell
# ❌ Wrong (uses PowerShell alias with different syntax)
curl -H "Header: value"

# ✅ Correct (uses real curl)
curl.exe -H "Header: value"
```

### PowerShell Error: "Cannot bind parameter 'Headers'"
**Cause**: Using `curl` instead of `curl.exe` in PowerShell  
**Solution**: Add `.exe` to use real curl:
```powershell
curl.exe -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

Or use native PowerShell:
```powershell
Invoke-RestMethod -Uri http://localhost:8001/api/auth/login/ -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"username":"admin","password":"admin123"}'
```

### CMD Error: "curl: command not found"
**Solution**: Use full path or install curl:
```cmd
# Windows 10/11 has curl built-in at:
C:\Windows\System32\curl.exe -s http://localhost:8001/api/health/
```

### Error: "The remote server returned an error: (400) Bad Request"
**Cause**: ALLOWED_HOSTS not updated yet  
**Solution**: Run `REBUILD_BACKEND.bat`

### Error: "Invalid credentials"
**Cause**: Admin user not created  
**Solution**: Run `CREATE_USERS.bat`

---

## ✅ Success Criteria

After running tests, you should see:

### Test 1 (Health):
```
status : ok
service : POS Backend
```

### Test 2 (Login localhost):
```
token : abc123def456...
user  : @{id=1; username=admin; role=admin}
```

### Test 3 (Login Docker hostname):
```
token : abc123def456...
user  : @{id=1; username=admin; role=admin}
```

**All 3 passed** = ✅ Backend is ready for admin login!

---

## 🎉 After Tests Pass

1. Open http://localhost:5175/
2. Login: admin / admin123
3. Should redirect to dashboard
4. No more 400 errors!

---

## 📝 Copy-Paste Ready Commands

### Full Test Suite (PowerShell):
```powershell
Write-Host "Testing Backend..." -ForegroundColor Yellow; Invoke-RestMethod http://localhost:8001/api/health/; Write-Host "`nTesting Login (localhost)..." -ForegroundColor Yellow; Invoke-RestMethod -Uri http://localhost:8001/api/auth/login/ -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"username":"admin","password":"admin123"}' | Select token; Write-Host "`nTesting Login (Docker hostname)..." -ForegroundColor Yellow; Invoke-RestMethod -Uri http://localhost:8001/api/auth/login/ -Method Post -Headers @{"Content-Type"="application/json";"Host"="backend"} -Body '{"username":"admin","password":"admin123"}' | Select token
```

### Quick Login Test (CMD):
```cmd
curl -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -H "Host: backend" -d "{\"username\":\"admin\",\"password\":\"admin123\"}" | findstr token
```

If you see `"token"` = ✅ SUCCESS!

---

**Next**: After backend tests pass, try login in browser! 🚀
