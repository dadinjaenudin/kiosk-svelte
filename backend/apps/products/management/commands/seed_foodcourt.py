"""
Management command to seed food court demo data with 5 tenants
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, Outlet
from apps.products.models import Category, Product, ProductModifier
from apps.core.context import set_current_tenant, clear_tenant_context
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed food court data with 5 different tenants'

    def handle(self, *args, **options):
        clear_tenant_context()
        
        self.stdout.write(self.style.SUCCESS('🏪 Creating Food Court with 5 Tenants...'))
        
        # Define 5 Food Court Tenants
        tenants_data = [
            {
                'slug': 'warung-nasi-padang',
                'name': 'Warung Nasi Padang',
                'description': 'Masakan Padang Asli dengan bumbu rempah pilihan',
                'color': '#FF6B35',
                'categories': ['Nasi Padang', 'Sayur', 'Minuman'],
                'products': [
                    {'sku': 'NP-001', 'name': 'Rendang Sapi', 'category': 'Nasi Padang', 'price': 45000},
                    {'sku': 'NP-002', 'name': 'Ayam Pop', 'category': 'Nasi Padang', 'price': 38000},
                    {'sku': 'NP-003', 'name': 'Gulai Ikan', 'category': 'Nasi Padang', 'price': 42000},
                    {'sku': 'NP-004', 'name': 'Dendeng Balado', 'category': 'Nasi Padang', 'price': 50000},
                    {'sku': 'NP-005', 'name': 'Gulai Tunjang', 'category': 'Nasi Padang', 'price': 40000},
                    {'sku': 'NP-006', 'name': 'Sayur Nangka', 'category': 'Sayur', 'price': 15000},
                    {'sku': 'NP-007', 'name': 'Teh Talua', 'category': 'Minuman', 'price': 12000},
                ]
            },
            {
                'slug': 'mie-ayam-bakso',
                'name': 'Mie Ayam & Bakso',
                'description': 'Mie ayam dan bakso sapi pilihan sejak 1990',
                'color': '#F7931E',
                'categories': ['Mie', 'Bakso', 'Minuman'],
                'products': [
                    {'sku': 'MB-001', 'name': 'Mie Ayam Spesial', 'category': 'Mie', 'price': 25000},
                    {'sku': 'MB-002', 'name': 'Mie Ayam Jumbo', 'category': 'Mie', 'price': 32000},
                    {'sku': 'MB-003', 'name': 'Bakso Sapi', 'category': 'Bakso', 'price': 28000},
                    {'sku': 'MB-004', 'name': 'Bakso Urat', 'category': 'Bakso', 'price': 35000},
                    {'sku': 'MB-005', 'name': 'Bakso Campur', 'category': 'Bakso', 'price': 40000},
                    {'sku': 'MB-006', 'name': 'Es Teh Manis', 'category': 'Minuman', 'price': 6000},
                ]
            },
            {
                'slug': 'ayam-geprek',
                'name': 'Ayam Geprek Mantap',
                'description': 'Ayam geprek crispy dengan level pedas pilihan',
                'color': '#DC143C',
                'categories': ['Ayam Geprek', 'Nasi', 'Minuman'],
                'products': [
                    {'sku': 'AG-001', 'name': 'Ayam Geprek Original', 'category': 'Ayam Geprek', 'price': 28000},
                    {'sku': 'AG-002', 'name': 'Ayam Geprek Keju', 'category': 'Ayam Geprek', 'price': 35000},
                    {'sku': 'AG-003', 'name': 'Ayam Geprek Mozarella', 'category': 'Ayam Geprek', 'price': 40000},
                    {'sku': 'AG-004', 'name': 'Ayam Geprek Jumbo', 'category': 'Ayam Geprek', 'price': 45000},
                    {'sku': 'AG-005', 'name': 'Nasi Putih', 'category': 'Nasi', 'price': 5000},
                    {'sku': 'AG-006', 'name': 'Es Jeruk', 'category': 'Minuman', 'price': 8000},
                ]
            },
            {
                'slug': 'soto-betawi',
                'name': 'Soto Betawi H. Mamat',
                'description': 'Soto Betawi legendaris dengan kuah santan gurih',
                'color': '#FFC300',
                'categories': ['Soto', 'Tambahan', 'Minuman'],
                'products': [
                    {'sku': 'SB-001', 'name': 'Soto Betawi Daging', 'category': 'Soto', 'price': 38000},
                    {'sku': 'SB-002', 'name': 'Soto Betawi Babat', 'category': 'Soto', 'price': 35000},
                    {'sku': 'SB-003', 'name': 'Soto Betawi Paru', 'category': 'Soto', 'price': 35000},
                    {'sku': 'SB-004', 'name': 'Soto Betawi Campur', 'category': 'Soto', 'price': 45000},
                    {'sku': 'SB-005', 'name': 'Emping', 'category': 'Tambahan', 'price': 8000},
                    {'sku': 'SB-006', 'name': 'Es Kelapa', 'category': 'Minuman', 'price': 12000},
                ]
            },
            {
                'slug': 'nasi-goreng',
                'name': 'Nasi Goreng Abang',
                'description': 'Nasi goreng enak dengan berbagai varian',
                'color': '#28A745',
                'categories': ['Nasi Goreng', 'Minuman', 'Snack'],
                'products': [
                    {'sku': 'NG-001', 'name': 'Nasi Goreng Biasa', 'category': 'Nasi Goreng', 'price': 20000},
                    {'sku': 'NG-002', 'name': 'Nasi Goreng Spesial', 'category': 'Nasi Goreng', 'price': 28000},
                    {'sku': 'NG-003', 'name': 'Nasi Goreng Seafood', 'category': 'Nasi Goreng', 'price': 40000},
                    {'sku': 'NG-004', 'name': 'Nasi Goreng Pete', 'category': 'Nasi Goreng', 'price': 32000},
                    {'sku': 'NG-005', 'name': 'Nasi Goreng Kambing', 'category': 'Nasi Goreng', 'price': 45000},
                    {'sku': 'NG-006', 'name': 'Kerupuk', 'category': 'Snack', 'price': 5000},
                    {'sku': 'NG-007', 'name': 'Es Teh', 'category': 'Minuman', 'price': 6000},
                ]
            }
        ]
        
        # Create Food Court outlet (shared location)
        self.stdout.write('Creating Food Court location...')
        
        # Create each tenant with products
        for tenant_data in tenants_data:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(self.style.SUCCESS(f"Creating Tenant: {tenant_data['name']}"))
            self.stdout.write('='*60)
            
            # Create Tenant
            tenant, created = Tenant.objects.get_or_create(
                slug=tenant_data['slug'],
                defaults={
                    'name': tenant_data['name'],
                    'description': tenant_data['description'],
                    'primary_color': tenant_data['color'],
                    'secondary_color': tenant_data['color'],
                    'phone': '021-12345678',
                    'tax_rate': Decimal('10.00'),
                    'service_charge_rate': Decimal('5.00'),
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Tenant created: {tenant.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Tenant exists: {tenant.name}'))
            
            # Set tenant context
            set_current_tenant(tenant)
            
            # Create Outlet for this tenant in Food Court
            outlet, _ = Outlet.objects.get_or_create(
                tenant=tenant,
                slug=f'foodcourt-{tenant.slug}',
                defaults={
                    'name': f'{tenant.name} - Food Court',
                    'address': 'Food Court Mall Plaza Senayan Lt. 3',
                    'city': 'Jakarta Pusat',
                    'province': 'DKI Jakarta',
                    'postal_code': '10270',
                    'phone': '021-12345678',
                }
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Outlet: {outlet.name}'))
            
            # Create User for this tenant
            username = tenant_data['slug']
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@foodcourt.com',
                    'first_name': tenant.name.split()[0],
                    'last_name': 'Owner',
                    'role': 'cashier',
                    'tenant': tenant,
                    'outlet': outlet,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ User: {username} (password: password123)'))
            
            # Create Categories
            self.stdout.write('Creating categories...')
            categories = {}
            for cat_name in tenant_data['categories']:
                cat, _ = Category.objects.get_or_create(
                    tenant=tenant,
                    name=cat_name,
                    defaults={'sort_order': len(categories) + 1}
                )
                categories[cat_name] = cat
                self.stdout.write(f'  ✓ {cat.name}')
            
            # Create Products
            self.stdout.write('Creating products...')
            for prod_data in tenant_data['products']:
                prod, created = Product.objects.get_or_create(
                    tenant=tenant,
                    sku=prod_data['sku'],
                    defaults={
                        'category': categories[prod_data['category']],
                        'name': prod_data['name'],
                        'description': f"{prod_data['name']} dari {tenant.name}",
                        'price': Decimal(str(prod_data['price'])),
                        'is_available': True,
                        'is_active': True,
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ {prod.name} - Rp {prod.price:,.0f}')
            
            # Clear context for next tenant
            clear_tenant_context()
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ Food Court Data Seeding Complete!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        total_tenants = Tenant.objects.count()
        total_products = Product.all_objects.count()
        total_categories = Category.all_objects.count()
        
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'   Tenants: {total_tenants}')
        self.stdout.write(f'   Products: {total_products}')
        self.stdout.write(f'   Categories: {total_categories}')
        
        self.stdout.write('\n🏪 Tenants Created:')
        for tenant in Tenant.objects.all():
            product_count = Product.all_objects.filter(tenant=tenant).count()
            self.stdout.write(f'   • {tenant.name} ({product_count} products) - Color: {tenant.primary_color}')
        
        self.stdout.write('\n🌐 Access Food Court Kiosk:')
        self.stdout.write('   http://localhost:5174/kiosk')
        self.stdout.write('\n💡 Users can browse ALL menus and filter by tenant!')
