#!/usr/bin/env python
"""Quick script to check if data exists in database"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

from apps.products.models import Product, Category
from apps.tenants.models import Tenant, Outlet
from django.contrib.auth import get_user_model

User = get_user_model()

print("📊 Database Check:")
print(f"  Tenants: {Tenant.objects.count()}")
print(f"  Outlets: {Outlet.objects.count()}")
print(f"  Users: {User.objects.count()}")
print(f"  Categories: {Category.objects.count()}")
print(f"  Products: {Product.objects.count()}")
print("")

if Product.objects.count() == 0:
    print("❌ No products found!")
    print("Run: docker-compose exec backend python manage.py seed_demo_data")
else:
    print("✅ Products exist:")
    for product in Product.objects.all()[:5]:
        print(f"  - {product.name}: Rp {product.price:,.0f}")
