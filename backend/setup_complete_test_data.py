"""
Complete Test Data Setup Script - OPSI 2 Many-to-Many Architecture
Creates comprehensive sample data for multi-store multi-outlet system:
- 4 Tenants: YOGYA, BORMA, MATAHARI, CARREFOUR (Retail Companies)
- 12 Stores: 3 per tenant (Physical retail locations)
- 3 Global Brands: Chicken Sumo, Magic Oven, Magic Pizza
- StoreOutlet junction: Links brands to stores (M2M)
- 9 Categories: 3 per brand
- 27 Products: 9 per brand
- Kitchen stations per brand

⚠️  WARNING: This script will DELETE ALL existing data including:
- Orders, OrderGroups, OrderItems
- Customers
- Products, Categories, ProductModifiers
- Kitchen Stations
- Stores, Outlets, StoreOutlets
- Tenants

Run with caution!
"""

import os
import sys
import django
from datetime import time
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, Store, Outlet, StoreOutlet, KitchenStation
from apps.products.models import Category, Product, ProductModifier
from apps.customers.models import Customer
from apps.orders.models import Order, OrderItem, OrderGroup
from apps.core.context import set_current_tenant

User = get_user_model()


def clear_all_data():
    """Clear all existing data"""
    print("\n🗑️  Clearing existing data...")
    
    # Clear orders first (has FK to products)
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    OrderGroup.objects.all().delete()
    print("  ✅ Cleared orders")
    
    # Clear customers
    Customer.objects.all().delete()
    print("  ✅ Cleared customers")
    
    # Clear products and categories
    ProductModifier.objects.all().delete()
    Product.all_objects.all().delete()
    Category.all_objects.all().delete()
    print("  ✅ Cleared products & categories")
    
    KitchenStation.objects.all().delete()
    print("  ✅ Cleared kitchen stations")
    
    StoreOutlet.objects.all().delete()
    Outlet.objects.all().delete()
    Store.objects.all().delete()
    print("  ✅ Cleared stores, outlets, and junctions")
    
    Tenant.objects.all().delete()
    print("  ✅ Cleared tenants")
    
    print("✅ All data cleared!\n")


def create_tenants():
    """Create 4 retail company tenants"""
    print("🏢 Creating Tenants (Retail Companies)...")
    
    tenants_data = [
        {
            'name': 'YOGYA',
            'slug': 'yogya',
            'description': 'Yogya Department Store - Retail chain with food court',
            'primary_color': '#E74C3C',
            'secondary_color': '#C0392B',
            'tax_rate': Decimal('10.00'),
            'service_charge_rate': Decimal('5.00'),
        },
        {
            'name': 'BORMA',
            'slug': 'borma',
            'description': 'Borma Toserba - Supermarket chain with food court',
            'primary_color': '#3498DB',
            'secondary_color': '#2980B9',
            'tax_rate': Decimal('10.00'),
            'service_charge_rate': Decimal('5.00'),
        },
        {
            'name': 'MATAHARI',
            'slug': 'matahari',
            'description': 'Matahari Department Store - Retail chain',
            'primary_color': '#F39C12',
            'secondary_color': '#E67E22',
            'tax_rate': Decimal('10.00'),
            'service_charge_rate': Decimal('5.00'),
        },
        {
            'name': 'CARREFOUR',
            'slug': 'carrefour',
            'description': 'Carrefour - Hypermarket chain',
            'primary_color': '#27AE60',
            'secondary_color': '#229954',
            'tax_rate': Decimal('10.00'),
            'service_charge_rate': Decimal('5.00'),
        },
    ]
    
    tenants = {}
    for tenant_data in tenants_data:
        tenant = Tenant.objects.create(**tenant_data)
        tenants[tenant.slug] = tenant
        print(f"  ✅ {tenant.name}")
    
    return tenants


def create_stores(tenants):
    """Create 3 stores per tenant (12 total)"""
    print("\n📍 Creating Stores (Physical Locations)...")
    
    stores_data = [
        # YOGYA Stores
        {
            'tenant': tenants['yogya'],
            'code': 'YOGYA-KAPATIHAN',
            'name': 'Yogya Kapatihan',
            'address': 'Jl. Ahmad Yani No. 288, Kapatihan',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'postal_code': '40271',
            'opening_time': time(8, 0),
            'closing_time': time(21, 0),
        },
        {
            'tenant': tenants['yogya'],
            'code': 'YOGYA-RIAU',
            'name': 'Yogya Riau',
            'address': 'Jl. Riau No. 16',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(9, 0),
            'closing_time': time(22, 0),
        },
        {
            'tenant': tenants['yogya'],
            'code': 'YOGYA-SUNDA',
            'name': 'Yogya Sunda',
            'address': 'Jl. Sunda No. 42',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(8, 30),
            'closing_time': time(21, 30),
        },
        
        # BORMA Stores
        {
            'tenant': tenants['borma'],
            'code': 'BORMA-DAGO',
            'name': 'Borma Dago',
            'address': 'Jl. Ir. H. Juanda No. 135 (Dago)',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(8, 0),
            'closing_time': time(22, 0),
        },
        {
            'tenant': tenants['borma'],
            'code': 'BORMA-CIBIRU',
            'name': 'Borma Cibiru',
            'address': 'Jl. Cibiru Hilir No. 1',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(7, 30),
            'closing_time': time(21, 0),
        },
        {
            'tenant': tenants['borma'],
            'code': 'BORMA-KEBON-WARU',
            'name': 'Borma Kebon Waru',
            'address': 'Jl. Kebon Waru No. 8',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(8, 0),
            'closing_time': time(21, 0),
        },
        
        # MATAHARI Stores
        {
            'tenant': tenants['matahari'],
            'code': 'MATAHARI-BIP',
            'name': 'Matahari BIP',
            'address': 'Bandung Indah Plaza, Jl. Merdeka No. 56',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(10, 0),
            'closing_time': time(22, 0),
        },
        {
            'tenant': tenants['matahari'],
            'code': 'MATAHARI-TSM',
            'name': 'Matahari Trans Studio Mall',
            'address': 'Trans Studio Mall Bandung',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(10, 0),
            'closing_time': time(22, 0),
        },
        {
            'tenant': tenants['matahari'],
            'code': 'MATAHARI-PVJ',
            'name': 'Matahari Paris Van Java',
            'address': 'Paris Van Java Mall',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(10, 0),
            'closing_time': time(22, 0),
        },
        
        # CARREFOUR Stores
        {
            'tenant': tenants['carrefour'],
            'code': 'CARREFOUR-CIHAMPELAS',
            'name': 'Carrefour Cihampelas',
            'address': 'Cihampelas Walk, Jl. Cihampelas',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(8, 0),
            'closing_time': time(22, 0),
        },
        {
            'tenant': tenants['carrefour'],
            'code': 'CARREFOUR-FESTIVAL',
            'name': 'Carrefour Festival Citylink',
            'address': 'Festival Citylink',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(9, 0),
            'closing_time': time(22, 0),
        },
        {
            'tenant': tenants['carrefour'],
            'code': 'CARREFOUR-PASTEUR',
            'name': 'Carrefour Pasteur',
            'address': 'Jl. Dr. Djunjunan (Pasteur)',
            'city': 'Bandung',
            'province': 'Jawa Barat',
            'opening_time': time(8, 0),
            'closing_time': time(21, 0),
        },
    ]
    
    stores = []
    for store_data in stores_data:
        store = Store.objects.create(**store_data)
        stores.append(store)
        print(f"  ✅ {store.name} ({store.code})")
    
    return stores


def create_global_brands(tenants):
    """
    Create outlets for each tenant - each tenant has 3 unique brands
    """
    print("\n🍗 Creating Outlets (3 per tenant)...")
    
    outlets_data = {
        'yogya': [
            ('Chicken Sumo', 'chicken-sumo', '021-1111111', 'cs@yogya.com', 'ws://localhost:8001/ws/kitchen/chicken-sumo/'),
            ('Magic Oven', 'magic-oven', '021-2222222', 'mo@yogya.com', 'ws://localhost:8001/ws/kitchen/magic-oven/'),
            ('Magic Pizza', 'magic-pizza', '021-3333333', 'mp@yogya.com', 'ws://localhost:8001/ws/kitchen/magic-pizza/'),
        ],
        'borma': [
            ('Borma Cafe', 'borma-cafe', '022-1111111', 'cafe@borma.com', 'ws://localhost:8001/ws/kitchen/borma-cafe/'),
            ('Borma Bakery', 'borma-bakery', '022-2222222', 'bakery@borma.com', 'ws://localhost:8001/ws/kitchen/borma-bakery/'),
            ('Borma Fresh', 'borma-fresh', '022-3333333', 'fresh@borma.com', 'ws://localhost:8001/ws/kitchen/borma-fresh/'),
        ],
        'matahari': [
            ('Matahari Food Court', 'matahari-fc', '021-4444444', 'fc@matahari.com', 'ws://localhost:8001/ws/kitchen/matahari-fc/'),
            ('Matahari Coffee', 'matahari-coffee', '021-5555555', 'coffee@matahari.com', 'ws://localhost:8001/ws/kitchen/matahari-coffee/'),
            ('Matahari Snack Bar', 'matahari-snack', '021-6666666', 'snack@matahari.com', 'ws://localhost:8001/ws/kitchen/matahari-snack/'),
        ],
        'carrefour': [
            ('Carrefour Bistro', 'carrefour-bistro', '021-7777777', 'bistro@carrefour.com', 'ws://localhost:8001/ws/kitchen/carrefour-bistro/'),
            ('Carrefour Bakery', 'carrefour-bakery', '021-8888888', 'bakery@carrefour.com', 'ws://localhost:8001/ws/kitchen/carrefour-bakery/'),
            ('Carrefour Express', 'carrefour-express', '021-9999999', 'express@carrefour.com', 'ws://localhost:8001/ws/kitchen/carrefour-express/'),
        ],
    }
    
    brands = {}
    for tenant_key, outlet_list in outlets_data.items():
        tenant = tenants[tenant_key]
        print(f"\n  {tenant.name}:")
        for name, slug, phone, email, ws_url in outlet_list:
            outlet = Outlet.objects.create(
                tenant=tenant,
                name=name,
                brand_name=name,
                slug=slug,
                phone=phone,
                email=email,
                websocket_url=ws_url,
                is_active=True
            )
            brands[slug] = outlet
            print(f"    ✅ {outlet.brand_name}")
    
    return brands


def assign_brands_to_stores(stores, brands):
    """
    Create StoreOutlet entries to assign brands to stores (CROSS-TENANT)
    This demonstrates OPSI 2 architecture where stores can have outlets from different tenants
    """
    print("\n🔗 Assigning Brands to Stores (Cross-Tenant Many-to-Many)...")
    
    # Get specific outlets from each tenant
    chicken_sumo = brands['chicken-sumo']
    magic_oven = brands['magic-oven']
    magic_pizza = brands['magic-pizza']
    
    # YOGYA stores get their own brands (Chicken Sumo, Magic Oven, Magic Pizza)
    yogya_stores = [s for s in stores if s.tenant.slug == 'yogya']
    for store in yogya_stores:
        StoreOutlet.objects.create(store=store, outlet=chicken_sumo, is_active=True, display_order=1)
        StoreOutlet.objects.create(store=store, outlet=magic_oven, is_active=True, display_order=2)
        StoreOutlet.objects.create(store=store, outlet=magic_pizza, is_active=True, display_order=3)
        print(f"  ✅ {store.name}: Chicken Sumo, Magic Oven, Magic Pizza")
    
    # BORMA stores (cross-tenant) - can have YOGYA brands
    borma_stores = [s for s in stores if s.tenant.slug == 'borma']
    borma_cafe = brands['borma-cafe']
    borma_bakery = brands['borma-bakery']
    for store in borma_stores:
        # Own brands
        StoreOutlet.objects.create(store=store, outlet=borma_cafe, is_active=True, display_order=1)
        StoreOutlet.objects.create(store=store, outlet=borma_bakery, is_active=True, display_order=2)
        # Cross-tenant: YOGYA's Chicken Sumo
        StoreOutlet.objects.create(store=store, outlet=chicken_sumo, is_active=True, display_order=3)
        print(f"  ✅ {store.name}: Borma Cafe, Borma Bakery, Chicken Sumo (YOGYA)")
    
    # MATAHARI stores (cross-tenant) - can have YOGYA brands
    matahari_stores = [s for s in stores if s.tenant.slug == 'matahari']
    matahari_fc = brands['matahari-fc']
    matahari_coffee = brands['matahari-coffee']
    for store in matahari_stores:
        # Own brands
        StoreOutlet.objects.create(store=store, outlet=matahari_fc, is_active=True, display_order=1)
        StoreOutlet.objects.create(store=store, outlet=matahari_coffee, is_active=True, display_order=2)
        # Cross-tenant: YOGYA's Magic Pizza
        StoreOutlet.objects.create(store=store, outlet=magic_pizza, is_active=True, display_order=3)
        print(f"  ✅ {store.name}: Matahari FC, Matahari Coffee, Magic Pizza (YOGYA)")
    
    # CARREFOUR stores (cross-tenant) - can have multiple brands from YOGYA
    carrefour_stores = [s for s in stores if s.tenant.slug == 'carrefour']
    carrefour_bistro = brands['carrefour-bistro']
    for store in carrefour_stores:
        # Own brand
        StoreOutlet.objects.create(store=store, outlet=carrefour_bistro, is_active=True, display_order=1)
        # Cross-tenant: All YOGYA brands
        StoreOutlet.objects.create(store=store, outlet=chicken_sumo, is_active=True, display_order=2)
        StoreOutlet.objects.create(store=store, outlet=magic_oven, is_active=True, display_order=3)
        StoreOutlet.objects.create(store=store, outlet=magic_pizza, is_active=True, display_order=4)
        print(f"  ✅ {store.name}: Carrefour Bistro, Chicken Sumo (YOGYA), Magic Oven (YOGYA), Magic Pizza (YOGYA)")


def create_kitchen_stations(brands):
    """Create kitchen stations per outlet"""
    print("\n🍳 Creating Kitchen Stations (Per Outlet)...")
    
    # YOGYA Outlets
    chicken_sumo = brands['chicken-sumo']
    KitchenStation.objects.create(outlet=chicken_sumo, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    KitchenStation.objects.create(outlet=chicken_sumo, name='Grill Station', code='GRILL', is_active=True, sort_order=2)
    print(f"  ✅ Chicken Sumo: MAIN, GRILL")
    
    magic_oven = brands['magic-oven']
    KitchenStation.objects.create(outlet=magic_oven, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    KitchenStation.objects.create(outlet=magic_oven, name='Oven Station', code='OVEN', is_active=True, sort_order=2)
    print(f"  ✅ Magic Oven: MAIN, OVEN")
    
    magic_pizza = brands['magic-pizza']
    KitchenStation.objects.create(outlet=magic_pizza, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    KitchenStation.objects.create(outlet=magic_pizza, name='Pizza Oven', code='PIZZA', is_active=True, sort_order=2)
    print(f"  ✅ Magic Pizza: MAIN, PIZZA")
    
    # BORMA Outlets
    borma_cafe = brands['borma-cafe']
    KitchenStation.objects.create(outlet=borma_cafe, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    KitchenStation.objects.create(outlet=borma_cafe, name='Beverage Station', code='BEVERAGE', is_active=True, sort_order=2)
    print(f"  ✅ Borma Cafe: MAIN, BEVERAGE")
    
    borma_bakery = brands['borma-bakery']
    KitchenStation.objects.create(outlet=borma_bakery, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    KitchenStation.objects.create(outlet=borma_bakery, name='Bakery Oven', code='BAKERY', is_active=True, sort_order=2)
    print(f"  ✅ Borma Bakery: MAIN, BAKERY")
    
    borma_fresh = brands['borma-fresh']
    KitchenStation.objects.create(outlet=borma_fresh, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    print(f"  ✅ Borma Fresh: MAIN")
    
    # MATAHARI Outlets
    matahari_fc = brands['matahari-fc']
    KitchenStation.objects.create(outlet=matahari_fc, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    KitchenStation.objects.create(outlet=matahari_fc, name='Grill Station', code='GRILL', is_active=True, sort_order=2)
    print(f"  ✅ Matahari Food Court: MAIN, GRILL")
    
    matahari_coffee = brands['matahari-coffee']
    KitchenStation.objects.create(outlet=matahari_coffee, name='Main Bar', code='MAIN', is_active=True, sort_order=1)
    KitchenStation.objects.create(outlet=matahari_coffee, name='Espresso Bar', code='ESPRESSO', is_active=True, sort_order=2)
    print(f"  ✅ Matahari Coffee: MAIN, ESPRESSO")
    
    matahari_snack = brands['matahari-snack']
    KitchenStation.objects.create(outlet=matahari_snack, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    print(f"  ✅ Matahari Snack Bar: MAIN")
    
    # CARREFOUR Outlets
    carrefour_bistro = brands['carrefour-bistro']
    KitchenStation.objects.create(outlet=carrefour_bistro, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    KitchenStation.objects.create(outlet=carrefour_bistro, name='Grill Station', code='GRILL', is_active=True, sort_order=2)
    print(f"  ✅ Carrefour Bistro: MAIN, GRILL")
    
    carrefour_bakery = brands['carrefour-bakery']
    KitchenStation.objects.create(outlet=carrefour_bakery, name='Main Kitchen', code='MAIN', is_active=True, sort_order=1)
    KitchenStation.objects.create(outlet=carrefour_bakery, name='Bakery Oven', code='BAKERY', is_active=True, sort_order=2)
    print(f"  ✅ Carrefour Bakery: MAIN, BAKERY")
    
    carrefour_express = brands['carrefour-express']
    KitchenStation.objects.create(outlet=carrefour_express, name='Main Counter', code='MAIN', is_active=True, sort_order=1)
    print(f"  ✅ Carrefour Express: MAIN")


def create_categories_and_products(brands, tenants):
    """Create categories and products per outlet - only for YOGYA brands (sample)"""
    print("\n📋 Creating Categories and Products (Sample: YOGYA Outlets)...")
    
    yogya = tenants['yogya']
    
    # Set current tenant for YOGYA products
    set_current_tenant(yogya)
    
    try:
        # CHICKEN SUMO Menu
        chicken_sumo = brands['chicken-sumo']
        print(f"\n  🍗 {chicken_sumo.brand_name}")
        
        # Categories - use all_objects manager to bypass tenant filtering
        cat_fried = Category.all_objects.create(
            outlet=chicken_sumo,
            tenant=yogya,
            name='Fried Chicken',
            kitchen_station_code='GRILL',
            sort_order=1
        )
        print(f"    ✅ Created category: {cat_fried.name}")
    except Exception as e:
        print(f"    ❌ ERROR creating category: {e}")
        import traceback
        traceback.print_exc()
    cat_combo = Category.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        name='Combos',
        kitchen_station_code='MAIN',
        sort_order=2
    )
    cat_drink = Category.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        name='Drinks',
        kitchen_station_code='MAIN',
        sort_order=3
    )
    
    # Products - Fried Chicken
    Product.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        category=cat_fried,
        sku='CS-FC-001',
        name='Chicken Sumo Original',
        description='Ayam goreng crispy original',
        price=Decimal('25000'),
        preparation_time=10,
        is_popular=True
    )
    Product.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        category=cat_fried,
        sku='CS-FC-002',
        name='Chicken Sumo Spicy',
        description='Ayam goreng pedas level 5',
        price=Decimal('27000'),
        preparation_time=10,
        is_popular=True
    )
    Product.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        category=cat_fried,
        sku='CS-FC-003',
        name='Chicken Wings 5pcs',
        description='Sayap ayam goreng crispy',
        price=Decimal('20000'),
        preparation_time=8
    )
    
    # Products - Combos
    Product.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        category=cat_combo,
        sku='CS-CB-001',
        name='Chicken Combo + Fries + Drink',
        description='Paket ayam + kentang + minuman',
        price=Decimal('35000'),
        preparation_time=12,
        is_featured=True
    )
    Product.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        category=cat_combo,
        sku='CS-CB-002',
        name='Family Meal 8pcs',
        description='Paket keluarga 8 potong ayam',
        price=Decimal('85000'),
        preparation_time=15,
        is_featured=True
    )
    Product.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        category=cat_combo,
        sku='CS-CB-003',
        name='Double Chicken Burger',
        description='Burger ayam goreng double',
        price=Decimal('32000'),
        preparation_time=10
    )
    
    # Products - Drinks
    Product.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        category=cat_drink,
        sku='CS-DR-001',
        name='Iced Tea',
        price=Decimal('5000'),
        preparation_time=2
    )
    Product.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        category=cat_drink,
        sku='CS-DR-002',
        name='Orange Juice',
        price=Decimal('8000'),
        preparation_time=3
    )
    Product.all_objects.create(
        outlet=chicken_sumo,
        tenant=yogya,
        category=cat_drink,
        sku='CS-DR-003',
        name='Mineral Water',
        price=Decimal('3000'),
        preparation_time=1
    )
    
    print(f"    ✅ 3 categories, 9 products")
    
    # MAGIC OVEN Menu
    magic_oven = brands['magic-oven']
    print(f"\n  🍞 {magic_oven.brand_name}")
    
    # Categories
    cat_bread = Category.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        name='Breads',
        kitchen_station_code='OVEN',
        sort_order=1
    )
    cat_pastry = Category.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        name='Pastries',
        kitchen_station_code='OVEN',
        sort_order=2
    )
    cat_cake = Category.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        name='Cakes',
        kitchen_station_code='OVEN',
        sort_order=3
    )
    
    # Products - Breads
    Product.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        category=cat_bread,
        sku='MO-BR-001',
        name='Croissant',
        price=Decimal('15000'),
        preparation_time=5,
        is_popular=True
    )
    Product.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        category=cat_bread,
        sku='MO-BR-002',
        name='Baguette',
        price=Decimal('18000'),
        preparation_time=5
    )
    Product.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        category=cat_bread,
        sku='MO-BR-003',
        name='Sourdough Bread',
        price=Decimal('25000'),
        preparation_time=5
    )
    
    # Products - Pastries
    Product.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        category=cat_pastry,
        sku='MO-PS-001',
        name='Danish Pastry',
        price=Decimal('12000'),
        preparation_time=5
    )
    Product.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        category=cat_pastry,
        sku='MO-PS-002',
        name='Cheese Tart',
        price=Decimal('14000'),
        preparation_time=5,
        is_popular=True
    )
    Product.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        category=cat_pastry,
        sku='MO-PS-003',
        name='Apple Turnover',
        price=Decimal('13000'),
        preparation_time=5
    )
    
    # Products - Cakes
    Product.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        category=cat_cake,
        sku='MO-CK-001',
        name='Chocolate Cake Slice',
        price=Decimal('22000'),
        preparation_time=3,
        is_featured=True
    )
    Product.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        category=cat_cake,
        sku='MO-CK-002',
        name='Red Velvet Slice',
        price=Decimal('24000'),
        preparation_time=3,
        is_featured=True
    )
    Product.all_objects.create(
        outlet=magic_oven,
        tenant=yogya,
        category=cat_cake,
        sku='MO-CK-003',
        name='Tiramisu',
        price=Decimal('28000'),
        preparation_time=3
    )
    
    print(f"    ✅ 3 categories, 9 products")
    
    # MAGIC PIZZA Menu
    magic_pizza = brands['magic-pizza']
    print(f"\n  🍕 {magic_pizza.brand_name}")
    
    # Categories
    cat_pizza = Category.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        name='Pizza',
        kitchen_station_code='PIZZA',
        sort_order=1
    )
    cat_pasta = Category.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        name='Pasta',
        kitchen_station_code='MAIN',
        sort_order=2
    )
    cat_dessert = Category.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        name='Desserts',
        kitchen_station_code='MAIN',
        sort_order=3
    )
    
    # Products - Pizza
    Product.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        category=cat_pizza,
        sku='MP-PZ-001',
        name='Margherita Pizza',
        price=Decimal('65000'),
        preparation_time=15,
        is_popular=True
    )
    Product.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        category=cat_pizza,
        sku='MP-PZ-002',
        name='Pepperoni Pizza',
        price=Decimal('75000'),
        preparation_time=15,
        is_popular=True
    )
    Product.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        category=cat_pizza,
        sku='MP-PZ-003',
        name='Hawaiian Pizza',
        price=Decimal('70000'),
        preparation_time=15
    )
    
    # Products - Pasta
    Product.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        category=cat_pasta,
        sku='MP-PA-001',
        name='Spaghetti Carbonara',
        price=Decimal('45000'),
        preparation_time=12,
        is_featured=True
    )
    Product.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        category=cat_pasta,
        sku='MP-PA-002',
        name='Penne Arrabiata',
        price=Decimal('42000'),
        preparation_time=12
    )
    Product.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        category=cat_pasta,
        sku='MP-PA-003',
        name='Fettuccine Alfredo',
        price=Decimal('48000'),
        preparation_time=12
    )
    
    # Products - Desserts
    Product.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        category=cat_dessert,
        sku='MP-DS-001',
        name='Gelato Vanilla',
        price=Decimal('18000'),
        preparation_time=3
    )
    Product.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        category=cat_dessert,
        sku='MP-DS-002',
        name='Gelato Chocolate',
        price=Decimal('18000'),
        preparation_time=3
    )
    Product.all_objects.create(
        outlet=magic_pizza,
        tenant=yogya,
        category=cat_dessert,
        sku='MP-DS-003',
        name='Panna Cotta',
        price=Decimal('22000'),
        preparation_time=3
    )
    
    print(f"    ✅ 3 categories, 9 products")


def create_spicy_levels(tenants):
    """Create spicy level modifiers (globally available for all products)"""
    print("\n🌶️ Creating Spicy Levels...")
    spicy_levels = [
        {'name': 'Level 1 (Mild)', 'sort': 1},
        {'name': 'Level 2 (Medium)', 'sort': 2},
        {'name': 'Level 3 (Hot)', 'sort': 3},
        {'name': 'Level 4 (Extra Hot)', 'sort': 4},
        {'name': 'Level 5 (Insane)', 'sort': 5},
    ]
    
    for level in spicy_levels:
        ProductModifier.objects.create(
            name=level['name'],
            type='spicy',
            price_adjustment=Decimal('0'),  # No additional cost for spice level
            product=None,  # Global (available for all products)
            is_active=True,
            sort_order=level['sort']
        )
    print(f"  ✅ Created {len(spicy_levels)} spicy levels (global)")


def create_toppings(tenants):
    """Create topping modifiers (globally available for all products)"""
    print("\n🧀 Creating Toppings...")
    toppings = [
        {'name': 'Extra Cheese', 'sort': 1, 'price': 5000},
        {'name': 'Mushrooms', 'sort': 2, 'price': 3000},
        {'name': 'Olives', 'sort': 3, 'price': 3000},
        {'name': 'Onions', 'sort': 4, 'price': 2000},
        {'name': 'Tomatoes', 'sort': 5, 'price': 2000},
        {'name': 'Peppers', 'sort': 6, 'price': 2000},
        {'name': 'Bacon', 'sort': 7, 'price': 8000},
        {'name': 'Sausage', 'sort': 8, 'price': 7000},
    ]
    
    for topping in toppings:
        ProductModifier.objects.create(
            name=topping['name'],
            type='topping',
            price_adjustment=Decimal(str(topping['price'])),
            product=None,  # Global
            is_active=True,
            sort_order=topping['sort']
        )
    print(f"  ✅ Created {len(toppings)} toppings (global)")


def create_additions(tenants):
    """Create addition modifiers (sides, extras, upgrades)"""
    print("\n🍟 Creating Additions...")
    additions = [
        {'name': 'Extra Sauce', 'sort': 1, 'price': 3000},
        {'name': 'Garlic Bread', 'sort': 2, 'price': 15000},
        {'name': 'Coleslaw', 'sort': 3, 'price': 10000},
        {'name': 'Pickles', 'sort': 4, 'price': 2000},
        {'name': 'Upgrade to Large', 'sort': 5, 'price': 10000},
        {'name': 'Add Egg', 'sort': 6, 'price': 5000},
        {'name': 'Add Avocado', 'sort': 7, 'price': 12000},
        {'name': 'Extra Meat', 'sort': 8, 'price': 15000},
    ]
    
    for addition in additions:
        ProductModifier.objects.create(
            name=addition['name'],
            type='extra',  # Changed from 'addition' to match frontend
            price_adjustment=Decimal(str(addition['price'])),
            product=None,  # Global
            is_active=True,
            sort_order=addition['sort']
        )
    print(f"  ✅ Created {len(additions)} additions (global)")


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🚀 OPSI 2 Many-to-Many Test Data Setup")
    print("="*60)
    
    try:
        # Clear existing data
        clear_all_data()
        
        # Create tenants
        tenants = create_tenants()
        
        # Create users (superadmin and tenant owners)
        create_users(tenants)
        
        # Create stores
        stores = create_stores(tenants)
        
        # Create global brands
        brands = create_global_brands(tenants)
        
        # Assign brands to stores (M2M)
        assign_brands_to_stores(stores, brands)
        
        # Create kitchen stations per brand
        create_kitchen_stations(brands)
        
        # Create categories and products per brand
        create_categories_and_products(brands, tenants)
        
        # Create modifiers (global)
        create_spicy_levels(tenants)
        create_toppings(tenants)
        create_additions(tenants)
        
        print("\n" + "="*60)
        print("✅ Test data setup completed successfully!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  - Tenants: {Tenant.objects.count()}")
        print(f"  - Users: {User.objects.count()}")
        print(f"  - Stores: {Store.objects.count()}")
        print(f"  - Global Brands (Outlets): {Outlet.objects.count()}")
        print(f"  - Store-Brand Assignments: {StoreOutlet.objects.count()}")
        print(f"  - Kitchen Stations: {KitchenStation.objects.count()}")
        print(f"  - Categories: {Category.all_objects.count()}")
        print(f"  - Products: {Product.all_objects.count()}")
        print(f"  • Spicy Levels: {ProductModifier.objects.filter(type='spicy').count()}")
        print(f"  • Toppings: {ProductModifier.objects.filter(type='topping').count()}")
        print(f"  • Additions: {ProductModifier.objects.filter(type='extra').count()}")
        
        print(f"\n👤 Test Users:")
        print(f"  - Superadmin: superadmin / admin123")
        print(f"  - Tenant Owners: yogya_owner, borma_owner, matahari_owner, carrefour_owner / owner123")
        
        print(f"\n🏪 Test Store Codes:")
        for store in Store.objects.all()[:3]:
            print(f"  - {store.code} ({store.name})")
        
        print(f"\n🍗 Test Brands:")
        for outlet in Outlet.objects.all():
            stores_count = outlet.stores.count()
            print(f"  - {outlet.brand_name} (available at {stores_count} stores)")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def create_users(tenants):
    """Create superadmin and test users"""
    print("\n👤 Creating Users...")
    
    # Delete existing users
    User.objects.all().delete()
    print("  ✅ Cleared existing users")
    
    # Create superadmin
    superadmin = User.objects.create_superuser(
        username='superadmin',
        email='superadmin@kiosk.local',
        password='admin123',
        first_name='Super',
        last_name='Admin',
        role='super_admin'
    )
    print(f"  ✅ Superadmin: superadmin / admin123")
    
    # Create tenant owners (one per tenant)
    for slug, tenant in tenants.items():
        owner = User.objects.create_user(
            username=f'{slug}_owner',
            email=f'owner@{slug}.local',
            password='owner123',
            first_name=tenant.name,
            last_name='Owner',
            role='tenant_owner',
            tenant=tenant
        )
        print(f"  ✅ {tenant.name} Owner: {slug}_owner / owner123")
    
    print(f"\n  Total users created: {User.objects.count()}")


if __name__ == '__main__':
    main()

