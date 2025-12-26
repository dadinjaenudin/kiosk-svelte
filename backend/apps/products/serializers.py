"""
Serializers for Product models
"""
from rest_framework import serializers
from .models import Category, Product, ProductModifier


class ProductModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModifier
        fields = ['id', 'name', 'type', 'price_adjustment', 'is_active', 'sort_order']


class ProductSerializer(serializers.ModelSerializer):
    modifiers = ProductModifierSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    # Food court: Add tenant info for filtering
    tenant_id = serializers.IntegerField(source='tenant.id', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    tenant_slug = serializers.CharField(source='tenant.slug', read_only=True)
    tenant_color = serializers.CharField(source='tenant.primary_color', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'image', 
            'price', 'category', 'category_name',
            'tenant_id', 'tenant_name', 'tenant_slug', 'tenant_color',  # Food court fields
            'is_available', 'is_featured', 
            'preparation_time', 'modifiers'
        ]


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    # Food court: Add tenant info
    tenant_id = serializers.IntegerField(source='tenant.id', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'sort_order', 'is_active', 'product_count', 'tenant_id', 'tenant_name']
    
    def get_product_count(self, obj):
        return obj.products.filter(is_available=True).count()
