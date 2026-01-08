#!/usr/bin/env python
"""Check products by outlet"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Product
from apps.tenants.models import Outlet

print(f"Total Outlets: {Outlet.objects.count()}")
print(f"Total Products (all_objects): {Product.all_objects.count()}")

print("\n=== Products by Outlet ===")
for outlet in Outlet.objects.all():
    products = Product.all_objects.filter(outlet=outlet)
    if products.exists():
        stores_count = outlet.stores.count()
        print(f"\n{outlet.brand_name} (ID: {outlet.id}, Tenant: {outlet.tenant.name}, {stores_count} stores):")
        for prod in products[:5]:
            print(f"  - ID: {prod.id} | {prod.name} | Price: {prod.price}")
        if products.count() > 5:
            print(f"  ... and {products.count() - 5} more")
