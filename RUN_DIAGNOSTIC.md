# 🔬 DIAGNOSTIC MODE: 400 Bad Request Persists

## Current Status
Migrations done ✅ but still getting 400 Bad Request ❌

We need to **diagnose the exact cause** with test scripts.

---

## 🚀 Run Diagnostic Tests

### Quick Test (2 Commands)

```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
docker-compose exec backend python /app/test_api_direct.py
```

**This will test**:
1. ✅ Models work?
2. ✅ Serializers work?
3. ✅ ViewSet queryset works?
4. ✅ API request simulation works?

**Share the full output!**

---

### Full Test (Optional)

```bash
chmod +x test_full_api.sh
./test_full_api.sh > diagnostic_report.txt 2>&1
```

Then share `diagnostic_report.txt`

---

## 📋 What to Share

Please run and share output of:

```bash
docker-compose exec backend python /app/test_api_direct.py
```

Expected output format:
```
============================================================
DIRECT API TEST
============================================================

1. Testing Models...
----------------------------------------
✓ Total categories: 5
✓ Active categories: 5
  Sample categories:
    - 1: Main Course (tenant: 1)
    - 2: Beverages (tenant: 1)
    - 3: Desserts (tenant: 1)

2. Testing Serializers...
----------------------------------------
✓ Serializer works, got 2 items
  First item keys: ['id', 'name', 'description', ...]

3. Testing ViewSet Queryset...
----------------------------------------
✓ ViewSet queryset: 5 items
  First 3 items:
    - Main Course
    - Beverages
    - Desserts

4. Simulating API Request...
----------------------------------------
✓ Response status: 200
  Response type: <class 'rest_framework.response.Response'>
  Response data type: <class 'rest_framework.utils.serializer_helpers.ReturnDict'>
  Response keys: ['count', 'next', 'previous', 'results']
  Results count: 5
✓ SUCCESS: API returns 200

============================================================
TEST COMPLETE
============================================================
```

---

## 🎯 Possible Causes of 400

Based on your output, we can identify:

### Cause 1: Model Issue
If you see:
```
✗ Model test failed: ...
```
→ Problem with TenantModel or database

### Cause 2: Serializer Issue
If you see:
```
✗ Serializer test failed: ...
```
→ Problem with CategorySerializer

### Cause 3: ViewSet Issue
If you see:
```
✗ ViewSet test failed: ...
```
→ Problem with get_queryset()

### Cause 4: Middleware Issue
If simulation works but real API fails:
```
✓ SUCCESS: API returns 200 (in test)
✗ But curl returns 400
```
→ Problem with middleware or CORS

---

## 🔧 Quick Fixes Based on Output

### If models fail:
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed_demo_data
```

### If serializers fail:
Check for missing fields or invalid data

### If ViewSet fails:
Issue with `all_objects` manager

### If only real API fails:
Issue with middleware or settings

---

## 📝 Alternative: Check Response Details

Try this to see actual error:

```bash
curl -v http://localhost:8001/api/products/categories/ 2>&1 | tee curl_verbose.txt
```

Look for:
```
< HTTP/1.1 400 Bad Request
< Content-Type: application/json

{
  "error": "...",
  "detail": "..."
}
```

Share the error message!

---

## 🎯 Next Steps

1. **Run test**: `docker-compose exec backend python /app/test_api_direct.py`
2. **Share output**: Copy-paste full output
3. **I'll identify**: Exact cause from output
4. **We'll fix**: Target the specific issue

---

## 📊 What We Know So Far

✅ **Working**:
- Backend container running
- Migrations applied
- Code deployed

❌ **Not Working**:
- API returns 400
- Frontend can't fetch data

🔍 **Need to Know**:
- Which step fails in test_api_direct.py?
- What's the exact error message?

---

## ⚡ Quick Command

```bash
cd D:\YOGYA-Kiosk\kiosk-svelte && \
git pull origin main && \
docker-compose exec backend python /app/test_api_direct.py
```

**Copy-paste all output and share it!**

---

**GitHub**: https://github.com/dadinjaenudin/kiosk-svelte
**Latest**: `1381559` - Diagnostic test scripts

**Status**: 🔬 **AWAITING DIAGNOSTIC OUTPUT**

Silakan jalankan test dan share hasilnya! Dengan output ini, saya akan tahu persis apa masalahnya. 🎯
