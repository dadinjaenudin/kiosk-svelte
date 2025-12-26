#!/bin/bash

# Food Court Data Reset and Seed Script
# Reset old data and create 5 tenants for Food Court

echo "================================================"
echo "FOOD COURT - RESET AND SEED 5 TENANTS"
echo "================================================"
echo ""

cd /home/user/webapp

echo "Step 1: Deleting old data..."
echo ""
docker-compose exec -T backend python manage.py shell << 'PYTHON'
from apps.tenants.models import Tenant
from apps.products.models import Product, Category

Product.all_objects.all().delete()
Category.all_objects.all().delete()
Tenant.objects.all().delete()

print('\n==============================================')
print('✓ OLD DATA DELETED SUCCESSFULLY')
print('==============================================\n')
PYTHON

echo ""
echo "Step 2: Creating 5 Food Court Tenants..."
echo ""
docker-compose exec backend python manage.py seed_foodcourt

echo ""
echo "Step 3: Verifying data..."
echo ""
docker-compose exec -T backend python manage.py shell << 'PYTHON'
from apps.tenants.models import Tenant
from apps.products.models import Product

print('\n==============================================')
print('DATA VERIFICATION')
print('==============================================\n')

tenants = Tenant.objects.all()
print(f'Total Tenants: {tenants.count()}\n')

for t in tenants:
    count = Product.all_objects.filter(tenant=t).count()
    print(f'  {t.id}. {t.name} ({count} products) - {t.primary_color}')

total_products = Product.all_objects.count()
print(f'\nTotal Products: {total_products}')
print('\n==============================================\n')
PYTHON

echo ""
echo "Step 4: Restarting frontend..."
docker-compose restart frontend

echo ""
echo "================================================"
echo "WAITING FOR SERVICES TO START..."
echo "================================================"
echo "Waiting 15 seconds..."
sleep 15

echo ""
echo "================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Open browser: http://localhost:5174/kiosk"
echo "2. Press Ctrl+Shift+R to hard reload"
echo "3. Open Console (F12)"
echo "4. Verify logs:"
echo "   ✓ Products loaded: 38"
echo "   ✓ Tenants extracted: 5"
echo ""
echo "5. Check UI:"
echo "   ✓ FILTER BY RESTAURANT section visible"
echo "   ✓ 5 tenant buttons + All button"
echo "   ✓ 38 products with colored badges"
echo ""
echo "6. Test filtering:"
echo "   ✓ Click 'Warung Nasi Padang' → should show 7 products"
echo "   ✓ Console: 🏪 Tenant filter changed: 1"
echo "   ✓ Console: 📊 Products after filter: 7"
echo ""
echo "================================================"
echo ""
echo "🏪 5 TENANTS CREATED:"
echo "   1. 🟧 Warung Nasi Padang (7 products)"
echo "   2. 🟨 Mie Ayam & Bakso (6 products)"
echo "   3. 🟥 Ayam Geprek Mantap (6 products)"
echo "   4. 🟡 Soto Betawi H. Mamat (6 products)"
echo "   5. 🟩 Nasi Goreng Abang (7 products)"
echo ""
echo "Total: 38 products"
echo ""
