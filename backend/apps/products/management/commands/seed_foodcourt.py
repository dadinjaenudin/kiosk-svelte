"""
Management command to seed food court sample data with search features
Usage: python manage.py seed_foodcourt
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed food court sample data with search features (popular, promo, available)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting seed process...'))
        
        if options['clear']:
            self.stdout.write('🗑️  Clearing existing search flags...')
            Product.objects.all().update(
                is_popular=False,
                has_promo=False,
                promo_price=None
            )
        
        try:
            with transaction.atomic():
                self._seed_ayam_geprek()
                self._seed_soto_house()
                self._seed_nasi_padang()
                self._seed_mie_ayam()
                self._seed_minuman()
                
            self.stdout.write(self.style.SUCCESS('✅ Sample data seeded successfully!'))
            self._print_summary()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            raise
    
    def _seed_ayam_geprek(self):
        """Seed Ayam Geprek Mantap products"""
        self.stdout.write('🍗 Seeding Ayam Geprek Mantap...')
        
        updates = {
            'AG-001': {  # Ayam Geprek Original
                'is_popular': True,
                'has_promo': False,
                'is_available': True,
                'tags': 'pedas,ayam,geprek,populer'
            },
            'AG-002': {  # Ayam Geprek Keju
                'is_popular': True,
                'has_promo': True,
                'promo_price': Decimal('38000'),  # Original: 42000
                'is_available': True,
                'tags': 'pedas,ayam,geprek,keju,promo,populer'
            },
            'AG-003': {  # Ayam Geprek Sambal Matah
                'is_popular': False,
                'has_promo': False,
                'is_available': True,
                'tags': 'pedas,ayam,geprek,sambal matah'
            },
            'AG-004': {  # Ayam Geprek Jumbo
                'is_popular': True,
                'has_promo': False,
                'is_available': True,
                'tags': 'pedas,ayam,geprek,jumbo,besar,populer'
            },
            'AG-005': {  # Ayam Geprek Mozarella
                'is_popular': False,
                'has_promo': True,
                'promo_price': Decimal('43000'),  # Original: 48000
                'is_available': True,
                'tags': 'pedas,ayam,geprek,keju,mozarella,promo'
            },
            'AG-006': {  # Ayam Geprek Pedas Gila
                'is_popular': True,
                'has_promo': False,
                'is_available': False,  # SOLD OUT
                'tags': 'pedas,ayam,geprek,extra pedas,sold out'
            },
        }
        
        count = self._apply_updates(updates)
        self.stdout.write(f'   ✓ Updated {count} Ayam Geprek products')
    
    def _seed_soto_house(self):
        """Seed Soto House products"""
        self.stdout.write('🍜 Seeding Soto House...')
        
        updates = {
            'SH-001': {  # Soto Ayam
                'is_popular': True,
                'has_promo': False,
                'is_available': True,
                'tags': 'soto,ayam,berkuah,hangat,populer'
            },
            'SH-002': {  # Soto Betawi
                'is_popular': True,
                'has_promo': True,
                'promo_price': Decimal('27000'),  # Original: 32000
                'is_available': True,
                'tags': 'soto,sapi,berkuah,betawi,promo,populer'
            },
            'SH-003': {  # Soto Kudus
                'is_popular': False,
                'has_promo': False,
                'is_available': True,
                'tags': 'soto,ayam,berkuah,kudus'
            },
            'SH-004': {  # Soto Daging
                'is_popular': False,
                'has_promo': False,
                'is_available': True,
                'tags': 'soto,sapi,daging,berkuah'
            },
        }
        
        count = self._apply_updates(updates)
        self.stdout.write(f'   ✓ Updated {count} Soto House products')
    
    def _seed_nasi_padang(self):
        """Seed Nasi Padang Sederhana products"""
        self.stdout.write('🍛 Seeding Nasi Padang Sederhana...')
        
        updates = {
            'NP-001': {  # Nasi Rendang
                'is_popular': True,
                'has_promo': False,
                'is_available': True,
                'tags': 'nasi,rendang,padang,populer'
            },
            'NP-002': {  # Nasi Gulai Ayam
                'is_popular': False,
                'has_promo': True,
                'promo_price': Decimal('22000'),  # Original: 28000
                'is_available': True,
                'tags': 'nasi,gulai,ayam,padang,promo'
            },
            'NP-003': {  # Nasi Gulai Kambing
                'is_popular': True,
                'has_promo': True,
                'promo_price': Decimal('38000'),  # Original: 45000
                'is_available': True,
                'tags': 'nasi,gulai,kambing,padang,promo,populer'
            },
            'NP-004': {  # Nasi Dendeng Balado
                'is_popular': False,
                'has_promo': False,
                'is_available': True,
                'tags': 'nasi,dendeng,balado,pedas,padang'
            },
            'NP-005': {  # Nasi Ayam Pop
                'is_popular': False,
                'has_promo': False,
                'is_available': False,  # SOLD OUT
                'tags': 'nasi,ayam,pop,padang,sold out'
            },
        }
        
        count = self._apply_updates(updates)
        self.stdout.write(f'   ✓ Updated {count} Nasi Padang products')
    
    def _seed_mie_ayam(self):
        """Seed Mie Ayam Barokah products"""
        self.stdout.write('🍝 Seeding Mie Ayam Barokah...')
        
        updates = {
            'MA-001': {  # Mie Ayam Original
                'is_popular': True,
                'has_promo': False,
                'is_available': True,
                'tags': 'mie,ayam,bakso,populer'
            },
            'MA-002': {  # Mie Ayam Bakso
                'is_popular': True,
                'has_promo': True,
                'promo_price': Decimal('18000'),  # Original: 22000
                'is_available': True,
                'tags': 'mie,ayam,bakso,promo,populer'
            },
            'MA-003': {  # Mie Ayam Jumbo
                'is_popular': False,
                'has_promo': False,
                'is_available': True,
                'tags': 'mie,ayam,jumbo,besar'
            },
            'MA-004': {  # Mie Ayam Pangsit
                'is_popular': False,
                'has_promo': False,
                'is_available': True,
                'tags': 'mie,ayam,pangsit,wonton'
            },
        }
        
        count = self._apply_updates(updates)
        self.stdout.write(f'   ✓ Updated {count} Mie Ayam products')
    
    def _seed_minuman(self):
        """Seed Minuman & Dessert products"""
        self.stdout.write('🥤 Seeding Minuman & Dessert...')
        
        updates = {
            'BV-001': {  # Es Teh Manis
                'is_popular': True,
                'has_promo': False,
                'is_available': True,
                'tags': 'minuman,es,teh,manis,populer'
            },
            'BV-002': {  # Es Jeruk
                'is_popular': False,
                'has_promo': False,
                'is_available': True,
                'tags': 'minuman,es,jeruk,segar'
            },
            'BV-003': {  # Jus Alpukat
                'is_popular': False,
                'has_promo': True,
                'promo_price': Decimal('12000'),  # Original: 15000
                'is_available': True,
                'tags': 'minuman,jus,alpukat,sehat,promo'
            },
            'DS-001': {  # Es Campur
                'is_popular': True,
                'has_promo': False,
                'is_available': True,
                'tags': 'dessert,es campur,manis,segar,populer'
            },
        }
        
        count = self._apply_updates(updates)
        self.stdout.write(f'   ✓ Updated {count} Minuman products')
    
    def _apply_updates(self, updates):
        """Apply updates to products"""
        count = 0
        for sku, data in updates.items():
            try:
                product = Product.objects.get(sku=sku)
                for key, value in data.items():
                    setattr(product, key, value)
                product.save()
                count += 1
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'   ⚠️  Product {sku} not found, skipping...')
                )
        return count
    
    def _print_summary(self):
        """Print summary statistics"""
        total = Product.objects.count()
        popular = Product.objects.filter(is_popular=True).count()
        promo = Product.objects.filter(has_promo=True).count()
        available = Product.objects.filter(is_available=True).count()
        sold_out = Product.objects.filter(is_available=False).count()
        popular_promo = Product.objects.filter(is_popular=True, has_promo=True).count()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📊 Summary:'))
        self.stdout.write(f'   Total Products: {total}')
        self.stdout.write(f'   ⭐ Popular: {popular} products')
        self.stdout.write(f'   🔥 Promo: {promo} products')
        self.stdout.write(f'   ✓ Available: {available} products')
        self.stdout.write(f'   ❌ Sold Out: {sold_out} products')
        self.stdout.write(f'   🌟 Popular + Promo: {popular_promo} products')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Ready to test search features!'))
        self.stdout.write('   Open: http://localhost:5174/kiosk')
        self.stdout.write('   Try:')
        self.stdout.write('     - 🔍 Search for "nasi", "ayam", "pedas"')
        self.stdout.write('     - ⭐ Click [Populer] filter')
        self.stdout.write('     - 🔥 Click [Promo] filter')
        self.stdout.write('     - ✓ Toggle [Tersedia] filter')
