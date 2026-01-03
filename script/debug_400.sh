#!/bin/bash

echo "🔍 Debugging 400 Bad Request"
echo "=============================="
echo ""

echo "Step 1: Check Backend Logs"
echo "-------------------------"
docker-compose logs backend --tail 50

echo ""
echo "Step 2: Test API Directly"
echo "------------------------"
curl -v http://localhost:8001/api/products/categories/ 2>&1 | head -50

echo ""
echo "Step 3: Check Database Connection"
echo "--------------------------------"
docker-compose exec backend python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.products.models import Category
print(f'Categories count: {Category.all_objects.count()}')
print('Sample categories:')
for cat in Category.all_objects.all()[:3]:
    print(f'  - {cat.name} (active: {cat.is_active})')
"

echo ""
echo "Step 4: Test ViewSet"
echo "------------------"
docker-compose exec backend python manage.py shell << 'EOF'
from apps.products.views import CategoryViewSet
from apps.products.models import Category

print(f"Total categories in DB: {Category.all_objects.count()}")
print(f"Active categories: {Category.all_objects.filter(is_active=True).count()}")

# Test ViewSet queryset
viewset = CategoryViewSet()
try:
    qs = viewset.get_queryset()
    print(f"ViewSet queryset count: {qs.count()}")
    for cat in qs[:3]:
        print(f"  - {cat.name}")
except Exception as e:
    print(f"ERROR: {e}")
EOF
