"""
Management command to check promo/popular data status
Usage: python manage.py check_promo_data
"""
from django.core.management.base import BaseCommand
from apps.products.models import Product
from django.db.models import Q


class Command(BaseCommand):
    help = 'Check status of promo and popular data in database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Checking database status...\n'))
        
        # Count totals
        total = Product.objects.count()
        popular = Product.objects.filter(is_popular=True).count()
        promo = Product.objects.filter(has_promo=True).count()
        available = Product.objects.filter(is_available=True).count()
        popular_promo = Product.objects.filter(is_popular=True, has_promo=True).count()
        
        # Summary
        self.stdout.write(self.style.SUCCESS('📊 Database Summary:'))
        self.stdout.write(f'   Total Products: {total}')
        self.stdout.write(f'   ⭐ Popular: {popular}')
        self.stdout.write(f'   🔥 Promo: {promo}')
        self.stdout.write(f'   ✓ Available: {available}')
        self.stdout.write(f'   🌟 Popular + Promo: {popular_promo}\n')
        
        # Check if data is seeded
        if total == 0:
            self.stdout.write(self.style.ERROR('❌ No products found in database!'))
            self.stdout.write('   Run: python manage.py loaddata sample_data.json')
            return
        
        if promo == 0:
            self.stdout.write(self.style.WARNING('⚠️  No promo products found!'))
            self.stdout.write('   Run: python manage.py seed_foodcourt')
            self.stdout.write('')
        else:
            # List promo products
            self.stdout.write(self.style.SUCCESS(f'🔥 Promo Products ({promo}):'))
            promo_products = Product.objects.filter(has_promo=True).values(
                'sku', 'name', 'price', 'promo_price', 'is_popular'
            )
            for p in promo_products:
                popular_icon = '⭐' if p['is_popular'] else '  '
                self.stdout.write(
                    f'   {popular_icon} {p["sku"]}: {p["name"]} '
                    f'(Rp {p["price"]:,.0f} → Rp {p["promo_price"]:,.0f})'
                )
            self.stdout.write('')
        
        if popular == 0:
            self.stdout.write(self.style.WARNING('⚠️  No popular products found!'))
            self.stdout.write('   Run: python manage.py seed_foodcourt')
            self.stdout.write('')
        else:
            # List popular products
            self.stdout.write(self.style.SUCCESS(f'⭐ Popular Products ({popular}):'))
            popular_products = Product.objects.filter(is_popular=True).values(
                'sku', 'name', 'has_promo'
            )
            for p in popular_products:
                promo_icon = '🔥' if p['has_promo'] else '  '
                self.stdout.write(f'   {promo_icon} {p["sku"]}: {p["name"]}')
            self.stdout.write('')
        
        # Check for missing SKUs
        expected_skus = [
            'AG-001', 'AG-002', 'AG-003', 'AG-004', 'AG-005', 'AG-006',
            'SH-001', 'SH-002', 'SH-003', 'SH-004',
            'NP-001', 'NP-002', 'NP-003', 'NP-004', 'NP-005',
            'MA-001', 'MA-002', 'MA-003', 'MA-004',
            'BV-001', 'BV-002', 'BV-003', 'DS-001'
        ]
        existing_skus = set(Product.objects.values_list('sku', flat=True))
        missing_skus = [sku for sku in expected_skus if sku not in existing_skus]
        
        if missing_skus:
            self.stdout.write(self.style.WARNING(f'⚠️  Missing SKUs ({len(missing_skus)}):'))
            for sku in missing_skus:
                self.stdout.write(f'   - {sku}')
            self.stdout.write('   These products need to be created first!')
            self.stdout.write('')
        
        # Final recommendation
        if promo > 0 and popular > 0:
            self.stdout.write(self.style.SUCCESS('✅ Database is properly seeded!'))
            self.stdout.write('   You can now test search filters.')
        else:
            self.stdout.write(self.style.WARNING('⚠️  Database needs seeding!'))
            self.stdout.write('   Run: python manage.py seed_foodcourt')
