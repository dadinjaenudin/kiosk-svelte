#!/bin/bash

echo "🔍 Debugging Tenant Filter Issue..."
echo ""

echo "1. Check if products have tenant info:"
curl -s http://localhost:8001/api/products/products/ | jq '.results[0] | {id, name, tenant_id, tenant_name, tenant_color}' 2>/dev/null || echo "❌ API not responding or jq not available"

echo ""
echo "2. Check product count:"
curl -s http://localhost:8001/api/products/products/ | jq '.results | length' 2>/dev/null || echo "❌ Cannot get count"

echo ""
echo "3. Check if tenants table has data:"
docker-compose exec -T backend python manage.py shell << 'PYTHON'
from apps.tenants.models import Tenant
print(f"Total tenants: {Tenant.objects.count()}")
for t in Tenant.objects.all():
    print(f"  - ID: {t.id}, Name: {t.name}, Color: {t.primary_color}")
PYTHON

echo ""
echo "4. Check frontend logs for tenant extraction:"
echo "Open browser console and check for 'Tenants extracted' log"

