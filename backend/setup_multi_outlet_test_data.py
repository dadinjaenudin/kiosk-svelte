#!/usr/bin/env python
"""
Multi-Outlet RBAC Testing Data Setup Script
Creates test data with outlets, tenant_owner role, and outlet assignments
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from apps.tenants.models import Tenant, Outlet
from apps.products.models import Category, Product, ProductModifier
from apps.orders.models import Order
from apps.promotions.models import Promotion
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

User = get_user_model()

@transaction.atomic
def reset_data():
    """Clear all test data"""
    print("🗑️  Clearing existing data...")
    
    # Delete in reverse dependency order
    Order.objects.all().delete()
    Promotion.objects.all().delete()
    ProductModifier.objects.all().delete()
    Product.all_objects.all().delete()
    Category.all_objects.all().delete()
    Outlet.objects.all().delete()
    
    # Delete test users
    User.objects.filter(username__in=[
        'admin', 'superadmin',
        'pizza_owner', 'pizza_manager', 'pizza_cashier', 'pizza_cashier2', 'pizza_kitchen', 'pizza_kitchen2',
        'burger_owner', 'burger_manager', 'burger_cashier', 'burger_cashier2', 'burger_kitchen', 'burger_kitchen2',
        'noodle_owner', 'noodle_manager', 'noodle_cashier', 'noodle_cashier2', 'noodle_kitchen', 'noodle_kitchen2'
    ]).delete()
    
    Tenant.objects.all().delete()
    
    print("✅ All test data cleared")


@transaction.atomic
def create_tenants():
    """Create 3 test tenants"""
    print("\n🏢 Creating tenants...")
    
    tenants_data = [
        {
            'name': 'Pizza Paradise',
            'slug': 'pizza-paradise',
            'description': 'Italian pizza restaurant',
            'email': 'info@pizzaparadise.com',
            'phone': '+62811111111',
            'primary_color': '#E74C3C'
        },
        {
            'name': 'Burger Station',
            'slug': 'burger-station',
            'description': 'American burger joint',
            'email': 'info@burgerstation.com',
            'phone': '+62822222222',
            'primary_color': '#F39C12'
        },
        {
            'name': 'Noodle House',
            'slug': 'noodle-house',
            'description': 'Asian noodle restaurant',
            'email': 'info@noodlehouse.com',
            'phone': '+62833333333',
            'primary_color': '#3498DB'
        }
    ]
    
    tenants = []
    for data in tenants_data:
        tenant = Tenant.objects.create(**data)
        tenants.append(tenant)
        print(f"  ✓ Created: {tenant.name}")
    
    return tenants


@transaction.atomic
def create_outlets(tenants):
    """Create 2 outlets for each tenant"""
    print("\n📍 Creating outlets...")
    
    outlets = {}
    
    # Pizza Paradise outlets
    outlets['pizza'] = []
    for i, name_suffix in enumerate(['Main Branch', 'North Branch'], 1):
        outlet = Outlet.objects.create(
            tenant=tenants[0],
            name=f'Pizza Paradise - {name_suffix}',
            slug=f'pizza-{name_suffix.lower().replace(" ", "-")}',
            address=f'Jl. Sudirman No. {100+i}, Jakarta',
            phone=f'+6281111111{i}',
            is_active=True
        )
        outlets['pizza'].append(outlet)
        print(f"  ✓ {outlet.name}")
    
    # Burger Station outlets
    outlets['burger'] = []
    for i, name_suffix in enumerate(['Central', 'West'], 1):
        outlet = Outlet.objects.create(
            tenant=tenants[1],
            name=f'Burger Station - {name_suffix}',
            slug=f'burger-{name_suffix.lower()}',
            address=f'Jl. Gatot Subroto No. {200+i}, Jakarta',
            phone=f'+6282222222{i}',
            is_active=True
        )
        outlets['burger'].append(outlet)
        print(f"  ✓ {outlet.name}")
    
    # Noodle House outlets
    outlets['noodle'] = []
    for i, name_suffix in enumerate(['Downtown', 'East'], 1):
        outlet = Outlet.objects.create(
            tenant=tenants[2],
            name=f'Noodle House - {name_suffix}',
            slug=f'noodle-{name_suffix.lower()}',
            address=f'Jl. Kuningan No. {300+i}, Jakarta',
            phone=f'+6283333333{i}',
            is_active=True
        )
        outlets['noodle'].append(outlet)
        print(f"  ✓ {outlet.name}")
    
    return outlets


@transaction.atomic
def create_users(tenants, outlets):
    """Create test users with outlet assignments"""
    print("\n👥 Creating users...")
    
    # Super Admin
    super_admin = User.objects.create_user(
        username='superadmin',
        email='superadmin@kiosk.com',
        password='admin123',
        role='super_admin',
        is_superuser=True,
        is_staff=True
    )
    print(f"  ✓ superadmin (super_admin) - ALL TENANTS")
    
    # Admin
    admin = User.objects.create_user(
        username='admin',
        email='admin@kiosk.com',
        password='admin123',
        role='admin',
        is_staff=True
    )
    print(f"  ✓ admin (admin) - ALL TENANTS")
    
    users = {}
    
    # Create users for each tenant
    for i, tenant in enumerate(tenants):
        prefix = tenant.name.split()[0].lower()
        tenant_outlets = outlets[prefix]
        
        # Tenant Owner
        owner = User.objects.create_user(
            username=f'{prefix}_owner',
            email=f'owner@{prefix}.com',
            password='owner123',
            role='tenant_owner',
            tenant=tenant,
            outlet=tenant_outlets[0]
        )
        print(f"  ✓ {owner.username} (tenant_owner) - {tenant.name} - ALL OUTLETS")
        
        # Manager
        manager = User.objects.create_user(
            username=f'{prefix}_manager',
            email=f'manager@{prefix}.com',
            password='manager123',
            role='manager',
            tenant=tenant,
            outlet=tenant_outlets[0]
        )
        manager.accessible_outlets.add(*tenant_outlets)
        print(f"  ✓ {manager.username} (manager) - Both outlets")
        
        # Cashier 1 (Main)
        cashier1 = User.objects.create_user(
            username=f'{prefix}_cashier',
            email=f'cashier@{prefix}.com',
            password='cashier123',
            role='cashier',
            tenant=tenant,
            outlet=tenant_outlets[0]
        )
        print(f"  ✓ {cashier1.username} (cashier) - {tenant_outlets[0].name}")
        
        # Cashier 2 (Branch 2)
        cashier2 = User.objects.create_user(
            username=f'{prefix}_cashier2',
            email=f'cashier2@{prefix}.com',
            password='cashier123',
            role='cashier',
            tenant=tenant,
            outlet=tenant_outlets[1]
        )
        print(f"  ✓ {cashier2.username} (cashier) - {tenant_outlets[1].name}")
        
        # Kitchen 1 (Main)
        kitchen1 = User.objects.create_user(
            username=f'{prefix}_kitchen',
            email=f'kitchen@{prefix}.com',
            password='kitchen123',
            role='kitchen',
            tenant=tenant,
            outlet=tenant_outlets[0]
        )
        print(f"  ✓ {kitchen1.username} (kitchen) - {tenant_outlets[0].name}")
        
        # Kitchen 2 (Branch 2)
        kitchen2 = User.objects.create_user(
            username=f'{prefix}_kitchen2',
            email=f'kitchen2@{prefix}.com',
            password='kitchen123',
            role='kitchen',
            tenant=tenant,
            outlet=tenant_outlets[1]
        )
        print(f"  ✓ {kitchen2.username} (kitchen) - {tenant_outlets[1].name}")
    
    return users


@transaction.atomic
def create_categories(tenants):
    """Create categories"""
    print("\n📁 Creating categories...")
    
    categories = {}
    
    category_data = {
        'pizza': [('Pizza', 'Pizzas'), ('Beverages', 'Drinks'), ('Sides', 'Sides')],
        'burger': [('Burgers', 'Burgers'), ('Fries', 'Fries'), ('Drinks', 'Drinks')],
        'noodle': [('Noodles', 'Noodles'), ('Soup', 'Soups'), ('Appetizers', 'Appetizers')]
    }
    
    for i, tenant in enumerate(tenants):
        prefix = tenant.name.split()[0].lower()
        categories[prefix] = []
        
        for name, desc in category_data[prefix]:
            cat = Category.all_objects.create(
                name=name,
                description=desc,
                tenant=tenant,
                is_active=True
            )
            categories[prefix].append(cat)
            print(f"  ✓ {tenant.name}: {cat.name}")
    
    return categories


@transaction.atomic
def create_products(tenants, categories, outlets):
    """Create products with outlet assignments"""
    print("\n🍕 Creating products...")
    
    # Product data: (name, sku_suffix, category_idx, price, stock, outlet_idx or None)
    product_data = {
        'pizza': [
            ('Margherita Pizza', '001', 0, 85000, 10, 0),  # Main branch only
            ('Pepperoni Pizza', '002', 0, 95000, 8, 1),    # North branch only
            ('Coca Cola', 'BEV-001', 1, 15000, 50, None),  # All outlets
            ('Garlic Bread', 'SIDE-001', 2, 25000, 20, None)  # All outlets
        ],
        'burger': [
            ('Classic Burger', '001', 0, 45000, 15, 0),    # Central only
            ('Cheese Burger', '002', 0, 55000, 12, 1),     # West only
            ('French Fries', 'SIDE-001', 1, 20000, 30, None),  # All outlets
            ('Iced Tea', 'BEV-001', 2, 12000, 40, None)   # All outlets
        ],
        'noodle': [
            ('Ramen Bowl', '001', 0, 40000, 20, 0),        # Downtown only
            ('Pad Thai', '002', 0, 38000, 18, 1),          # East only
            ('Tom Yum Soup', 'SOUP-001', 1, 35000, 15, None),  # All outlets
            ('Spring Rolls', 'APP-001', 2, 22000, 25, None)  # All outlets
        ]
    }
    
    for i, tenant in enumerate(tenants):
        prefix = tenant.name.split()[0].lower()
        tenant_outlets = outlets[prefix]
        tenant_categories = categories[prefix]
        
        for name, sku_suffix, cat_idx, price, stock, outlet_idx in product_data[prefix]:
            outlet = tenant_outlets[outlet_idx] if outlet_idx is not None else None
            
            Product.all_objects.create(
                name=name,
                sku=f'{prefix.upper()}-{sku_suffix}',
                category=tenant_categories[cat_idx],
                tenant=tenant,
                outlet=outlet,
                price=Decimal(str(price)),
                stock_quantity=stock,
                is_available=True,
                is_active=True,
                track_stock=True
            )
            
            outlet_info = outlet.name if outlet else "All Outlets"
            print(f"  ✓ {tenant.name}: {name} - Rp {price:,} - {outlet_info}")


@transaction.atomic
def create_spicy_levels(tenants):
    """Create spicy level modifiers (global for all products)"""
    print("\n🌶️  Creating spicy levels...")
    
    spicy_levels = [
        {'name': 'Level 1 (Tidak Pedas)', 'sort': 1, 'price': 0},
        {'name': 'Level 2 (Sedang)', 'sort': 2, 'price': 0},
        {'name': 'Level 3 (Pedas)', 'sort': 3, 'price': 0},
        {'name': 'Level 4 (Sangat Pedas)', 'sort': 4, 'price': 0},
        {'name': 'Level 5 (Extra Pedas)', 'sort': 5, 'price': 0},
    ]
    
    # Create global spicy levels (no product = available for all products)
    for level in spicy_levels:
        ProductModifier.objects.create(
            name=level['name'],
            type='spicy',
            price_adjustment=Decimal(str(level['price'])),
            product=None,  # Global = available for all products
            is_active=True,
            sort_order=level['sort']
        )
        print(f"  ✓ Global: {level['name']}")
    
    print(f"  📊 Total spicy levels created: {len(spicy_levels)} (global for all products)")


@transaction.atomic
def create_toppings(tenants):
    """Create topping modifiers (global for all products)"""
    print("\n🧀 Creating toppings...")
    
    toppings = [
        {'name': 'Extra Cheese', 'sort': 1, 'price': 5000},
        {'name': 'Mushrooms', 'sort': 2, 'price': 3000},
        {'name': 'Olives', 'sort': 3, 'price': 3000},
        {'name': 'Onions', 'sort': 4, 'price': 2000},
        {'name': 'Tomatoes', 'sort': 5, 'price': 2000},
    ]
    
    # Create global toppings
    for topping in toppings:
        ProductModifier.objects.create(
            name=topping['name'],
            type='topping',
            price_adjustment=Decimal(str(topping['price'])),
            product=None,  # Global = available for all products
            is_active=True,
            sort_order=topping['sort']
        )
        print(f"  ✓ Global: {topping['name']} (+Rp {topping['price']:,})")
    
    print(f"  📊 Total toppings created: {len(toppings)} (global for all products)")


@transaction.atomic
def create_promotions(tenants):
    """Create promotions"""
    print("\n🎉 Creating promotions...")
    
    now = timezone.now()
    
    promos = [
        {
            'tenant': tenants[0],
            'name': 'Weekend Special',
            'code': 'WEEKEND20',
            'promo_type': 'percentage',
            'discount_value': 20
        },
        {
            'tenant': tenants[1],
            'name': 'Combo Deal',
            'code': 'COMBO60',
            'promo_type': 'fixed',
            'discount_value': 15000
        },
        {
            'tenant': tenants[2],
            'name': 'Lunch Special',
            'code': 'LUNCH10K',
            'promo_type': 'fixed',
            'discount_value': 10000
        }
    ]
    
    for promo_data in promos:
        Promotion.objects.create(
            **promo_data,
            description='Test promotion',
            start_date=now,
            end_date=now + timedelta(days=30),
            status='active',
            is_active=True
        )
        print(f"  ✓ {promo_data['tenant'].name}: {promo_data['name']}")


def print_summary():
    """Print summary"""
    print("\n" + "="*80)
    print("🎯 MULTI-OUTLET TEST DATA SETUP COMPLETE")
    print("="*80)
    
    print("\n📊 TEST ACCOUNTS:")
    print("-" * 80)
    print(f"{'Username':<25} {'Password':<15} {'Role':<15} {'Details':<25}")
    print("-" * 80)
    print(f"{'superadmin':<25} {'admin123':<15} {'super_admin':<15} {'ALL TENANTS':<25}")
    print(f"{'admin':<25} {'admin123':<15} {'admin':<15} {'ALL TENANTS':<25}")
    print("-" * 80)
    
    for tenant_prefix in ['pizza', 'burger', 'noodle']:
        print(f"{tenant_prefix}_owner".ljust(25) + f"{'owner123':<15} {'tenant_owner':<15} {'All outlets':<25}")
        print(f"{tenant_prefix}_manager".ljust(25) + f"{'manager123':<15} {'manager':<15} {'Both outlets':<25}")
        print(f"{tenant_prefix}_cashier".ljust(25) + f"{'cashier123':<15} {'cashier':<15} {'Main branch':<25}")
        print(f"{tenant_prefix}_cashier2".ljust(25) + f"{'cashier123':<15} {'cashier':<15} {'Branch 2':<25}")
        print(f"{tenant_prefix}_kitchen".ljust(25) + f"{'kitchen123':<15} {'kitchen':<15} {'Main branch':<25}")
        print(f"{tenant_prefix}_kitchen2".ljust(25) + f"{'kitchen123':<15} {'kitchen':<15} {'Branch 2':<25}")
        print("-" * 80)
    
    print("\n📝 SUMMARY:")
    print(f"  • Tenants: {Tenant.objects.count()}")
    print(f"  • Outlets: {Outlet.objects.count()} (2 per tenant)")
    print(f"  • Users: {User.objects.count()}")
    print(f"  • Products: {Product.all_objects.count()} (4 per tenant)")
    print(f"  • Categories: {Category.all_objects.count()}")
    print(f"  • Toppings: {ProductModifier.objects.filter(type='topping').count()}")
    print(f"  • Spicy Levels: {ProductModifier.objects.filter(type='spicy').count()}")
    print(f"  • Promotions: {Promotion.objects.count()}")
    
    print("\n🔗 NEXT STEPS:")
    print("  1. Login to admin panel: http://localhost:5175/")
    print("  2. Test outlet switching with different roles")
    print("  3. Verify product filtering by outlet")
    print("\n✨ Multi-outlet system ready for testing!\n")


def main():
    """Main execution"""
    print("="*80)
    print("🚀 MULTI-OUTLET TEST DATA SETUP")
    print("="*80)
    
    # Warning about data deletion
    print("\n⚠️  WARNING: This script will DELETE ALL existing data!")
    print("   - All orders will be deleted")
    print("   - All customers will be deleted")
    print("   - All products will be deleted")
    print("   - All categories will be deleted")
    print("   - All outlets will be deleted")
    print("   - All tenants will be deleted")
    print("   - All users (except superusers) will be deleted")
    print("\n   New test data will be created:")
    print("   - 3 Tenants (Pizza, Burger, Noodle)")
    print("   - 6 Outlets (2 per tenant)")
    print("   - 12 Categories")
    print("   - 30 Products")
    print("   - 5 Spicy Levels (Level 1-5)")
    print("   - 5 Toppings (Global)")
    print("   - 20 Users (various roles)")
    
    response = input("\n❓ Continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Setup cancelled by user.")
        sys.exit(0)
    
    print("\n🗑️  Clearing existing data...\n")
    
    try:
        reset_data()
        tenants = create_tenants()
        outlets = create_outlets(tenants)
        users = create_users(tenants, outlets)
        categories = create_categories(tenants)
        create_products(tenants, categories, outlets)
        create_toppings(tenants)
        create_spicy_levels(tenants)
        create_promotions(tenants)
        print_summary()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
