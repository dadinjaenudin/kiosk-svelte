#!/usr/bin/env python
"""
Assign placeholder images to products that don't have images
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Product

# Product name to image mapping (simple matching)
image_mapping = {
    'mi ayam': 'products/mi-ayam.jpg',
    'mie ayam': 'products/mi-ayam.jpg',
    'sate kambing': 'products/state_kambing.jpg',
    'satay': 'products/state_kambing.jpg',
}

# Default placeholder for products without specific images
default_image = 'products/mi-ayam.jpg'

def assign_images():
    # Get all products
    products = Product.objects.all()
    
    updated_count = 0
    for product in products:
        # Skip if product already has an image
        if product.image and product.image.name:
            continue
            
        # Try to find a matching image
        product_name_lower = product.name.lower()
        image_path = None
        
        for keyword, img in image_mapping.items():
            if keyword in product_name_lower:
                image_path = img
                break
        
        # If no match, use default
        if not image_path:
            image_path = default_image
        
        product.image = image_path
        product.save()
        updated_count += 1
        print(f"✅ Updated {product.name} -> {image_path}")
    
    print(f"\n🎉 Updated {updated_count} products with images")

if __name__ == '__main__':
    print("🔄 Assigning images to products...")
    assign_images()
    print("✅ Done!")
