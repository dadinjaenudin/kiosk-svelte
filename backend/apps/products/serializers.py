"""
Serializers for Product models
"""
from rest_framework import serializers
from .models import Category, Product, ProductModifier


class ProductModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModifier
        fields = ['id', 'product', 'name', 'type', 'price_adjustment', 'is_active', 'sort_order']


class ProductSerializer(serializers.ModelSerializer):
    modifiers = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    kitchen_station_code = serializers.ReadOnlyField()  # Property from model
    
    # Food court: Add tenant info for filtering
    tenant_id = serializers.IntegerField(source='tenant.id', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    tenant_slug = serializers.CharField(source='tenant.slug', read_only=True)
    tenant_color = serializers.CharField(source='tenant.primary_color', read_only=True)
    
    def get_modifiers(self, obj):
        """
        Return both product-specific modifiers AND global modifiers (product=null)
        """
        # Get product-specific modifiers
        product_modifiers = obj.modifiers.filter(is_active=True)
        
        # Get global modifiers (product=null)
        global_modifiers = ProductModifier.objects.filter(product__isnull=True, is_active=True)
        
        # Combine both querysets
        all_modifiers = list(product_modifiers) + list(global_modifiers)
        
        # Sort by sort_order
        all_modifiers.sort(key=lambda x: x.sort_order)
        
        # Serialize
        return ProductModifierSerializer(all_modifiers, many=True).data
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'image', 
            'price', 'category', 'category_name',
            'kitchen_station_code', 'kitchen_station_code_override',  # Kitchen routing
            'tenant_id', 'tenant_name', 'tenant_slug', 'tenant_color',  # Food court fields
            'is_available', 'is_featured', 
            'is_popular', 'has_promo', 'promo_price',  # Search filter fields
            'preparation_time', 'modifiers', 'tags'
        ]


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    # Food court: Add tenant info
    tenant_id = serializers.IntegerField(source='tenant.id', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'sort_order', 'is_active', 
            'kitchen_station_code',  # Kitchen routing
            'product_count', 'tenant_id', 'tenant_name'
        ]
    
    def get_product_count(self, obj):
        return obj.products.filter(is_available=True).count()
