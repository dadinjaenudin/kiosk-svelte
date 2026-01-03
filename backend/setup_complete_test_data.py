"""
Complete Test Data Setup Script
Creates comprehensive sample data for multi-outlet food court system:
- Tenants (3)
- Outlets (6) 
- Categories (12)
- Products (30)
- Toppings (20)
- Additions (15)
- Users (20)
- Customers (30)
- Orders (50)
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.tenants.models import Tenant, Outlet
from apps.products.models import Category, Product, ProductModifier
from apps.customers.models import Customer
from apps.orders.models import Order, OrderItem
from apps.promotions.models import Promotion

User = get_user_model()

def create_toppings():
    """Create sample toppings for products"""
    print("\n📝 Creating Toppings...")
    
    # Get tenants
    pizza = Tenant.objects.get(slug='pizza-paradise')
    burger = Tenant.objects.get(slug='burger-station')
    noodle = Tenant.objects.get(slug='noodle-house')
    
    toppings_data = [
        # Pizza toppings
        {'name': 'Extra Cheese', 'tenant': pizza, 'price': 15000},
        {'name': 'Pepperoni', 'tenant': pizza, 'price': 20000},
        {'name': 'Mushrooms', 'tenant': pizza, 'price': 12000},
        {'name': 'Black Olives', 'tenant': pizza, 'price': 10000},
        {'name': 'Green Peppers', 'tenant': pizza, 'price': 8000},
        {'name': 'Onions', 'tenant': pizza, 'price': 8000},
        {'name': 'Italian Sausage', 'tenant': pizza, 'price': 18000},
        
        # Burger toppings
        {'name': 'Bacon', 'tenant': burger, 'price': 15000},
        {'name': 'Cheddar Cheese', 'tenant': burger, 'price': 10000},
        {'name': 'Swiss Cheese', 'tenant': burger, 'price': 12000},
        {'name': 'Fried Egg', 'tenant': burger, 'price': 8000},
        {'name': 'Grilled Onions', 'tenant': burger, 'price': 5000},
        {'name': 'Jalapeños', 'tenant': burger, 'price': 5000},
        
        # Noodle toppings
        {'name': 'Extra Meat', 'tenant': noodle, 'price': 15000},
        {'name': 'Extra Vegetables', 'tenant': noodle, 'price': 10000},
        {'name': 'Boiled Egg', 'tenant': noodle, 'price': 8000},
        {'name': 'Fried Wonton', 'tenant': noodle, 'price': 12000},
        {'name': 'Extra Noodles', 'tenant': noodle, 'price': 10000},
        {'name': 'Chili Oil', 'tenant': noodle, 'price': 5000},
        {'name': 'Spring Onions', 'tenant': noodle, 'price': 3000},
    ]
    
    created = 0
    for data in toppings_data:
        # Get random product from tenant for association
        product = Product.all_objects.filter(tenant=data['tenant']).first()
        
        modifier, created_new = ProductModifier.objects.get_or_create(
            name=data['name'],
            product=product,
            type='topping',
            defaults={
                'price_adjustment': Decimal(str(data['price'])),
                'is_active': True
            }
        )
        if created_new:
            created += 1
            print(f"  ✅ Created topping: {modifier.name} - Rp {modifier.price_adjustment:,.0f}")
    
    print(f"✅ Created {created} new toppings, total: {ProductModifier.objects.filter(type='topping').count()}")

def create_additions():
    """Create sample additions (sides/drinks)"""
    print("\n🥤 Creating Additions...")
    
    # Get tenants
    pizza = Tenant.objects.get(slug='pizza-paradise')
    burger = Tenant.objects.get(slug='burger-station')
    noodle = Tenant.objects.get(slug='noodle-house')
    
    additions_data = [
        # Pizza additions
        {'name': 'Garlic Bread', 'tenant': pizza, 'price': 25000},
        {'name': 'Chicken Wings (6pcs)', 'tenant': pizza, 'price': 35000},
        {'name': 'Caesar Salad', 'tenant': pizza, 'price': 30000},
        {'name': 'Coca Cola', 'tenant': pizza, 'price': 10000},
        {'name': 'Iced Tea', 'tenant': pizza, 'price': 8000},
        
        # Burger additions
        {'name': 'French Fries', 'tenant': burger, 'price': 20000},
        {'name': 'Onion Rings', 'tenant': burger, 'price': 22000},
        {'name': 'Coleslaw', 'tenant': burger, 'price': 15000},
        {'name': 'Milkshake', 'tenant': burger, 'price': 25000},
        {'name': 'Soft Drink', 'tenant': burger, 'price': 10000},
        
        # Noodle additions
        {'name': 'Spring Rolls (4pcs)', 'tenant': noodle, 'price': 20000},
        {'name': 'Gyoza (6pcs)', 'tenant': noodle, 'price': 25000},
        {'name': 'Fried Rice', 'tenant': noodle, 'price': 30000},
        {'name': 'Green Tea', 'tenant': noodle, 'price': 8000},
        {'name': 'Jasmine Tea', 'tenant': noodle, 'price': 8000},
    ]
    
    created = 0
    for data in additions_data:
        # Get random product from tenant for association
        product = Product.all_objects.filter(tenant=data['tenant']).first()
        
        modifier, created_new = ProductModifier.objects.get_or_create(
            name=data['name'],
            product=product,
            type='extra',
            defaults={
                'price_adjustment': Decimal(str(data['price'])),
                'is_active': True
            }
        )
        if created_new:
            created += 1
            print(f"  ✅ Created addition: {modifier.name} - Rp {modifier.price_adjustment:,.0f}")
    
    print(f"✅ Created {created} new additions, total: {ProductModifier.objects.filter(type='extra').count()}")

def create_customers():
    """Create sample customers"""
    print("\n👥 Creating Customers...")
    
    # Get all tenants for random assignment
    tenants = list(Tenant.objects.all())
    
    if not tenants:
        print("❌ No tenants found. Cannot create customers.")
        return
    
    customers_data = [
        {'name': 'John Doe', 'phone': '081234567890', 'email': 'john@example.com'},
        {'name': 'Jane Smith', 'phone': '081234567891', 'email': 'jane@example.com'},
        {'name': 'Bob Johnson', 'phone': '081234567892', 'email': 'bob@example.com'},
        {'name': 'Alice Williams', 'phone': '081234567893', 'email': 'alice@example.com'},
        {'name': 'Charlie Brown', 'phone': '081234567894', 'email': 'charlie@example.com'},
        {'name': 'David Lee', 'phone': '081234567895', 'email': 'david@example.com'},
        {'name': 'Emma Davis', 'phone': '081234567896', 'email': 'emma@example.com'},
        {'name': 'Frank Miller', 'phone': '081234567897', 'email': 'frank@example.com'},
        {'name': 'Grace Wilson', 'phone': '081234567898', 'email': 'grace@example.com'},
        {'name': 'Henry Moore', 'phone': '081234567899', 'email': 'henry@example.com'},
        {'name': 'Ivy Taylor', 'phone': '081234567800', 'email': 'ivy@example.com'},
        {'name': 'Jack Anderson', 'phone': '081234567801', 'email': 'jack@example.com'},
        {'name': 'Kate Thomas', 'phone': '081234567802', 'email': 'kate@example.com'},
        {'name': 'Leo Jackson', 'phone': '081234567803', 'email': 'leo@example.com'},
        {'name': 'Mia White', 'phone': '081234567804', 'email': 'mia@example.com'},
        {'name': 'Noah Harris', 'phone': '081234567805', 'email': 'noah@example.com'},
        {'name': 'Olivia Martin', 'phone': '081234567806', 'email': 'olivia@example.com'},
        {'name': 'Peter Garcia', 'phone': '081234567807', 'email': 'peter@example.com'},
        {'name': 'Quinn Martinez', 'phone': '081234567808', 'email': 'quinn@example.com'},
        {'name': 'Rachel Robinson', 'phone': '081234567809', 'email': 'rachel@example.com'},
        {'name': 'Sam Clark', 'phone': '081234567810', 'email': 'sam@example.com'},
        {'name': 'Tina Rodriguez', 'phone': '081234567811', 'email': 'tina@example.com'},
        {'name': 'Uma Lewis', 'phone': '081234567812', 'email': 'uma@example.com'},
        {'name': 'Victor Walker', 'phone': '081234567813', 'email': 'victor@example.com'},
        {'name': 'Wendy Hall', 'phone': '081234567814', 'email': 'wendy@example.com'},
        {'name': 'Xavier Allen', 'phone': '081234567815', 'email': 'xavier@example.com'},
        {'name': 'Yara Young', 'phone': '081234567816', 'email': 'yara@example.com'},
        {'name': 'Zack King', 'phone': '081234567817', 'email': 'zack@example.com'},
        {'name': 'Amy Wright', 'phone': '081234567818', 'email': 'amy@example.com'},
        {'name': 'Brian Scott', 'phone': '081234567819', 'email': 'brian@example.com'},
    ]
    
    created = 0
    for data in customers_data:
        # Randomly assign a tenant to each customer
        tenant = random.choice(tenants)
        
        customer, created_new = Customer.objects.get_or_create(
            phone=data['phone'],
            defaults={
                'name': data['name'],
                'email': data['email'],
                'tenant': tenant
            }
        )
        if created_new:
            created += 1
            print(f"  ✅ Created customer: {customer.name} ({customer.phone}) - {tenant.name}")
    
    print(f"✅ Created {created} new customers, total: {Customer.objects.count()}")

def create_orders():
    """Create sample orders"""
    print("\n📦 Creating Orders...")
    
    outlets = list(Outlet.objects.all())
    customers = list(Customer.objects.all())
    products = list(Product.all_objects.filter(is_active=True, is_available=True))
    
    if not customers:
        print("❌ No customers found. Run create_customers() first.")
        return
    
    if not products:
        print("❌ No products found. Cannot create orders.")
        return
    
    statuses = ['pending', 'confirmed', 'preparing', 'ready', 'served', 'completed']
    payment_statuses = ['paid', 'unpaid', 'pending']
    payment_methods = ['cash', 'qris', 'debit_card', 'credit_card']
    
    created = 0
    
    # Create orders for the last 7 days
    for day in range(7):
        date = datetime.now() - timedelta(days=day)
        orders_per_day = random.randint(5, 10)
        
        for _ in range(orders_per_day):
            outlet = random.choice(outlets)
            customer = random.choice(customers)
            
            # Random time during the day
            hour = random.randint(10, 21)
            minute = random.randint(0, 59)
            order_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Create order
            order = Order.objects.create(
                tenant=outlet.tenant,
                outlet=outlet,
                customer_name=customer.name,
                customer_phone=customer.phone,
                customer_email=customer.email,
                order_number=f"ORD{order_time.strftime('%Y%m%d')}{random.randint(1000, 9999)}",
                status=random.choice(statuses),
                payment_status=random.choice(payment_statuses),
                created_at=order_time,
                updated_at=order_time
            )
            
            # Add 1-4 items to order
            num_items = random.randint(1, 4)
            tenant_products = [p for p in products if p.tenant_id == outlet.tenant_id]
            
            if not tenant_products:
                order.delete()
                continue
            
            order_total = Decimal('0')
            
            for _ in range(num_items):
                product = random.choice(tenant_products)
                quantity = random.randint(1, 3)
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    quantity=quantity,
                    unit_price=product.price,
                    total_price=product.price * quantity
                )
                
                order_total += product.price * quantity
            
            # Update order totals
            order.subtotal = order_total
            order.total_amount = order_total
            order.save()
            
            created += 1
            print(f"  ✅ Created order: {order.order_number} - {order.outlet.name} - Rp {order.total_amount:,.0f}")
    
    print(f"✅ Created {created} new orders, total: {Order.objects.count()}")

def create_promotions():
    """Create sample promotions with different types for each tenant"""
    print("\n🎉 Creating Promotions...")
    
    # Get tenants
    pizza = Tenant.objects.get(slug='pizza-paradise')
    burger = Tenant.objects.get(slug='burger-station')
    noodle = Tenant.objects.get(slug='noodle-house')
    
    now = timezone.now()
    next_month = now + timedelta(days=30)
    next_week = now + timedelta(days=7)
    
    promotions_data = [
        # Pizza Paradise promotions
        {
            'tenant': pizza,
            'name': 'Weekend Special',
            'description': '20% off on all pizzas during weekends',
            'code': 'WEEKEND20',
            'promo_type': 'percentage',
            'discount_value': Decimal('20.00'),
            'start_date': now,
            'end_date': next_month,
            'is_active': True,
            'min_purchase_amount': Decimal('50000'),
        },
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
            'code': 'BUY2GET1PIZZA',
            'promo_type': 'buy_x_get_y',
            'discount_value': Decimal('0.00'),
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
        
        # Burger Station promotions
        {
            'tenant': burger,
            'name': 'Combo Deal',
            'description': 'Special combo discount',
            'code': 'COMBO15K',
            'promo_type': 'fixed',
            'discount_value': Decimal('15000.00'),
            'start_date': now,
            'end_date': next_month,
            'is_active': True,
            'min_purchase_amount': Decimal('60000'),
        },
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
            'discount_value': Decimal('0.00'),
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
        
        # Noodle House promotions
        {
            'tenant': noodle,
            'name': 'Lunch Special',
            'description': 'Lunch hour special discount',
            'code': 'LUNCH10K',
            'promo_type': 'fixed',
            'discount_value': Decimal('10000.00'),
            'start_date': now,
            'end_date': next_month,
            'is_active': True,
            'min_purchase_amount': Decimal('40000'),
        },
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
            'discount_value': Decimal('0.00'),
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
            'code': 'HOLIDAY2026',
            'promo_type': 'fixed',
            'discount_value': Decimal('20000.00'),
            'start_date': now,
            'end_date': next_month,
            'is_active': False,
        },
    ]
    
    created = 0
    skipped = 0
    for promo_data in promotions_data:
        try:
            # Check if code already exists
            if promo_data.get('code'):
                existing = Promotion.objects.filter(code=promo_data['code']).first()
                if existing:
                    skipped += 1
                    continue
            
            promo = Promotion.objects.create(**promo_data)
            created += 1
            status = "✅" if promo.is_active else "⏸️"
            print(f"  {status} Created: {promo.name} ({promo.promo_type}) - {promo.tenant.name}")
        except Exception as e:
            print(f"  ❌ Error creating '{promo_data['name']}': {str(e)}")
    
    if skipped > 0:
        print(f"  ⚠️  Skipped {skipped} existing promotions")
    print(f"✅ Created {created} new promotions, total: {Promotion.objects.count()}")

def main():
    print("=" * 70)
    print("🚀 COMPLETE TEST DATA SETUP")
    print("=" * 70)
    
    try:
        # Check if tenants exist
        if Tenant.objects.count() == 0:
            print("\n❌ No tenants found. Please run the multi-outlet setup first!")
            sys.exit(1)
        
        # Warning about data that will be deleted
        print("\n⚠️  WARNING: This script will DELETE existing:")
        print("   - All orders")
        print("   - All existing toppings/modifiers")
        print("   - All existing promotions")
        print("\n   Existing customers will be kept (or created if not exist)")
        print("\n   New test data will be created:")
        print("   - 20 Toppings")
        print("   - 15 Additions")
        print("   - 18 Promotions (all types: percentage, fixed, buy_x_get_y, bundle)")
        print("   - 30 Customers (if not exist)")
        print("   - 50+ Orders (last 7 days)")
        
        response = input("\n❓ Continue? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("\n❌ Setup cancelled by user.")
            sys.exit(0)
        
        print("\n🗑️  Clearing existing data...\n")
        
        # Delete existing data (DO NOT delete customers to preserve products)
        # DO NOT delete modifiers - it somehow cascades to products!
        print("  - Deleting orders...")
        Order.objects.all().delete()
        print("  - Deleting promotions...")
        Promotion.objects.all().delete()
        print("  - Data cleared!\n")
        
        # Create all test data
        print("Checking existing data before creation...")
        print(f"  - Products: {Product.all_objects.count()}")
        print(f"  - Categories: {Category.all_objects.count()}")
        print()
        
        create_toppings()
        create_additions()
        create_promotions()
        create_customers()
        create_orders()
        
        print("\n" + "=" * 70)
        print("✅ COMPLETE TEST DATA SETUP FINISHED!")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"  - Tenants: {Tenant.objects.count()}")
        print(f"  - Outlets: {Outlet.objects.count()}")
        print(f"  - Categories: {Category.all_objects.count()}")
        print(f"  - Products: {Product.all_objects.count()}")
        print(f"  - Toppings: {ProductModifier.objects.filter(type='topping').count()}")
        print(f"  - Additions: {ProductModifier.objects.filter(type='extra').count()}")
        print(f"  - Promotions: {Promotion.objects.count()} ({Promotion.objects.filter(is_active=True).count()} active)")
        print(f"  - Users: {User.objects.count()}")
        print(f"  - Customers: {Customer.objects.count()}")
        print(f"  - Orders: {Order.objects.count()}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
