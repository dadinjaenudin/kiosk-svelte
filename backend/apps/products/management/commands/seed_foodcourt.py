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
                    {'sku': 'NP-001', 'name': 'Rendang Sapi', 'category': 'Nasi Padang', 'price': 45000, 'is_popular': True, 'has_promo': False, 'tags': 'rendang,sapi,padang,populer'},
                    {'sku': 'NP-002', 'name': 'Ayam Pop', 'category': 'Nasi Padang', 'price': 38000, 'is_popular': False, 'has_promo': True, 'promo_price': 32000, 'tags': 'ayam,pop,padang,promo'},
                    {'sku': 'NP-003', 'name': 'Gulai Ikan', 'category': 'Nasi Padang', 'price': 42000, 'is_popular': True, 'has_promo': True, 'promo_price': 36000, 'tags': 'gulai,ikan,padang,promo,populer'},
                    {'sku': 'NP-004', 'name': 'Dendeng Balado', 'category': 'Nasi Padang', 'price': 50000, 'is_popular': False, 'has_promo': False, 'tags': 'dendeng,balado,pedas,padang'},
                    {'sku': 'NP-005', 'name': 'Gulai Tunjang', 'category': 'Nasi Padang', 'price': 40000, 'is_popular': False, 'has_promo': False, 'tags': 'gulai,tunjang,padang'},
                    {'sku': 'NP-006', 'name': 'Sayur Nangka', 'category': 'Sayur', 'price': 15000, 'is_popular': False, 'has_promo': False, 'tags': 'sayur,nangka,vegetarian'},
                    {'sku': 'NP-007', 'name': 'Teh Talua', 'category': 'Minuman', 'price': 12000, 'is_popular': False, 'has_promo': False, 'tags': 'minuman,teh,tradisional'},
                ]
            },
            {
                'slug': 'mie-ayam-bakso',
                'name': 'Mie Ayam & Bakso',
                'description': 'Mie ayam dan bakso sapi pilihan sejak 1990',
                'color': '#F7931E',
                'categories': ['Mie', 'Bakso', 'Minuman'],
                'products': [
                    {'sku': 'MB-001', 'name': 'Mie Ayam Spesial', 'category': 'Mie', 'price': 25000, 'is_popular': True, 'has_promo': False, 'tags': 'mie,ayam,bakso,populer'},
                    {'sku': 'MB-002', 'name': 'Mie Ayam Jumbo', 'category': 'Mie', 'price': 32000, 'is_popular': True, 'has_promo': True, 'promo_price': 27000, 'tags': 'mie,ayam,jumbo,promo,populer'},
                    {'sku': 'MB-003', 'name': 'Bakso Sapi', 'category': 'Bakso', 'price': 28000, 'is_popular': False, 'has_promo': False, 'tags': 'bakso,sapi,kuah'},
                    {'sku': 'MB-004', 'name': 'Bakso Urat', 'category': 'Bakso', 'price': 35000, 'is_popular': False, 'has_promo': True, 'promo_price': 30000, 'tags': 'bakso,urat,promo'},
                    {'sku': 'MB-005', 'name': 'Bakso Campur', 'category': 'Bakso', 'price': 40000, 'is_popular': False, 'has_promo': False, 'tags': 'bakso,campur,komplit'},
                    {'sku': 'MB-006', 'name': 'Es Teh Manis', 'category': 'Minuman', 'price': 6000, 'is_popular': True, 'has_promo': False, 'tags': 'minuman,es,teh,populer'},
                ]
            },
            {
                'slug': 'ayam-geprek',
                'name': 'Ayam Geprek Mantap',
                'description': 'Ayam geprek crispy dengan level pedas pilihan',
                'color': '#DC143C',
                'categories': ['Ayam Geprek', 'Nasi', 'Minuman'],
                'products': [
                    {'sku': 'AG-001', 'name': 'Ayam Geprek Original', 'category': 'Ayam Geprek', 'price': 28000, 'is_popular': True, 'has_promo': False, 'tags': 'ayam,geprek,pedas,populer'},
                    {'sku': 'AG-002', 'name': 'Ayam Geprek Keju', 'category': 'Ayam Geprek', 'price': 35000, 'is_popular': True, 'has_promo': True, 'promo_price': 30000, 'tags': 'ayam,geprek,keju,promo,populer'},
                    {'sku': 'AG-003', 'name': 'Ayam Geprek Mozarella', 'category': 'Ayam Geprek', 'price': 40000, 'is_popular': False, 'has_promo': False, 'tags': 'ayam,geprek,mozarella,keju'},
                    {'sku': 'AG-004', 'name': 'Ayam Geprek Jumbo', 'category': 'Ayam Geprek', 'price': 45000, 'is_popular': True, 'has_promo': False, 'tags': 'ayam,geprek,jumbo,besar,populer'},
                    {'sku': 'AG-005', 'name': 'Nasi Putih', 'category': 'Nasi', 'price': 5000, 'is_popular': False, 'has_promo': False, 'tags': 'nasi,putih,tambahan'},
                    {'sku': 'AG-006', 'name': 'Es Jeruk', 'category': 'Minuman', 'price': 8000, 'is_popular': False, 'has_promo': False, 'tags': 'minuman,es,jeruk,segar'},
                ]
            },
            {
                'slug': 'soto-betawi',
                'name': 'Soto Betawi H. Mamat',
                'description': 'Soto Betawi legendaris dengan kuah santan gurih',
                'color': '#FFC300',
                'categories': ['Soto', 'Tambahan', 'Minuman'],
                'products': [
                    {'sku': 'SB-001', 'name': 'Soto Betawi Daging', 'category': 'Soto', 'price': 38000, 'is_popular': True, 'has_promo': False, 'tags': 'soto,betawi,daging,populer'},
                    {'sku': 'SB-002', 'name': 'Soto Betawi Babat', 'category': 'Soto', 'price': 35000, 'is_popular': True, 'has_promo': True, 'promo_price': 29000, 'tags': 'soto,betawi,babat,promo,populer'},
                    {'sku': 'SB-003', 'name': 'Soto Betawi Paru', 'category': 'Soto', 'price': 35000, 'is_popular': False, 'has_promo': False, 'tags': 'soto,betawi,paru'},
                    {'sku': 'SB-004', 'name': 'Soto Betawi Campur', 'category': 'Soto', 'price': 45000, 'is_popular': False, 'has_promo': False, 'tags': 'soto,betawi,campur,komplit'},
                    {'sku': 'SB-005', 'name': 'Emping', 'category': 'Tambahan', 'price': 8000, 'is_popular': False, 'has_promo': False, 'tags': 'tambahan,emping,kerupuk'},
                    {'sku': 'SB-006', 'name': 'Es Kelapa', 'category': 'Minuman', 'price': 12000, 'is_popular': False, 'has_promo': False, 'tags': 'minuman,es,kelapa,segar'},
                ]
            },
            {
                'slug': 'nasi-goreng',
                'name': 'Nasi Goreng Abang',
                'description': 'Nasi goreng enak dengan berbagai varian',
                'color': '#28A745',
                'categories': ['Nasi Goreng', 'Minuman', 'Snack'],
                'products': [
                    {'sku': 'NG-001', 'name': 'Nasi Goreng Biasa', 'category': 'Nasi Goreng', 'price': 20000, 'is_popular': True, 'has_promo': False, 'tags': 'nasi,goreng,populer'},
                    {'sku': 'NG-002', 'name': 'Nasi Goreng Spesial', 'category': 'Nasi Goreng', 'price': 28000, 'is_popular': True, 'has_promo': True, 'promo_price': 23000, 'tags': 'nasi,goreng,spesial,promo,populer'},
                    {'sku': 'NG-003', 'name': 'Nasi Goreng Seafood', 'category': 'Nasi Goreng', 'price': 40000, 'is_popular': False, 'has_promo': False, 'tags': 'nasi,goreng,seafood,udang'},
                    {'sku': 'NG-004', 'name': 'Nasi Goreng Pete', 'category': 'Nasi Goreng', 'price': 32000, 'is_popular': False, 'has_promo': True, 'promo_price': 27000, 'tags': 'nasi,goreng,pete,promo'},
                    {'sku': 'NG-005', 'name': 'Nasi Goreng Kambing', 'category': 'Nasi Goreng', 'price': 45000, 'is_popular': True, 'has_promo': False, 'tags': 'nasi,goreng,kambing,populer'},
                    {'sku': 'NG-006', 'name': 'Kerupuk', 'category': 'Snack', 'price': 5000, 'is_popular': False, 'has_promo': False, 'tags': 'kerupuk,tambahan,snack'},
                    {'sku': 'NG-007', 'name': 'Es Teh', 'category': 'Minuman', 'price': 6000, 'is_popular': False, 'has_promo': False, 'tags': 'minuman,es,teh'},
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
            product_objects = {}  # Store products by SKU for modifiers
            for prod_data in tenant_data['products']:
                defaults = {
                    'category': categories[prod_data['category']],
                    'name': prod_data['name'],
                    'description': f"{prod_data['name']} dari {tenant.name}",
                    'price': Decimal(str(prod_data['price'])),
                    'is_available': True,
                    'is_active': True,
                    'is_popular': prod_data.get('is_popular', False),
                    'has_promo': prod_data.get('has_promo', False),
                    'tags': prod_data.get('tags', ''),
                }
                
                # Add promo_price if has_promo is True
                if prod_data.get('has_promo') and 'promo_price' in prod_data:
                    defaults['promo_price'] = Decimal(str(prod_data['promo_price']))
                
                prod, created = Product.objects.get_or_create(
                    tenant=tenant,
                    sku=prod_data['sku'],
                    defaults=defaults
                )
                product_objects[prod_data['sku']] = prod  # Store for modifiers
                if created:
                    promo_info = ''
                    if prod.has_promo and prod.promo_price:
                        promo_info = f' (Promo: Rp {prod.promo_price:,.0f})'
                    popular_mark = ' ⭐' if prod.is_popular else ''
                    self.stdout.write(f'  ✓ {prod.name} - Rp {prod.price:,.0f}{promo_info}{popular_mark}')
            
            # Create Modifiers
            self.stdout.write('Creating modifiers...')
            self._create_modifiers(tenant, product_objects, tenant_data['slug'])
            
            # Clear context for next tenant
            clear_tenant_context()
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ Food Court Data Seeding Complete!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        total_tenants = Tenant.objects.count()
        total_products = Product.all_objects.count()
        total_categories = Category.all_objects.count()
        total_modifiers = ProductModifier.objects.count()
        total_popular = Product.all_objects.filter(is_popular=True).count()
        total_promo = Product.all_objects.filter(has_promo=True).count()
        total_popular_promo = Product.all_objects.filter(is_popular=True, has_promo=True).count()
        
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'   Tenants: {total_tenants}')
        self.stdout.write(f'   Products: {total_products}')
        self.stdout.write(f'   Categories: {total_categories}')
        self.stdout.write(f'   Modifiers: {total_modifiers}')
        self.stdout.write(f'   ⭐ Popular: {total_popular}')
        self.stdout.write(f'   🔥 Promo: {total_promo}')
        self.stdout.write(f'   🌟 Popular + Promo: {total_popular_promo}')
        
        self.stdout.write('\n🏪 Tenants Created:')
        for tenant in Tenant.objects.all():
            product_count = Product.all_objects.filter(tenant=tenant).count()
            popular_count = Product.all_objects.filter(tenant=tenant, is_popular=True).count()
            promo_count = Product.all_objects.filter(tenant=tenant, has_promo=True).count()
            self.stdout.write(
                f'   • {tenant.name} ({product_count} products, {popular_count} popular, {promo_count} promo) - Color: {tenant.primary_color}'
            )
        
        self.stdout.write('\n🌐 Access Food Court Kiosk:')
        self.stdout.write('   http://localhost:5174/kiosk')
        self.stdout.write('\n💡 Users can browse ALL menus and filter by tenant!')
    
    def _create_modifiers(self, tenant, products, tenant_slug):
        """Create product modifiers based on tenant type"""
        
        modifiers_config = {
            'warung-nasi-padang': [
                # Rendang, Ayam Pop, etc - portion size
                {
                    'products': ['NP-001', 'NP-002', 'NP-003', 'NP-004', 'NP-005'],
                    'modifiers': [
                        {'name': 'Porsi Kecil', 'type': 'size', 'price': -5000, 'sort': 1},
                        {'name': 'Porsi Sedang', 'type': 'size', 'price': 0, 'sort': 2},
                        {'name': 'Porsi Besar', 'type': 'size', 'price': 8000, 'sort': 3},
                        {'name': 'Extra Sambal', 'type': 'extra', 'price': 2000, 'sort': 4},
                        {'name': 'Extra Nasi', 'type': 'extra', 'price': 5000, 'sort': 5},
                    ]
                },
            ],
            'mie-ayam-bakso': [
                {
                    'products': ['MB-001', 'MB-002'],  # Mie ayam
                    'modifiers': [
                        {'name': 'Pangsit Goreng', 'type': 'extra', 'price': 3000, 'sort': 1},
                        {'name': 'Extra Ayam', 'type': 'extra', 'price': 8000, 'sort': 2},
                        {'name': 'Extra Mie', 'type': 'extra', 'price': 5000, 'sort': 3},
                        {'name': 'Tidak Pakai Sawi', 'type': 'extra', 'price': 0, 'sort': 4},
                    ]
                },
                {
                    'products': ['MB-003', 'MB-004', 'MB-005'],  # Bakso
                    'modifiers': [
                        {'name': 'Extra Bakso (2 pcs)', 'type': 'extra', 'price': 10000, 'sort': 1},
                        {'name': 'Extra Mie', 'type': 'extra', 'price': 5000, 'sort': 2},
                        {'name': 'Kuah Pedas', 'type': 'spicy', 'price': 0, 'sort': 3},
                        {'name': 'Kuah Ekstra', 'type': 'extra', 'price': 3000, 'sort': 4},
                    ]
                },
            ],
            'ayam-geprek': [
                {
                    'products': ['AG-001', 'AG-002', 'AG-003', 'AG-004'],  # All ayam geprek
                    'modifiers': [
                        {'name': 'Level 1 (Tidak Pedas)', 'type': 'spicy', 'price': 0, 'sort': 1},
                        {'name': 'Level 2 (Sedang)', 'type': 'spicy', 'price': 0, 'sort': 2},
                        {'name': 'Level 3 (Pedas)', 'type': 'spicy', 'price': 0, 'sort': 3},
                        {'name': 'Level 4 (Sangat Pedas)', 'type': 'spicy', 'price': 0, 'sort': 4},
                        {'name': 'Level 5 (Extra Pedas)', 'type': 'spicy', 'price': 0, 'sort': 5},
                        {'name': 'Extra Keju', 'type': 'topping', 'price': 7000, 'sort': 6},
                        {'name': 'Extra Nasi', 'type': 'extra', 'price': 5000, 'sort': 7},
                        {'name': 'Tanpa Nasi', 'type': 'extra', 'price': -5000, 'sort': 8},
                    ]
                },
            ],
            'soto-betawi': [
                {
                    'products': ['SB-001', 'SB-002', 'SB-003', 'SB-004'],  # All soto
                    'modifiers': [
                        {'name': 'Kuah Santan', 'type': 'sauce', 'price': 0, 'sort': 1},
                        {'name': 'Kuah Bening', 'type': 'sauce', 'price': 0, 'sort': 2},
                        {'name': 'Emping', 'type': 'topping', 'price': 5000, 'sort': 3},
                        {'name': 'Jeruk Limau', 'type': 'extra', 'price': 2000, 'sort': 4},
                        {'name': 'Extra Daging', 'type': 'extra', 'price': 12000, 'sort': 5},
                        {'name': 'Sambal Rawit', 'type': 'spicy', 'price': 0, 'sort': 6},
                    ]
                },
            ],
            'nasi-goreng': [
                {
                    'products': ['NG-001', 'NG-002', 'NG-003', 'NG-004', 'NG-005'],  # All nasi goreng
                    'modifiers': [
                        {'name': 'Telur Mata Sapi', 'type': 'topping', 'price': 5000, 'sort': 1},
                        {'name': 'Telur Dadar', 'type': 'topping', 'price': 4000, 'sort': 2},
                        {'name': 'Extra Ayam', 'type': 'extra', 'price': 10000, 'sort': 3},
                        {'name': 'Extra Seafood', 'type': 'extra', 'price': 15000, 'sort': 4},
                        {'name': 'Kerupuk', 'type': 'extra', 'price': 3000, 'sort': 5},
                        {'name': 'Acar', 'type': 'extra', 'price': 2000, 'sort': 6},
                        {'name': 'Level Pedas (1-5)', 'type': 'spicy', 'price': 0, 'sort': 7},
                    ]
                },
            ],
        }
        
        if tenant_slug in modifiers_config:
            for config in modifiers_config[tenant_slug]:
                for sku in config['products']:
                    if sku in products:
                        product = products[sku]
                        for mod_data in config['modifiers']:
                            modifier, created = ProductModifier.objects.get_or_create(
                                product=product,
                                name=mod_data['name'],
                                defaults={
                                    'type': mod_data['type'],
                                    'price_adjustment': Decimal(str(mod_data['price'])),
                                    'is_active': True,
                                    'sort_order': mod_data['sort']
                                }
                            )
                            if created:
                                price_str = f"+Rp {abs(mod_data['price']):,.0f}" if mod_data['price'] > 0 else (
                                    f"-Rp {abs(mod_data['price']):,.0f}" if mod_data['price'] < 0 else "Rp 0"
                                )
                                self.stdout.write(f"    ✓ {product.name}: {modifier.name} ({price_str})")
