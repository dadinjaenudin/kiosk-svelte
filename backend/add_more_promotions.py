#!/usr/bin/env python
"""Add more promotions with different types for each tenant"""
import os
import django
from decimal import Decimal
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from apps.promotions.models import Promotion
from apps.tenants.models import Tenant
from apps.products.models import Product

print("\n=== Adding More Promotions ===\n")

# Get tenants
pizza = Tenant.objects.get(name="Pizza Paradise")
burger = Tenant.objects.get(name="Burger Station")
noodle = Tenant.objects.get(name="Noodle House")

# Get some products for bundle promotions
pizza_products = Product.objects.filter(tenant=pizza)
burger_products = Product.objects.filter(tenant=burger)
noodle_products = Product.objects.filter(tenant=noodle)

now = timezone.now()
tomorrow = now + timedelta(days=1)
next_week = now + timedelta(days=7)
next_month = now + timedelta(days=30)

promotions_data = [
    # Pizza Paradise - More variety
    {
        'tenant': pizza,
        'name': 'Happy Hour Pizza',
        'description': '15% off on all pizzas from 2-5 PM',
        'code': 'HAPPYHOUR15',
        'promo_type': 'percentage',
        'discount_value': Decimal('15.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
        'min_purchase_amount': Decimal('50000'),
    },
    {
        'tenant': pizza,
        'name': 'Large Pizza Deal',
        'description': 'Rp 25,000 off on large pizzas',
        'code': 'LARGE25K',
        'promo_type': 'fixed',
        'discount_value': Decimal('25000.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
        'min_purchase_amount': Decimal('80000'),
    },
    {
        'tenant': pizza,
        'name': 'Buy 2 Get 1 Free Pizza',
        'description': 'Buy 2 pizzas get 1 free (cheapest free)',
        'code': 'BUY2GET1',
        'promo_type': 'buy_x_get_y',
        'buy_quantity': 2,
        'get_quantity': 1,
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
    },
    {
        'tenant': pizza,
        'name': 'Family Bundle',
        'description': '2 Large Pizzas + 2 Drinks for special price',
        'code': 'FAMILY99K',
        'promo_type': 'bundle',
        'discount_value': Decimal('30000.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
    },
    
    # Burger Station - More variety
    {
        'tenant': burger,
        'name': 'Student Discount',
        'description': '20% off for students with valid ID',
        'code': 'STUDENT20',
        'promo_type': 'percentage',
        'discount_value': Decimal('20.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
        'min_purchase_amount': Decimal('30000'),
    },
    {
        'tenant': burger,
        'name': 'Mega Burger Discount',
        'description': 'Rp 20,000 off on mega burgers',
        'code': 'MEGA20K',
        'promo_type': 'fixed',
        'discount_value': Decimal('20000.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
        'min_purchase_amount': Decimal('60000'),
    },
    {
        'tenant': burger,
        'name': 'Buy 3 Get 1 Free',
        'description': 'Buy 3 burgers get 1 free',
        'code': 'BURGERBUY3',
        'promo_type': 'buy_x_get_y',
        'buy_quantity': 3,
        'get_quantity': 1,
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
    },
    {
        'tenant': burger,
        'name': 'Couple Bundle',
        'description': '2 Burgers + 2 Fries + 2 Drinks',
        'code': 'COUPLE79K',
        'promo_type': 'bundle',
        'discount_value': Decimal('25000.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
    },
    
    # Noodle House - More variety
    {
        'tenant': noodle,
        'name': 'Lunch Promo',
        'description': '25% off on all noodles 11 AM - 2 PM',
        'code': 'LUNCH25',
        'promo_type': 'percentage',
        'discount_value': Decimal('25.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
        'min_purchase_amount': Decimal('40000'),
    },
    {
        'tenant': noodle,
        'name': 'Ramen Discount',
        'description': 'Rp 15,000 off on all ramen bowls',
        'code': 'RAMEN15K',
        'promo_type': 'fixed',
        'discount_value': Decimal('15000.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
        'min_purchase_amount': Decimal('50000'),
    },
    {
        'tenant': noodle,
        'name': 'Buy 2 Ramen Get 1 Drink',
        'description': 'Buy 2 ramen bowls get 1 free drink',
        'code': 'RAMEN2DRINK',
        'promo_type': 'buy_x_get_y',
        'buy_quantity': 2,
        'get_quantity': 1,
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
    },
    {
        'tenant': noodle,
        'name': 'Noodle Feast',
        'description': '3 Noodles + 3 Drinks + Appetizer',
        'code': 'FEAST120K',
        'promo_type': 'bundle',
        'discount_value': Decimal('35000.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': True,
    },
    
    # Add some expired/scheduled promotions for testing
    {
        'tenant': pizza,
        'name': 'New Year Special (Expired)',
        'description': 'New year promotion - already expired',
        'code': 'NEWYEAR2025',
        'promo_type': 'percentage',
        'discount_value': Decimal('30.00'),
        'start_date': now - timedelta(days=30),
        'end_date': now - timedelta(days=1),
        'is_active': False,
    },
    {
        'tenant': burger,
        'name': 'Coming Soon: Summer Sale',
        'description': 'Starting next week!',
        'code': 'SUMMER30',
        'promo_type': 'percentage',
        'discount_value': Decimal('30.00'),
        'start_date': next_week,
        'end_date': next_month,
        'is_active': False,
    },
    {
        'tenant': noodle,
        'name': 'Paused: Holiday Special',
        'description': 'Temporarily paused',
        'code': 'HOLIDAY',
        'promo_type': 'fixed',
        'discount_value': Decimal('20000.00'),
        'start_date': now,
        'end_date': next_month,
        'is_active': False,
    },
]

created_count = 0
for promo_data in promotions_data:
    try:
        # Check if code already exists
        if promo_data.get('code'):
            existing = Promotion.objects.filter(code=promo_data['code']).first()
            if existing:
                print(f"⚠️  Skipping '{promo_data['name']}' - code already exists")
                continue
        
        promo = Promotion.objects.create(**promo_data)
        created_count += 1
        status = "✅ Active" if promo.is_active else "⏸️ Inactive"
        print(f"{status} Created: {promo.name} ({promo.promo_type}) - {promo.tenant.name}")
    except Exception as e:
        print(f"❌ Error creating '{promo_data['name']}': {str(e)}")

print(f"\n✅ Successfully created {created_count} new promotions!")
print(f"📊 Total promotions now: {Promotion.objects.count()}")

# Summary by tenant
print("\n=== Summary by Tenant ===")
for tenant in [pizza, burger, noodle]:
    count = Promotion.objects.filter(tenant=tenant).count()
    active = Promotion.objects.filter(tenant=tenant, is_active=True).count()
    print(f"{tenant.name}: {count} total ({active} active)")

# Summary by type
print("\n=== Summary by Type ===")
for promo_type, label in Promotion.TYPE_CHOICES:
    count = Promotion.objects.filter(promo_type=promo_type).count()
    print(f"{label}: {count}")
