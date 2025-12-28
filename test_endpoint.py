#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/user/webapp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver

# Get all URL patterns
resolver = get_resolver()

def show_urls(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # It's an included URLconf
            show_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            # It's a URL pattern
            print(f"{prefix}{pattern.pattern}")

print("=== Registered URLs ===")
show_urls(resolver.url_patterns)
