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
from apps.core.context import clear_tenant_context

User = get_user_model()

# Clear tenant context to see all data
clear_tenant_context()

print("📊 Database Check:")
print(f"  Tenants: {Tenant.objects.count()}")
print(f"  Outlets: {Outlet.objects.count()}")
print(f"  Users: {User.objects.count()}")

# Use filter() instead of direct count() to bypass TenantManager temporarily
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]

print(f"  Categories: {cat_count}")
print(f"  Products: {prod_count}")
print("")

if prod_count == 0:
    print("❌ No products found!")
    print("Run: docker-compose exec backend python manage.py seed_demo_data")
else:
    print("✅ Products exist:")
    # Query directly from DB to bypass manager
    with connection.cursor() as cursor:
        cursor.execute("SELECT name, price FROM products LIMIT 5")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: Rp {row[1]:,.0f}")
