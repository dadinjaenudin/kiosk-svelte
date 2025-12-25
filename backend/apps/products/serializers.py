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
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'image', 
            'price', 'category', 'category_name',
            'is_available', 'is_featured', 
            'preparation_time', 'modifiers'
        ]


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'sort_order', 'is_active', 'product_count']
    
    def get_product_count(self, obj):
        return obj.products.filter(is_available=True).count()
