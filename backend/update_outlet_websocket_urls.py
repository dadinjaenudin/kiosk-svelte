"""
Update outlet websocket_url from ws:// to http:// for Socket.IO compatibility
Run this script to fix existing outlet records in the database
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Outlet

def update_outlet_websocket_urls():
    """Update all outlet websocket URLs from ws:// to http://"""
    
    print("=" * 60)
    print("UPDATE OUTLET WEBSOCKET URLs")
    print("=" * 60)
    print()
    
    # Get all outlets
    outlets = Outlet.objects.all()
    total = outlets.count()
    updated = 0
    skipped = 0
    
    print(f"Found {total} outlets in database")
    print()
    
    for outlet in outlets:
        old_url = outlet.websocket_url
        
        if not old_url:
            print(f"⚠️  Outlet #{outlet.id} ({outlet.name}): No WebSocket URL set")
            skipped += 1
            continue
        
        # Convert ws:// to http:// and wss:// to https://
        if old_url.startswith('ws://'):
            new_url = old_url.replace('ws://', 'http://')
            outlet.websocket_url = new_url
            outlet.save()
            print(f"✅ Outlet #{outlet.id} ({outlet.name}):")
            print(f"   OLD: {old_url}")
            print(f"   NEW: {new_url}")
            updated += 1
        elif old_url.startswith('wss://'):
            new_url = old_url.replace('wss://', 'https://')
            outlet.websocket_url = new_url
            outlet.save()
            print(f"✅ Outlet #{outlet.id} ({outlet.name}):")
            print(f"   OLD: {old_url}")
            print(f"   NEW: {new_url}")
            updated += 1
        elif old_url.startswith('http://') or old_url.startswith('https://'):
            print(f"⏭️  Outlet #{outlet.id} ({outlet.name}): Already using HTTP/HTTPS")
            print(f"   URL: {old_url}")
            skipped += 1
        else:
            print(f"⚠️  Outlet #{outlet.id} ({outlet.name}): Unknown URL format")
            print(f"   URL: {old_url}")
            skipped += 1
        
        print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total outlets: {total}")
    print(f"Updated:       {updated}")
    print(f"Skipped:       {skipped}")
    print()
    
    if updated > 0:
        print("✅ Database updated successfully!")
        print("   Outlets now use http:// URLs for Socket.IO")
    else:
        print("ℹ️  No updates needed")

if __name__ == '__main__':
    try:
        update_outlet_websocket_urls()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
