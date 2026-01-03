#!/usr/bin/env python
"""Check products in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Product, Category
from apps.tenants.models import Tenant

print(f"Total Tenants: {Tenant.objects.count()}")
print(f"Total Categories: {Category.objects.count()}")
print(f"Total Products: {Product.objects.count()}")

print("\n=== Sample Categories ===")
for cat in Category.objects.all()[:5]:
    print(f"  - {cat.name} (Active: {cat.is_active}, Tenant: {cat.tenant.name if cat.tenant else 'None'})")

print("\n=== Sample Products ===")
for prod in Product.objects.all()[:10]:
    print(f"  - {prod.name} | Category: {prod.category.name if prod.category else 'None'} | Price: {prod.price} | Tenant: {prod.tenant.name if prod.tenant else 'None'}")
