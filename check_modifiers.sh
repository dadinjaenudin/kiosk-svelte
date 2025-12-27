#!/bin/bash
echo "🔍 Checking Product Modifiers in Database..."
echo ""

docker exec kiosk-svelte-backend-1 python manage.py shell << 'PYTHON'
from apps.products.models import Product, ProductModifier

products = Product.objects.all()
total_modifiers = ProductModifier.objects.count()

print(f"📦 Total Products: {products.count()}")
print(f"🔧 Total Modifiers: {total_modifiers}")
print("")

if products.count() > 0:
    print("Sample Products with Modifiers:")
    print("-" * 50)
    for p in products[:5]:
        modifiers = p.modifiers.all()
        print(f"\n{p.name} (Rp {p.price})")
        print(f"  Modifiers: {modifiers.count()}")
        for m in modifiers[:5]:
            print(f"    - {m.name} ({m.type}): +Rp {m.price_adjustment}")
else:
    print("❌ No products found! Run: python manage.py seed_foodcourt")

PYTHON
