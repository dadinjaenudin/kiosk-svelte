#!/bin/bash

# Clean Database and Reseed with Fresh Food Court Data

echo "=================================================="
echo "🧹 CLEAN & RESEED - Food Court Database"
echo "=================================================="
echo ""

cd /home/user/webapp

echo "⚠️  WARNING: This will DELETE all existing data!"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Step 1: Deleting ALL data from database..."
docker-compose exec -T backend python manage.py shell << 'PYTHON'
from apps.products.models import Product, Category, ProductModifier
from apps.tenants.models import Tenant, Outlet
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.users.models import User

print("\n🗑️  Deleting data...")
OrderItem.objects.all().delete()
Order.objects.all().delete()
Payment.objects.all().delete()
ProductModifier.all_objects.all().delete()
Product.all_objects.all().delete()
Category.all_objects.all().delete()
Outlet.objects.all().delete()

# Don't delete superuser
User.objects.filter(is_superuser=False).delete()

# Delete tenants
Tenant.objects.all().delete()

print("✓ All data deleted (except superuser)")
PYTHON

echo ""
echo "Step 2: Creating 5 Food Court Tenants..."
docker-compose exec backend python manage.py seed_foodcourt

echo ""
echo "Step 3: Verifying data..."
docker-compose exec -T backend python manage.py shell << 'PYTHON'
from apps.tenants.models import Tenant
from apps.products.models import Product

print("\n" + "="*60)
print("VERIFICATION RESULTS")
print("="*60)

tenants = Tenant.objects.all()
print(f"\nTenants: {tenants.count()} (expected: 5)")
for t in tenants:
    count = Product.all_objects.filter(tenant=t).count()
    print(f"  {t.id}. {t.name}: {count} products - {t.primary_color}")

total_products = Product.all_objects.count()
print(f"\nTotal Products: {total_products} (expected: ~38)")

orphans = Product.all_objects.filter(tenant_id__isnull=True).count()
if orphans > 0:
    print(f"⚠️  Products without tenant: {orphans}")
else:
    print("✓ All products have tenant")

print("\n" + "="*60)
PYTHON

echo ""
echo "=================================================="
echo "✅ CLEAN & RESEED COMPLETE"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Restart frontend: docker-compose restart frontend"
echo "2. Clear browser data:"
echo "   F12 → Console → indexedDB.deleteDatabase('POSDatabase')"
echo "3. Hard reload: Ctrl+Shift+R"
echo "4. Test checkout"
echo ""
