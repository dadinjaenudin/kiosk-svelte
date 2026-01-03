import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Product

# Update all products with placeholder image
products = Product.all_objects.all()
count = 0

for product in products:
    product.image = 'products/mi-ayam.jpg'
    product.save()
    count += 1
    print(f"✅ {product.name} -> products/mi-ayam.jpg")

print(f"\n🎉 Updated {count} products")
