#!/bin/bash

# Food Court Sample Data Seeding Script
# Creates 5 different food tenants with products

echo "=================================================="
echo "🏪 FOOD COURT - SAMPLE DATA SEEDING"
echo "=================================================="
echo ""

cd /home/user/webapp

echo "📦 Step 1: Delete old data..."
docker-compose exec backend python manage.py shell << 'PYTHON'
from apps.tenants.models import Tenant
from apps.products.models import Product, Category
from apps.users.models import User
from django.contrib.auth import get_user_model

# Delete all data (careful!)
print("Deleting existing data...")
Product.all_objects.all().delete()
Category.all_objects.all().delete()
Tenant.objects.all().delete()
print("✓ Old data deleted")
PYTHON

echo ""
echo "🌱 Step 2: Creating 5 Food Court Tenants..."
docker-compose exec backend python manage.py seed_foodcourt

echo ""
echo "=================================================="
echo "✅ FOOD COURT SETUP COMPLETE!"
echo "=================================================="
echo ""
echo "📊 Verification:"
echo ""

# Count data
echo "Checking database..."
docker-compose exec backend python manage.py shell << 'PYTHON'
from apps.tenants.models import Tenant
from apps.products.models import Product, Category

tenants = Tenant.objects.all()
print(f"\n✓ Tenants: {tenants.count()}")
for tenant in tenants:
    product_count = Product.all_objects.filter(tenant=tenant).count()
    print(f"  • {tenant.name}: {product_count} products - Color: {tenant.primary_color}")

print(f"\n✓ Total Products: {Product.all_objects.count()}")
print(f"✓ Total Categories: {Category.all_objects.count()}")
PYTHON

echo ""
echo "🧪 Testing API endpoints..."
echo ""

echo "1. Get ALL products (should show ~34 products from 5 tenants):"
curl -s http://localhost:8001/api/products/products/ | jq '.results | length'
echo ""

echo "2. Get tenants list:"
curl -s http://localhost:8001/api/products/products/ | jq '[.results[].tenant_name] | unique'
echo ""

echo "3. Sample products by tenant:"
curl -s http://localhost:8001/api/products/products/ | jq '.results[:3] | .[] | {name, tenant_name, tenant_color, price}'
echo ""

echo "=================================================="
echo "🌐 READY TO TEST!"
echo "=================================================="
echo ""
echo "Open: http://localhost:5174/kiosk"
echo ""
echo "Expected behavior:"
echo "  ✓ Page shows ALL 34 products from 5 tenants"
echo "  ✓ Tenant filter tabs show 5 restaurants"
echo "  ✓ Clicking tenant filters products"
echo "  ✓ Each product has tenant badge with color"
echo "  ✓ Cart groups items by tenant"
echo ""
echo "🏪 Tenants:"
echo "  • Warung Nasi Padang (orange)"
echo "  • Mie Ayam & Bakso (yellow)"
echo "  • Ayam Geprek Mantap (red)"
echo "  • Soto Betawi H. Mamat (gold)"
echo "  • Nasi Goreng Abang (green)"
echo ""
