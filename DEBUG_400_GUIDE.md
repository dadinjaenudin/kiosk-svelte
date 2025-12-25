# 🔍 DEBUG GUIDE: 400 Bad Request

## ❌ Error
```
GET http://localhost:8001/api/products/categories/ 400 (Bad Request)
GET http://localhost:8001/api/products/products/ 400 (Bad Request)
```

## 🔧 Quick Fixes to Try (In Order)

### Fix 1: Pull Latest Code & Deploy
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
chmod +x deploy.sh
./deploy.sh
```

This will:
- Pull latest debug logging
- Run migrations
- Seed data
- Test endpoints

---

### Fix 2: Check Backend Logs
```bash
# View live logs:
docker-compose logs -f backend

# Last 100 lines:
docker-compose logs backend --tail 100

# Look for errors like:
# - AttributeError
# - DoesNotExist
# - ProgrammingError
# - ValidationError
```

**Share the logs if you see errors!**

---

### Fix 3: Test API Directly
```bash
# Test health:
curl -v http://localhost:8001/api/health/

# Test categories with verbose:
curl -v http://localhost:8001/api/products/categories/

# Test products:
curl -v http://localhost:8001/api/products/products/
```

Look for:
- Response status code (should be 200, not 400)
- Response body (error messages)
- Headers (content-type, etc)

---

### Fix 4: Check Database
```bash
# Check if data exists:
docker-compose exec backend python check_data.py

# Should show:
# Tenants: 1
# Outlets: 2
# Users: 2
# Categories: 5
# Products: 20

# If 0, seed data:
docker-compose exec backend python manage.py seed_demo_data
```

---

### Fix 5: Test Models Directly
```bash
docker-compose exec backend python manage.py shell

# Then in shell:
from apps.products.models import Category, Product

# Test all_objects manager:
print(f"Categories: {Category.all_objects.count()}")
print(f"Active categories: {Category.all_objects.filter(is_active=True).count()}")
print(f"Products: {Product.all_objects.count()}")
print(f"Available products: {Product.all_objects.filter(is_available=True).count()}")

# List categories:
for cat in Category.all_objects.all():
    print(f"  - {cat.id}: {cat.name} (active: {cat.is_active})")

# Exit: Ctrl+D
```

---

### Fix 6: Test ViewSet
```bash
docker-compose exec backend python manage.py shell

# In shell:
from apps.products.views import CategoryViewSet
from apps.products.serializers import CategorySerializer

# Create viewset instance:
viewset = CategoryViewSet()

# Test queryset:
qs = viewset.get_queryset()
print(f"Queryset count: {qs.count()}")

# Test serializer:
cats = qs[:5]
serializer = CategorySerializer(cats, many=True)
print("Serialized data:")
print(serializer.data)

# Exit: Ctrl+D
```

---

### Fix 7: Nuclear Option (Fresh Start)
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte

# Stop everything:
docker-compose down -v  # ⚠️ Deletes data!

# Pull latest:
git pull origin main

# Deploy fresh:
chmod +x deploy.sh
./deploy.sh
```

---

## 🔍 Common Issues & Solutions

### Issue 1: "relation does not exist"
**Cause**: Migrations not run
**Fix**:
```bash
docker-compose run --rm backend python manage.py migrate
```

### Issue 2: Categories count = 0
**Cause**: No data seeded
**Fix**:
```bash
docker-compose exec backend python manage.py seed_demo_data
```

### Issue 3: "AttributeError: all_objects"
**Cause**: Model doesn't inherit from TenantModel
**Fix**: Rebuild backend
```bash
docker-compose build backend
docker-compose restart backend
```

### Issue 4: "ValidationError: Cannot save without tenant context"
**Cause**: Trying to save without tenant
**Fix**: This shouldn't happen in kiosk (read-only)
- Check if any POST/PUT requests are being made

### Issue 5: Pagination error
**Cause**: Pagination class issue
**Fix**: Might need to disable pagination for these endpoints

---

## 📝 What to Share for Help

If none of the fixes work, share:

1. **Backend logs** (last 100 lines):
```bash
docker-compose logs backend --tail 100 > backend_logs.txt
```

2. **curl verbose output**:
```bash
curl -v http://localhost:8001/api/products/categories/ > categories_response.txt 2>&1
```

3. **Database check**:
```bash
docker-compose exec backend python check_data.py > data_check.txt
```

4. **Container status**:
```bash
docker-compose ps > containers.txt
```

5. **Model test**:
```bash
docker-compose exec backend python manage.py shell << 'EOF' > model_test.txt
from apps.products.models import Category, Product
print(f"Categories: {Category.all_objects.count()}")
print(f"Products: {Product.all_objects.count()}")
EOF
```

---

## 🧪 Advanced Debugging

### Enable Django Debug Mode
Edit `.env`:
```
DEBUG=True
```

Then restart:
```bash
docker-compose restart backend
```

### Check Middleware
```bash
docker-compose exec backend python manage.py shell

from apps.tenants.middleware import TenantMiddleware
# Check middleware is loading
```

### Test Serializers
```bash
docker-compose exec backend python manage.py shell

from apps.products.models import Category
from apps.products.serializers import CategorySerializer

cat = Category.all_objects.first()
serializer = CategorySerializer(cat)
print(serializer.data)
```

### Raw SQL Query
```bash
docker-compose exec db psql -U pos_user -d pos_db

-- Check tables:
\dt

-- Check categories:
SELECT id, name, is_active FROM categories;

-- Check products:
SELECT id, name, is_available FROM products LIMIT 5;

-- Exit:
\q
```

---

## 🎯 Expected Working State

After fixes, you should see:

### Backend Logs:
```
INFO CategoryViewSet queryset count: 5
INFO CategoryViewSet.list called - Request: GET /api/products/categories/
INFO ProductViewSet queryset count: 20
INFO ProductViewSet.list called - Request: GET /api/products/products/
```

### API Response:
```bash
curl http://localhost:8001/api/products/categories/

# Should return:
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Main Course",
      "description": "",
      "sort_order": 1,
      "is_active": true,
      "product_count": 10
    },
    ...
  ]
}
```

### Frontend Console:
```
Categories API response: {count: 5, results: Array(5)}
Categories loaded: 5
Products API response: {count: 20, results: Array(20)}
Products loaded: 20
```

---

## ⚡ Quick Deploy Command

```bash
cd D:\YOGYA-Kiosk\kiosk-svelte && \
git pull origin main && \
chmod +x deploy.sh && \
./deploy.sh
```

This runs all migrations, seeds data, and tests endpoints automatically.

---

**STATUS**: Ready for debugging! Run `./deploy.sh` and share logs if errors persist.
