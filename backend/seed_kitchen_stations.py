"""
Seed initial kitchen stations for existing outlets
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Outlet, KitchenStation

def seed_kitchen_stations():
    """Create default kitchen stations for all outlets"""
    
    stations_created = 0
    
    for outlet in Outlet.objects.all():
        print(f"\n📍 Processing: {outlet.name}")
        
        # Check if outlet already has stations
        existing = KitchenStation.objects.filter(outlet=outlet).count()
        if existing > 0:
            print(f"   ⏭️  Skipped - already has {existing} stations")
            continue
        
        # Create default stations
        default_stations = [
            {
                'name': 'Main Kitchen',
                'code': 'MAIN',
                'description': 'Main kitchen for all items',
                'sort_order': 1
            },
            {
                'name': 'Beverage Station',
                'code': 'BEVERAGE',
                'description': 'Drinks and beverages',
                'sort_order': 2
            },
        ]
        
        for station_data in default_stations:
            station = KitchenStation.objects.create(
                outlet=outlet,
                **station_data
            )
            stations_created += 1
            print(f"   ✅ Created: {station.name} ({station.code})")
    
    print(f"\n✨ Total stations created: {stations_created}")

if __name__ == '__main__':
    print("🍳 Seeding Kitchen Stations...")
    seed_kitchen_stations()
    print("\n✅ Done!")
