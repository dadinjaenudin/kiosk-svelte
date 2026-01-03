from rest_framework import serializers
from .models import Promotion, PromotionProduct, PromotionUsage
from apps.products.models import Product


class PromotionProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = PromotionProduct
        fields = [
            'id', 'product', 'product_name', 'product_price', 'product_image',
            'custom_discount_value', 'priority', 'created_at'
        ]
    
    def get_product_image(self, obj):
        if obj.product.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.product.image.url)
        return None


class ProductSimpleSerializer(serializers.ModelSerializer):
    """Simplified product serializer for product selector"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'tenant', 'tenant_name', 'image', 'is_available']


class PromotionSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    products = PromotionProductSerializer(source='promotion_products', many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Product._base_manager.all(),  # Use _base_manager to bypass tenant filtering
        required=False
    )
    
    # Computed fields
    is_valid_now = serializers.SerializerMethodField()
    days_until_start = serializers.SerializerMethodField()
    days_until_end = serializers.SerializerMethodField()
    
    class Meta:
        model = Promotion
        fields = [
            'id', 'name', 'description', 'code', 'tenant', 'tenant_name',
            'promo_type', 'discount_value', 'max_discount_amount',
            'min_purchase_amount', 'buy_quantity', 'get_quantity',
            'start_date', 'end_date',
            'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday',
            'time_start', 'time_end',
            'usage_limit', 'usage_limit_per_customer', 'usage_count',
            'status', 'is_active', 'is_featured',
            'created_at', 'updated_at', 'created_by', 'created_by_username',
            'products', 'product_ids', 'is_valid_now', 
            'days_until_start', 'days_until_end'
        ]
        read_only_fields = ['usage_count', 'created_at', 'updated_at', 'created_by']
    
    def get_is_valid_now(self, obj):
        return obj.is_valid_now()
    
    def get_days_until_start(self, obj):
        from django.utils import timezone
        if obj.start_date > timezone.now():
            delta = obj.start_date - timezone.now()
            return delta.days
        return 0
    
    def get_days_until_end(self, obj):
        from django.utils import timezone
        if obj.end_date > timezone.now():
            delta = obj.end_date - timezone.now()
            return delta.days
        return 0
    
    def create(self, validated_data):
        product_ids = validated_data.pop('product_ids', [])
        
        # Set created_by from request user
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        
        promotion = Promotion.objects.create(**validated_data)
        
        # Create PromotionProduct relationships
        for product in product_ids:
            PromotionProduct.objects.create(promotion=promotion, product=product)
        
        return promotion
    
    def update(self, instance, validated_data):
        product_ids = validated_data.pop('product_ids', None)
        
        # Update promotion fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update products if provided
        if product_ids is not None:
            # Clear existing products
            instance.promotion_products.all().delete()
            
            # Add new products
            for product in product_ids:
                PromotionProduct.objects.create(promotion=instance, product=product)
        
        return instance
    
    def validate(self, data):
        """Validate promotion data"""
        # Validate date range
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date'
                })
        
        # Validate time range
        if data.get('time_start') and data.get('time_end'):
            if data['time_start'] >= data['time_end']:
                raise serializers.ValidationError({
                    'time_end': 'End time must be after start time'
                })
        
        # Validate Buy X Get Y fields
        if data.get('promo_type') == Promotion.TYPE_BUY_X_GET_Y:
            if not data.get('buy_quantity') or not data.get('get_quantity'):
                raise serializers.ValidationError({
                    'buy_quantity': 'Buy quantity and Get quantity are required for Buy X Get Y promos'
                })
        
        # Validate percentage discount
        if data.get('promo_type') == Promotion.TYPE_PERCENTAGE:
            if data.get('discount_value', 0) > 100:
                raise serializers.ValidationError({
                    'discount_value': 'Percentage discount cannot exceed 100%'
                })
        
        return data


class PromotionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    product_count = serializers.SerializerMethodField()
    is_valid_now = serializers.SerializerMethodField()
    
    class Meta:
        model = Promotion
        fields = [
            'id', 'name', 'tenant', 'tenant_name', 'promo_type',
            'discount_value', 'status', 'is_active', 'is_featured',
            'start_date', 'end_date', 'usage_count', 'usage_limit',
            'product_count', 'is_valid_now', 'created_at'
        ]
    
    def get_product_count(self, obj):
        return obj.promotion_products.count()
    
    def get_is_valid_now(self, obj):
        return obj.is_valid_now()


class PromotionUsageSerializer(serializers.ModelSerializer):
    promotion_name = serializers.CharField(source='promotion.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = PromotionUsage
        fields = [
            'id', 'promotion', 'promotion_name', 'order', 'order_number',
            'customer_identifier', 'discount_amount', 'created_at'
        ]
        read_only_fields = ['created_at']
