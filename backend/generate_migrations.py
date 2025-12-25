#!/usr/bin/env python
"""
Script to generate initial migrations for all apps
Run this inside the Django container
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

from django.core.management import call_command

# Apps in dependency order
apps = [
    'tenants',
    'users',
    'products',
    'orders',
    'payments',
    'kitchen',
]

print("Generating migrations for all apps...")
for app in apps:
    print(f"\n📦 Generating migration for {app}...")
    try:
        call_command('makemigrations', app, interactive=False)
        print(f"✅ {app} migration generated")
    except Exception as e:
        print(f"❌ {app} migration failed: {e}")

print("\n✅ All migrations generated!")
print("\nRun 'python manage.py migrate' to apply migrations")
