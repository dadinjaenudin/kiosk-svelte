import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Product

products = Product.objects.all()[:5]
for p in products:
    print(f"Product: {p.name}")
    print(f"  Has image: {bool(p.image)}")
    print(f"  Image field: {repr(p.image)}")
    if p.image:
        print(f"  Image name: {p.image.name}")
    print()
