"""
Management command to seed customer data
Usage: python manage.py seed_customer
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from apps.customers.models import Customer
from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = 'Seed customer data with 20 sample customers'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding customer data...\n')

        # Get all tenants
        tenants = list(Tenant.objects.all())

        if not tenants:
            self.stdout.write(self.style.ERROR('❌ No tenants found. Please create tenants first.'))
            return

        # Clear existing customers
        Customer.objects.all().delete()
        self.stdout.write('🗑️  Cleared existing customers\n')

        # Sample customer data
        first_names = [
            'Budi', 'Siti', 'Andi', 'Dewi', 'Agus', 'Rina', 'Joko', 'Sri',
            'Hendra', 'Linda', 'Wahyu', 'Ani', 'Bambang', 'Fitri', 'Rudi',
            'Maya', 'Dedi', 'Yuni', 'Eko', 'Dian'
        ]
        
        last_names = [
            'Santoso', 'Wijaya', 'Pratama', 'Kusuma', 'Saputra', 'Lestari',
            'Nugroho', 'Wati', 'Setiawan', 'Permata', 'Putra', 'Sari',
            'Gunawan', 'Indah', 'Hidayat', 'Anggraini', 'Hermawan', 'Puspita',
            'Kurniawan', 'Maharani'
        ]

        cities = [
            'Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Semarang',
            'Medan', 'Makassar', 'Palembang', 'Tangerang', 'Depok'
        ]

        membership_tiers = ['bronze', 'silver', 'gold', 'platinum']
        genders = ['male', 'female']

        created_count = 0
        now = timezone.now()

        for i in range(20):
            # Generate customer data
            first_name = first_names[i]
            last_name = last_names[i]
            full_name = f"{first_name} {last_name}"
            
            # Generate email and phone
            email = f"{first_name.lower()}.{last_name.lower()}@email.com"
            phone = f"08{random.randint(1000000000, 9999999999)}"
            
            # Random membership tier (weighted towards lower tiers)
            tier_weights = [50, 30, 15, 5]  # Bronze most common, Platinum rare
            membership_tier = random.choices(membership_tiers, weights=tier_weights)[0]
            
            # Points based on tier
            if membership_tier == 'bronze':
                points = random.randint(0, 500)
            elif membership_tier == 'silver':
                points = random.randint(500, 2000)
            elif membership_tier == 'gold':
                points = random.randint(2000, 5000)
            else:  # platinum
                points = random.randint(5000, 15000)
            
            # Random gender
            gender = random.choice(genders)
            
            # Random date of birth (18-60 years old)
            age_days = random.randint(18*365, 60*365)
            date_of_birth = now.date() - timedelta(days=age_days)
            
            # Random city
            city = random.choice(cities)
            
            # Random tenant
            tenant = random.choice(tenants)
            
            # Random active status (90% active)
            is_active = random.random() < 0.9
            
            # Random subscribed status (60% subscribed)
            is_subscribed = random.random() < 0.6
            
            # Random join date (within last 2 years)
            days_ago = random.randint(1, 730)
            join_date = now - timedelta(days=days_ago)
            
            # Create customer
            customer = Customer.objects.create(
                tenant=tenant,
                name=full_name,
                email=email,
                phone=phone,
                gender='M' if gender == 'male' else 'F',
                date_of_birth=date_of_birth,
                address=f"Jl. {last_name} No. {random.randint(1, 999)}",
                city=city,
                postal_code=f"{random.randint(10000, 99999)}",
                membership_tier=membership_tier,
                points=points,
                is_active=is_active,
                is_subscribed=is_subscribed,
                notes=f"Customer sejak {join_date.strftime('%B %Y')}"
            )
            
            # Override created_at to simulate different join dates
            Customer.objects.filter(pk=customer.pk).update(created_at=join_date)
            
            created_count += 1
            
            # Display info
            tier_colors = {
                'bronze': self.style.WARNING,
                'silver': self.style.NOTICE,
                'gold': self.style.SUCCESS,
                'platinum': self.style.HTTP_INFO,
            }
            color = tier_colors.get(membership_tier, self.style.SUCCESS)
            
            status = '✓' if is_active else '✗'
            status_color = self.style.SUCCESS if is_active else self.style.ERROR
            
            tier_display = membership_tier.upper().ljust(8)
            
            self.stdout.write(
                f"  {status_color(status)} {full_name:<20} "
                f"{color(tier_display)} "
                f"Points: {points:>6,} | "
                f"City: {city:<12} | "
                f"Gender: {gender}"
            )

        self.stdout.write(f'\n{self.style.SUCCESS("✅ Successfully created " + str(created_count) + " customers!")}')
        
        # Display summary
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'  Active: {Customer.objects.filter(is_active=True).count()}')
        self.stdout.write(f'  Inactive: {Customer.objects.filter(is_active=False).count()}')
        self.stdout.write(f'  Subscribed: {Customer.objects.filter(is_subscribed=True).count()}')
        self.stdout.write('\n  By Tier:')
        for tier in membership_tiers:
            count = Customer.objects.filter(membership_tier=tier).count()
            self.stdout.write(f'    {tier.capitalize()}: {count}')
        self.stdout.write('\n  By Gender:')
        self.stdout.write(f'    Male: {Customer.objects.filter(gender="M").count()}')
        self.stdout.write(f'    Female: {Customer.objects.filter(gender="F").count()}')
