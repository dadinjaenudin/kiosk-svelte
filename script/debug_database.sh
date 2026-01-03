#!/bin/bash

# Debug Script - Check Database State

echo "=================================================="
echo "🔍 DATABASE DEBUG - Checking Tenant & Product Data"
echo "=================================================="
echo ""

cd /home/user/webapp

echo "Step 1: Check Tenants..."
docker-compose exec -T backend python manage.py shell << 'PYTHON'
from apps.tenants.models import Tenant
from apps.products.models import Product, Category

print("\n" + "="*60)
print("TENANTS IN DATABASE")
print("="*60)
tenants = Tenant.objects.all()
for t in tenants:
    product_count = Product.all_objects.filter(tenant=t).count()
    print(f"{t.id}. {t.name} - {product_count} products - Color: {t.primary_color}")

print("\n" + "="*60)
print("PRODUCTS WITHOUT TENANT")
print("="*60)
orphan_products = Product.all_objects.filter(tenant_id__isnull=True)
if orphan_products.exists():
    print(f"⚠️  Found {orphan_products.count()} products without tenant:")
    for p in orphan_products[:5]:
        print(f"  - {p.id}: {p.name} (SKU: {p.sku})")
else:
    print("✓ All products have tenant assigned")

print("\n" + "="*60)
print("PRODUCTS SUMMARY")
print("="*60)
print(f"Total Products: {Product.all_objects.count()}")
print(f"With Tenant: {Product.all_objects.exclude(tenant_id=None).count()}")
print(f"Without Tenant: {Product.all_objects.filter(tenant_id__isnull=True).count()}")

print("\n" + "="*60)
print("CATEGORIES SUMMARY")
print("="*60)
print(f"Total Categories: {Category.all_objects.count()}")

PYTHON

echo ""
echo "Step 2: Check API Response..."
echo ""
echo "▶ GET /api/products/products/ (first 3 products):"
curl -s http://localhost:8001/api/products/products/ | jq '.results[:3] | .[] | {id, name, tenant_id, tenant_name, sku}'

echo ""
echo "Step 3: Check specific product details..."
echo ""
echo "▶ Product ID 1:"
curl -s http://localhost:8001/api/products/products/1/ | jq '{id, name, tenant_id, tenant_name, tenant_color, price}'

echo ""
echo "=================================================="
echo "📊 DIAGNOSIS COMPLETE"
echo "=================================================="
echo ""
echo "Issues to check:"
echo "1. Are there 6 tenants (should be 5 for food court)?"
echo "2. Are there products without tenant_id?"
echo "3. Does API return tenant_id, tenant_name, tenant_color?"
echo ""
echo "If issues found, run: ./clean_and_reseed.sh"
echo ""
