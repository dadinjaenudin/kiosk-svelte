#!/bin/bash

echo "🔬 COMPREHENSIVE API TEST"
echo "=========================="
echo ""

echo "Step 1: Check containers are running"
echo "------------------------------------"
docker-compose ps

echo ""
echo "Step 2: Test direct Python script"
echo "---------------------------------"
docker-compose exec backend python /app/test_api_direct.py

echo ""
echo "Step 3: Test curl from host"
echo "---------------------------"
echo "Health check:"
curl -s http://localhost:8001/api/health/ | head -20

echo ""
echo "Categories API:"
curl -s http://localhost:8001/api/products/categories/ | head -50

echo ""
echo "Step 4: Test curl from inside container"
echo "---------------------------------------"
docker-compose exec backend curl -s http://localhost:8000/api/products/categories/ | head -50

echo ""
echo "Step 5: Check Django settings"
echo "-----------------------------"
docker-compose exec backend python manage.py shell << 'EOF'
from django.conf import settings
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
print(f"CORS_ALLOW_ALL_ORIGINS: {getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)}")
EOF

echo ""
echo "Step 6: Check middleware"
echo "-----------------------"
docker-compose exec backend python manage.py shell << 'EOF'
from django.conf import settings
print("Middleware:")
for mw in settings.MIDDLEWARE:
    print(f"  - {mw}")
EOF

echo ""
echo "Step 7: Backend logs (last 30 lines)"
echo "------------------------------------"
docker-compose logs backend --tail 30

echo ""
echo "=========================="
echo "TEST COMPLETE"
echo "=========================="
echo ""
echo "If you see 400 errors above, share:"
echo "  1. Output of 'Step 2: Test direct Python script'"
echo "  2. Output of 'Step 7: Backend logs'"
echo ""
