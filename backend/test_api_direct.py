#!/usr/bin/env python
"""
Direct test of ViewSet from inside container
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

print("=" * 60)
print("DIRECT API TEST")
print("=" * 60)
print()

# Test 1: Check models
print("1. Testing Models...")
print("-" * 40)
from apps.products.models import Category, Product

try:
    total_cats = Category.all_objects.count()
    active_cats = Category.all_objects.filter(is_active=True).count()
    print(f"✓ Total categories: {total_cats}")
    print(f"✓ Active categories: {active_cats}")
    
    if active_cats > 0:
        print("  Sample categories:")
        for cat in Category.all_objects.filter(is_active=True)[:3]:
            print(f"    - {cat.id}: {cat.name} (tenant: {cat.tenant_id})")
except Exception as e:
    print(f"✗ Model test failed: {e}")

print()

# Test 2: Check serializers
print("2. Testing Serializers...")
print("-" * 40)
from apps.products.serializers import CategorySerializer

try:
    cats = Category.all_objects.filter(is_active=True)[:2]
    serializer = CategorySerializer(cats, many=True)
    data = serializer.data
    print(f"✓ Serializer works, got {len(data)} items")
    if len(data) > 0:
        print(f"  First item keys: {list(data[0].keys())}")
except Exception as e:
    print(f"✗ Serializer test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Check ViewSet queryset
print("3. Testing ViewSet Queryset...")
print("-" * 40)
from apps.products.views import CategoryViewSet

try:
    viewset = CategoryViewSet()
    queryset = viewset.get_queryset()
    count = queryset.count()
    print(f"✓ ViewSet queryset: {count} items")
    if count > 0:
        print("  First 3 items:")
        for cat in queryset[:3]:
            print(f"    - {cat.name}")
except Exception as e:
    print(f"✗ ViewSet test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Simulate API request
print("4. Simulating API Request...")
print("-" * 40)
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model

try:
    factory = APIRequestFactory()
    request = factory.get('/api/products/categories/')
    
    viewset = CategoryViewSet.as_view({'get': 'list'})
    response = viewset(request)
    
    print(f"✓ Response status: {response.status_code}")
    print(f"  Response type: {type(response)}")
    
    if hasattr(response, 'data'):
        print(f"  Response data type: {type(response.data)}")
        if isinstance(response.data, dict):
            print(f"  Response keys: {list(response.data.keys())}")
            if 'results' in response.data:
                print(f"  Results count: {len(response.data['results'])}")
        
        if response.status_code == 200:
            print("✓ SUCCESS: API returns 200")
        else:
            print(f"✗ FAILED: API returns {response.status_code}")
            print(f"  Data: {response.data}")
    else:
        print("  No data attribute")
        
except Exception as e:
    print(f"✗ API simulation failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
