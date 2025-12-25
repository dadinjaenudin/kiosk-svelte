"""
Management command untuk seed dummy data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, Outlet
from apps.products.models import Category, Product, ProductModifier
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.core.context import set_current_tenant, clear_tenant_context
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed dummy data untuk demo POS system'

    def handle(self, *args, **options):
        # Clear any existing context
        clear_tenant_context()
        
        self.stdout.write(self.style.SUCCESS('🌱 Starting data seeding...'))
        
        # 1. Create Tenant
        self.stdout.write('Creating tenant...')
        tenant, created = Tenant.objects.get_or_create(
            slug='warung-makan-sedap',
            defaults={
                'name': 'Warung Makan Sedap',
                'description': 'Restoran Indonesia dengan menu tradisional dan modern',
                'phone': '021-12345678',
                'email': 'info@warungs edap.com',
                'tax_rate': Decimal('10.00'),
                'service_charge_rate': Decimal('5.00'),
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Tenant: {tenant.name}'))
        
        # Set tenant context for the rest of the seeding
        set_current_tenant(tenant)
        
        # 2. Create Outlets
        self.stdout.write('Creating outlets...')
        outlet1, _ = Outlet.objects.get_or_create(
            tenant=tenant,
            slug='cabang-pusat',
            defaults={
                'name': 'Cabang Pusat',
                'address': 'Jl. Sudirman No. 123',
                'city': 'Jakarta Pusat',
                'province': 'DKI Jakarta',
                'postal_code': '10220',
                'phone': '021-12345678',
                'latitude': Decimal('-6.208763'),
                'longitude': Decimal('106.845599'),
            }
        )
        
        outlet2, _ = Outlet.objects.get_or_create(
            tenant=tenant,
            slug='cabang-selatan',
            defaults={
                'name': 'Cabang Selatan',
                'address': 'Jl. TB Simatupang No. 456',
                'city': 'Jakarta Selatan',
                'province': 'DKI Jakarta',
                'postal_code': '12430',
                'phone': '021-87654321',
                'latitude': Decimal('-6.300000'),
                'longitude': Decimal('106.800000'),
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Outlets: {outlet1.name}, {outlet2.name}'))
        
        # 3. Create Users
        self.stdout.write('Creating users...')
        
        # Admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@warungsedap.com',
                'first_name': 'Admin',
                'last_name': 'System',
                'role': 'admin',
                'tenant': tenant,
                'outlet': outlet1,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✓ Admin user created (username: admin, password: admin123)'))
        
        # Cashier user
        cashier, created = User.objects.get_or_create(
            username='cashier',
            defaults={
                'email': 'cashier@warungsedap.com',
                'first_name': 'Budi',
                'last_name': 'Santoso',
                'role': 'cashier',
                'tenant': tenant,
                'outlet': outlet1,
            }
        )
        if created:
            cashier.set_password('cashier123')
            cashier.save()
            self.stdout.write(self.style.SUCCESS('✓ Cashier user created (username: cashier, password: cashier123)'))
        
        # 4. Create Categories
        self.stdout.write('Creating categories...')
        categories_data = [
            {'name': 'Makanan Utama', 'sort_order': 1},
            {'name': 'Makanan Ringan', 'sort_order': 2},
            {'name': 'Minuman Dingin', 'sort_order': 3},
            {'name': 'Minuman Panas', 'sort_order': 4},
            {'name': 'Dessert', 'sort_order': 5},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(
                tenant=tenant,
                name=cat_data['name'],
                defaults={'sort_order': cat_data['sort_order']}
            )
            categories[cat_data['name']] = cat
            self.stdout.write(f'  ✓ {cat.name}')
        
        # 5. Create Products
        self.stdout.write('Creating products...')
        products_data = [
            # Makanan Utama
            {'category': 'Makanan Utama', 'sku': 'FD-001', 'name': 'Nasi Goreng Spesial', 'price': 35000, 'desc': 'Nasi goreng dengan telur, ayam, dan sayuran'},
            {'category': 'Makanan Utama', 'sku': 'FD-002', 'name': 'Mie Goreng', 'price': 30000, 'desc': 'Mie goreng pedas dengan topping telur'},
            {'category': 'Makanan Utama', 'sku': 'FD-003', 'name': 'Ayam Penyet', 'price': 40000, 'desc': 'Ayam goreng dengan sambal terasi'},
            {'category': 'Makanan Utama', 'sku': 'FD-004', 'name': 'Nasi Uduk Komplit', 'price': 35000, 'desc': 'Nasi uduk dengan lauk lengkap'},
            {'category': 'Makanan Utama', 'sku': 'FD-005', 'name': 'Soto Ayam', 'price': 32000, 'desc': 'Soto ayam kuning dengan nasi'},
            
            # Makanan Ringan
            {'category': 'Makanan Ringan', 'sku': 'SN-001', 'name': 'Pisang Goreng', 'price': 15000, 'desc': 'Pisang goreng crispy 5 potong'},
            {'category': 'Makanan Ringan', 'sku': 'SN-002', 'name': 'Tahu Isi', 'price': 18000, 'desc': 'Tahu isi sayuran 5 potong'},
            {'category': 'Makanan Ringan', 'sku': 'SN-003', 'name': 'Lumpia Basah', 'price': 20000, 'desc': 'Lumpia basah isi rebung 3 potong'},
            {'category': 'Makanan Ringan', 'sku': 'SN-004', 'name': 'Mendoan', 'price': 12000, 'desc': 'Tempe mendoan crispy 5 potong'},
            
            # Minuman Dingin
            {'category': 'Minuman Dingin', 'sku': 'DR-001', 'name': 'Es Teh Manis', 'price': 8000, 'desc': 'Es teh manis segar'},
            {'category': 'Minuman Dingin', 'sku': 'DR-002', 'name': 'Es Jeruk', 'price': 12000, 'desc': 'Es jeruk peras segar'},
            {'category': 'Minuman Dingin', 'sku': 'DR-003', 'name': 'Es Campur', 'price': 18000, 'desc': 'Es campur dengan berbagai topping'},
            {'category': 'Minuman Dingin', 'sku': 'DR-004', 'name': 'Jus Alpukat', 'price': 20000, 'desc': 'Jus alpukat kental'},
            {'category': 'Minuman Dingin', 'sku': 'DR-005', 'name': 'Es Kelapa Muda', 'price': 15000, 'desc': 'Kelapa muda dingin'},
            
            # Minuman Panas
            {'category': 'Minuman Panas', 'sku': 'HD-001', 'name': 'Teh Panas', 'price': 6000, 'desc': 'Teh panas manis'},
            {'category': 'Minuman Panas', 'sku': 'HD-002', 'name': 'Kopi Hitam', 'price': 10000, 'desc': 'Kopi hitam robusta'},
            {'category': 'Minuman Panas', 'sku': 'HD-003', 'name': 'Kopi Susu', 'price': 15000, 'desc': 'Kopi susu gula aren'},
            
            # Dessert
            {'category': 'Dessert', 'sku': 'DS-001', 'name': 'Es Krim Goreng', 'price': 25000, 'desc': 'Es krim goreng dengan topping'},
            {'category': 'Dessert', 'sku': 'DS-002', 'name': 'Pancake', 'price': 22000, 'desc': 'Pancake dengan maple syrup'},
        ]
        
        products = []
        for prod_data in products_data:
            prod, created = Product.objects.get_or_create(
                tenant=tenant,
                sku=prod_data['sku'],
                defaults={
                    'category': categories[prod_data['category']],
                    'name': prod_data['name'],
                    'description': prod_data['desc'],
                    'price': Decimal(str(prod_data['price'])),
                    'is_available': True,
                    'is_active': True,
                }
            )
            products.append(prod)
            if created:
                self.stdout.write(f'  ✓ {prod.name} - Rp {prod.price:,.0f}')
        
        # 6. Create Product Modifiers
        self.stdout.write('Creating product modifiers...')
        
        # Modifier untuk Nasi Goreng
        nasi_goreng = Product.objects.get(sku='FD-001')
        modifiers_ng = [
            {'name': 'Extra Telur', 'type': 'extra', 'price': 5000},
            {'name': 'Extra Ayam', 'type': 'extra', 'price': 8000},
            {'name': 'Level Pedas 1', 'type': 'spicy', 'price': 0},
            {'name': 'Level Pedas 2', 'type': 'spicy', 'price': 0},
            {'name': 'Level Pedas 3', 'type': 'spicy', 'price': 0},
        ]
        for mod_data in modifiers_ng:
            ProductModifier.objects.get_or_create(
                product=nasi_goreng,
                name=mod_data['name'],
                defaults={
                    'type': mod_data['type'],
                    'price_adjustment': Decimal(str(mod_data['price'])),
                }
            )
        
        # Modifier untuk minuman
        for sku in ['DR-001', 'DR-002', 'HD-001', 'HD-002', 'HD-003']:
            try:
                drink = Product.objects.get(sku=sku)
                ProductModifier.objects.get_or_create(
                    product=drink,
                    name='Less Sugar',
                    defaults={'type': 'extra', 'price_adjustment': Decimal('0')}
                )
                ProductModifier.objects.get_or_create(
                    product=drink,
                    name='Extra Ice',
                    defaults={'type': 'extra', 'price_adjustment': Decimal('0')}
                )
            except Product.DoesNotExist:
                pass
        
        self.stdout.write(self.style.SUCCESS('✓ Product modifiers created'))
        
        # 7. Create sample orders
        self.stdout.write('Creating sample orders...')
        
        # Order 1
        order1 = Order.objects.create(
            tenant=tenant,
            outlet=outlet1,
            cashier=cashier,
            status='completed',
            payment_status='paid',
            table_number='A1',
        )
        
        # Add items to order 1
        nasi_goreng = Product.objects.get(sku='FD-001')
        OrderItem.objects.create(
            order=order1,
            product=nasi_goreng,
            product_name=nasi_goreng.name,
            product_sku=nasi_goreng.sku,
            quantity=2,
            unit_price=nasi_goreng.price,
        )
        
        es_teh = Product.objects.get(sku='DR-001')
        OrderItem.objects.create(
            order=order1,
            product=es_teh,
            product_name=es_teh.name,
            product_sku=es_teh.sku,
            quantity=2,
            unit_price=es_teh.price,
        )
        
        order1.calculate_totals()
        
        # Create payment for order 1
        Payment.objects.create(
            order=order1,
            payment_method='cash',
            amount=order1.total_amount,
            status='success',
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Sample order created: {order1.order_number}'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('✅ Data seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'\nTenant: {tenant.name}')
        self.stdout.write(f'Outlets: {Outlet.objects.filter(tenant=tenant).count()}')
        self.stdout.write(f'Categories: {Category.objects.filter(tenant=tenant).count()}')
        self.stdout.write(f'Products: {Product.objects.filter(tenant=tenant).count()}')
        self.stdout.write(f'Users: {User.objects.filter(tenant=tenant).count()}')
        self.stdout.write(f'Orders: {Order.objects.filter(tenant=tenant).count()}')
        self.stdout.write('\n👤 Login credentials:')
        self.stdout.write('   Admin    - username: admin, password: admin123')
        self.stdout.write('   Cashier  - username: cashier, password: cashier123')
        self.stdout.write('\n🌐 Access the Kiosk Mode at: http://localhost:5173/kiosk')
        
        # Clear tenant context
        clear_tenant_context()
