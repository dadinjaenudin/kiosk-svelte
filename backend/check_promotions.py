#!/usr/bin/env python
"""Check promotions data in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.promotions.models import Promotion
from apps.tenants.models import Tenant

print("\n=== PROMOTIONS DATA ===\n")
promos = Promotion.objects.all()
print(f"Total Promotions: {promos.count()}\n")

for p in promos:
    tenant_name = p.tenant.name if p.tenant else "All Tenants"
    print(f"ID: {p.id}")
    print(f"  Name: {p.name}")
    print(f"  Type: {p.promo_type}")
    print(f"  Tenant: {tenant_name}")
    print(f"  Active: {p.is_active}")
    print(f"  Discount: {p.discount_value}")
    print()

print("\n=== TENANTS ===")
tenants = Tenant.objects.all()
for t in tenants:
    print(f"{t.id}. {t.name}")
