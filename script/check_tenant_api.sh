#!/bin/bash

echo "🔍 Checking Tenant API..."
echo ""

# Test tenant API directly
echo "1. Testing /api/public/tenants/ endpoint..."
curl -v http://localhost:8001/api/public/tenants/ 2>&1 | head -30

echo ""
echo ""
echo "2. Checking backend logs for errors..."
docker-compose logs backend --tail 50 | grep -A 5 -B 5 "Error\|Exception\|Traceback" || echo "No errors found in logs"

echo ""
echo ""
echo "3. Testing if tenants exist in database..."
docker-compose exec backend python manage.py shell << 'PYTHON'
from apps.tenants.models import Tenant
print(f"Total tenants: {Tenant.objects.count()}")
if Tenant.objects.exists():
    for tenant in Tenant.objects.all():
        print(f"  - {tenant.name} (id: {tenant.id}, active: {tenant.is_active})")
else:
    print("⚠️ No tenants found! Run: docker-compose exec backend python manage.py seed_demo_data")
PYTHON

echo ""
echo ""
echo "4. Checking if URL is registered..."
docker-compose exec backend python manage.py show_urls | grep -i tenant || echo "⚠️ Tenant URLs not found"

