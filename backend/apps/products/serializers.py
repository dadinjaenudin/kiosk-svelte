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
    image = serializers.SerializerMethodField()  # Return full URL for image
    
    # Food court: Add tenant info for filtering
    tenant_id = serializers.IntegerField(source='tenant.id', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    tenant_slug = serializers.CharField(source='tenant.slug', read_only=True)
    tenant_color = serializers.CharField(source='tenant.primary_color', read_only=True)
    
    def get_image(self, obj):
        """Return full URL for product image"""
        import logging
        logger = logging.getLogger(__name__)
        
        if obj.image:
            request = self.context.get('request')
            logger.info(f"🖼️ Product {obj.name} - image field: {obj.image}")
            
            if request:
                # Get the full URL
                full_url = request.build_absolute_uri(obj.image.url)
                
                # Replace host.docker.internal with localhost for browser access
                # This is needed because host.docker.internal only works inside Docker
                full_url = full_url.replace('host.docker.internal', 'localhost')
                
                logger.info(f"🖼️ Full URL (fixed): {full_url}")
                return full_url
            
            logger.warning(f"⚠️ No request context, returning relative URL: {obj.image.url}")
            return obj.image.url
        return None
    
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
    image = serializers.SerializerMethodField()  # Return full URL for image
    
    # Food court: Add tenant info
    tenant_id = serializers.IntegerField(source='tenant.id', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    def get_image(self, obj):
        """Return full URL for category image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                full_url = request.build_absolute_uri(obj.image.url)
                # Replace host.docker.internal with localhost for browser access
                full_url = full_url.replace('host.docker.internal', 'localhost')
                return full_url
            return obj.image.url
        return None
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'sort_order', 'is_active', 
            'kitchen_station_code',  # Kitchen routing
            'product_count', 'tenant_id', 'tenant_name'
        ]
    
    def get_product_count(self, obj):
        return obj.products.filter(is_available=True).count()
