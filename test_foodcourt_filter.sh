#!/bin/bash

# Quick Test Script untuk Food Court Tenant Filter

echo "=================================================="
echo "🧪 FOOD COURT TENANT FILTER - QUICK TEST"
echo "=================================================="
echo ""

cd D:\YOGYA-Kiosk\kiosk-svelte

echo "Step 1: Pull latest code..."
git pull origin main
echo ""

echo "Step 2: Restart services..."
docker-compose restart backend frontend
echo "⏳ Waiting 15 seconds for services to start..."
sleep 15
echo ""

echo "Step 3: Run seed script..."
docker-compose exec backend python manage.py seed_foodcourt
echo ""

echo "Step 4: Verify data..."
echo ""

echo "📊 Checking tenants..."
docker-compose exec backend python manage.py shell << 'PYTHON'
from apps.tenants.models import Tenant
from apps.products.models import Product

print("\n🏪 TENANTS CREATED:")
print("=" * 60)
for t in Tenant.objects.all():
    count = Product.all_objects.filter(tenant=t).count()
    print(f"  {t.id}. {t.name} ({count} products) - Color: {t.primary_color}")

print(f"\n📊 TOTALS:")
print(f"  • Tenants: {Tenant.objects.count()}")
print(f"  • Products: {Product.all_objects.count()}")
print(f"  • Categories: {Product.all_objects.values('category').distinct().count()}")
PYTHON

echo ""
echo "Step 5: Test API..."
echo ""

echo "▶ Testing /api/products/products/ endpoint:"
PRODUCT_COUNT=$(curl -s http://localhost:8001/api/products/products/ | jq '.results | length')
echo "  ✓ Products returned: $PRODUCT_COUNT (expected: ~38)"
echo ""

echo "▶ Testing tenant extraction:"
curl -s http://localhost:8001/api/products/products/ | jq -r '.results[0] | "  ✓ Sample: \(.name) from \(.tenant_name) (\(.tenant_color))"'
echo ""

echo "=================================================="
echo "✅ SETUP COMPLETE!"
echo "=================================================="
echo ""
echo "🌐 Open Kiosk:"
echo "   http://localhost:5174/kiosk"
echo ""
echo "🧪 Testing Steps:"
echo ""
echo "1. Open Browser Console (F12)"
echo ""
echo "2. Check Console Logs:"
echo "   ✓ 'Products loaded: 38'"
echo "   ✓ 'Tenants extracted: 5'"
echo "   ✓ '🏪 Tenants: [...]'"
echo ""
echo "3. Verify UI:"
echo "   ✓ 'FILTER BY RESTAURANT:' section visible"
echo "   ✓ 'All Restaurants' + 5 tenant buttons"
echo "   ✓ ~38 products visible"
echo "   ✓ Each product has colored tenant badge"
echo ""
echo "4. Test Filtering:"
echo "   ✓ Click 'Warung Nasi Padang' → see 7 products"
echo "   ✓ Console shows: '🏪 Tenant filter changed: 1'"
echo "   ✓ Console shows: '📊 Products after filter: 7'"
echo "   ✓ Button highlighted with orange border"
echo ""
echo "5. Test Multi-Tenant Cart:"
echo "   ✓ Add Rendang Sapi (Nasi Padang)"
echo "   ✓ Add Mie Ayam (Mie Ayam & Bakso)"
echo "   ✓ Cart shows 2 groups with colors"
echo "   ✓ Subtotal per tenant"
echo "   ✓ Grand total shown"
echo ""
echo "=================================================="
echo "🏪 5 TENANTS:"
echo "=================================================="
echo ""
echo "1. 🟧 Warung Nasi Padang (Orange #FF6B35)"
echo "   • 7 products: Rendang, Ayam Pop, Gulai Ikan..."
echo ""
echo "2. 🟨 Mie Ayam & Bakso (Yellow #F7931E)"
echo "   • 6 products: Mie Ayam, Bakso Sapi, Bakso Urat..."
echo ""
echo "3. 🟥 Ayam Geprek Mantap (Red #DC143C)"
echo "   • 6 products: Geprek Original, Geprek Keju..."
echo ""
echo "4. 🟡 Soto Betawi H. Mamat (Gold #FFC300)"
echo "   • 6 products: Soto Daging, Soto Babat..."
echo ""
echo "5. 🟩 Nasi Goreng Abang (Green #28A745)"
echo "   • 7 products: Nasi Goreng Biasa, Spesial, Seafood..."
echo ""
echo "=================================================="
echo ""
echo "📝 Need help? Check: FOOD_COURT_5_TENANTS.md"
echo ""
