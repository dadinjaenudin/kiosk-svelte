"""
Management command to seed promotion data
Usage: python manage.py seed_promotion
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from apps.promotions.models import Promotion, PromotionProduct
from apps.products.models import Product
from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = 'Seed promotion data with 15 sample promotions'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding promotion data...\n')

        # Get all products and tenants (use all_objects to bypass tenant filtering)
        products = list(Product.all_objects.all())
        tenants = list(Tenant.objects.all())

        if not products:
            self.stdout.write(self.style.ERROR('❌ No products found. Please create products first.'))
            return

        if not tenants:
            self.stdout.write(self.style.ERROR('❌ No tenants found. Please create tenants first.'))
            return

        # Clear existing promotions
        Promotion.objects.all().delete()
        self.stdout.write('🗑️  Cleared existing promotions\n')

        # Promotion templates
        promotions_data = [
            {
                'name': 'Buy 1 Get 1 Free Burger',
                'description': 'Beli 1 burger gratis 1 burger pilihan, berlaku untuk semua varian burger',
                'promo_type': 'buy_x_get_y',
                'discount_value': Decimal('0.00'),
                'buy_quantity': 1,
                'get_quantity': 1,
                'status': 'active',
                'is_active': True,
                'days_offset_start': -7,
                'days_offset_end': 14,
                'is_featured': True,
            },
            {
                'name': 'Diskon 20% Semua Menu',
                'description': 'Nikmati diskon 20% untuk semua menu pilihan',
                'promo_type': 'percentage',
                'discount_value': Decimal('20.00'),
                'status': 'active',
                'is_active': True,
                'days_offset_start': -3,
                'days_offset_end': 30,
                'is_featured': True,
            },
            {
                'name': 'Cashback Rp 10.000',
                'description': 'Dapatkan cashback Rp 10.000 untuk pembelian minimal Rp 50.000',
                'promo_type': 'fixed',
                'discount_value': Decimal('10000.00'),
                'min_purchase_amount': Decimal('50000.00'),
                'status': 'active',
                'is_active': True,
                'days_offset_start': -1,
                'days_offset_end': 20,
                'is_featured': False,
            },
            {
                'name': 'Combo Hemat Ayam Goreng',
                'description': 'Paket hemat ayam goreng + nasi + minum hanya Rp 25.000',
                'promo_type': 'bundle',
                'discount_value': Decimal('15000.00'),
                'status': 'active',
                'is_active': True,
                'days_offset_start': -5,
                'days_offset_end': 25,
                'is_featured': True,
            },
            {
                'name': 'Flash Sale Siang',
                'description': 'Diskon 50% khusus jam 11:00 - 14:00',
                'promo_type': 'percentage',
                'discount_value': Decimal('50.00'),
                'status': 'active',
                'is_active': True,
                'days_offset_start': 0,
                'days_offset_end': 7,
                'is_featured': True,
            },
            {
                'name': 'Promo Akhir Bulan',
                'description': 'Diskon hingga Rp 20.000 untuk pembelian minimal Rp 100.000',
                'promo_type': 'fixed',
                'discount_value': Decimal('20000.00'),
                'min_purchase_amount': Decimal('100000.00'),
                'status': 'scheduled',
                'is_active': False,
                'days_offset_start': 5,
                'days_offset_end': 35,
                'is_featured': False,
            },
            {
                'name': 'Buy 2 Get 1 Free Minuman',
                'description': 'Beli 2 minuman gratis 1 minuman pilihan',
                'promo_type': 'buy_x_get_y',
                'discount_value': Decimal('0.00'),
                'buy_quantity': 2,
                'get_quantity': 1,
                'status': 'active',
                'is_active': True,
                'days_offset_start': -10,
                'days_offset_end': 10,
                'is_featured': False,
            },
            {
                'name': 'Weekend Special 30% Off',
                'description': 'Diskon spesial 30% setiap akhir pekan',
                'promo_type': 'percentage',
                'discount_value': Decimal('30.00'),
                'status': 'active',
                'is_active': True,
                'days_offset_start': -2,
                'days_offset_end': 60,
                'is_featured': True,
            },
            {
                'name': 'Paket Keluarga Hemat',
                'description': 'Paket untuk 4 orang dengan harga spesial',
                'promo_type': 'bundle',
                'discount_value': Decimal('30000.00'),
                'min_purchase_amount': Decimal('80000.00'),
                'status': 'active',
                'is_active': True,
                'days_offset_start': -15,
                'days_offset_end': 15,
                'is_featured': True,
            },
            {
                'name': 'Diskon 15% Menu Pilihan',
                'description': 'Diskon 15% untuk menu-menu tertentu',
                'promo_type': 'percentage',
                'discount_value': Decimal('15.00'),
                'status': 'active',
                'is_active': True,
                'days_offset_start': -4,
                'days_offset_end': 11,
                'is_featured': False,
            },
            {
                'name': 'Promo Tahun Baru',
                'description': 'Spesial tahun baru diskon hingga 40%',
                'promo_type': 'percentage',
                'discount_value': Decimal('40.00'),
                'status': 'expired',
                'is_active': False,
                'days_offset_start': -60,
                'days_offset_end': -30,
                'is_featured': False,
            },
            {
                'name': 'Cashback Member 15%',
                'description': 'Cashback khusus member hingga 15%',
                'promo_type': 'percentage',
                'discount_value': Decimal('15.00'),
                'max_discount_amount': Decimal('25000.00'),
                'status': 'active',
                'is_active': True,
                'days_offset_start': -20,
                'days_offset_end': 40,
                'is_featured': True,
            },
            {
                'name': 'Promo Valentine',
                'description': 'Spesial Valentine diskon untuk couple',
                'promo_type': 'percentage',
                'discount_value': Decimal('25.00'),
                'status': 'scheduled',
                'is_active': False,
                'days_offset_start': 30,
                'days_offset_end': 45,
                'is_featured': True,
            },
            {
                'name': 'Gratis Ongkir',
                'description': 'Gratis ongkir untuk pembelian minimal Rp 30.000',
                'promo_type': 'fixed',
                'discount_value': Decimal('10000.00'),
                'min_purchase_amount': Decimal('30000.00'),
                'status': 'active',
                'is_active': True,
                'days_offset_start': -8,
                'days_offset_end': 22,
                'is_featured': False,
            },
            {
                'name': 'Diskon Malam Hari',
                'description': 'Diskon 35% khusus jam 19:00 - 22:00',
                'promo_type': 'percentage',
                'discount_value': Decimal('35.00'),
                'status': 'paused',
                'is_active': False,
                'days_offset_start': -5,
                'days_offset_end': 25,
                'is_featured': False,
            },
        ]

        created_count = 0
        now = timezone.now()

        for promo_data in promotions_data:
            # Calculate dates
            start_date = now + timedelta(days=promo_data.pop('days_offset_start'))
            end_date = now + timedelta(days=promo_data.pop('days_offset_end'))

            # Select random products (1-3 products per promo)
            selected_products = random.sample(products, min(random.randint(1, 3), len(products)))
            
            # Select random tenant
            tenant = random.choice(tenants)

            # Create promotion
            promotion = Promotion.objects.create(
                tenant=tenant,
                start_date=start_date,
                end_date=end_date,
                **promo_data
            )

            # Add products to promotion via PromotionProduct
            for product in selected_products:
                PromotionProduct.objects.create(
                    promotion=promotion,
                    product=product
                )

            created_count += 1
            
            # Display info
            status_color = {
                'active': self.style.SUCCESS,
                'scheduled': self.style.WARNING,
                'expired': self.style.ERROR,
                'paused': self.style.NOTICE,
            }
            color = status_color.get(promotion.status, self.style.SUCCESS)
            
            self.stdout.write(
                f"  {color('✓')} {promotion.name} "
                f"[{color(promotion.status.upper())}] "
                f"- {promotion.promo_type} - {len(selected_products)} products"
            )

        self.stdout.write(f'\n{self.style.SUCCESS("✅ Successfully created " + str(created_count) + " promotions!")}')
        
        # Display summary
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'  Active: {Promotion.objects.filter(status="active").count()}')
        self.stdout.write(f'  Scheduled: {Promotion.objects.filter(status="scheduled").count()}')
        self.stdout.write(f'  Expired: {Promotion.objects.filter(status="expired").count()}')
        self.stdout.write(f'  Paused: {Promotion.objects.filter(status="paused").count()}')
        self.stdout.write(f'  Featured: {Promotion.objects.filter(is_featured=True).count()}')
