from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.tenants.serializers import OutletSerializer, StoreSerializer
from apps.products.serializers import ProductSerializer


class KitchenOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items in kitchen display"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    modifiers_display = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_image',
            'quantity',
            'unit_price',
            'total_price',
            'notes',
            'modifiers',
            'modifiers_display',
        ]
    
    def get_product_image(self, obj):
        if obj.product and obj.product.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.product.image.url)
        return None
    
    def get_modifiers_display(self, obj):
        """Format modifiers for kitchen display"""
        if not obj.modifiers:
            return []
        
        modifiers_list = []
        for mod in obj.modifiers:
            modifiers_list.append({
                'name': mod.get('name', ''),
                'quantity': mod.get('quantity', 1),
            })
        return modifiers_list


class KitchenOrderSerializer(serializers.ModelSerializer):
    """Serializer for kitchen order display"""
    items = KitchenOrderItemSerializer(many=True, read_only=True)
    outlet_name = serializers.CharField(source='outlet.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    # Time tracking
    wait_time = serializers.SerializerMethodField()
    is_urgent = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'order_group_id',
            'status',
            'tenant',
            'tenant_name',
            'outlet',
            'outlet_name',
            'store',
            'store_name',
            'customer_name',
            'customer_phone',
            'table_number',
            'notes',
            'subtotal',
            'tax_amount',
            'service_charge_amount',
            'total_amount',
            'source',
            'device_id',
            'created_at',
            'updated_at',
            'completed_at',
            'items',
            'wait_time',
            'is_urgent',
        ]
    
    def get_wait_time(self, obj):
        """Calculate wait time in minutes"""
        from datetime import datetime
        from django.utils import timezone
        
        if obj.status in ['completed', 'served', 'cancelled']:
            if obj.completed_at:
                delta = obj.completed_at - obj.created_at
                return int(delta.total_seconds() / 60)
            return 0
        
        # For pending/preparing orders
        now = timezone.now()
        delta = now - obj.created_at
        return int(delta.total_seconds() / 60)
    
    def get_is_urgent(self, obj):
        """Mark order as urgent if wait time > 15 minutes"""
        wait_time = self.get_wait_time(obj)
        return wait_time > 15


class KitchenOrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    status = serializers.ChoiceField(choices=[
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    notes = serializers.CharField(required=False, allow_blank=True)


class KitchenStatsSerializer(serializers.Serializer):
    """Serializer for kitchen statistics"""
    pending_count = serializers.IntegerField()
    preparing_count = serializers.IntegerField()
    ready_count = serializers.IntegerField()
    completed_today = serializers.IntegerField()
    avg_prep_time = serializers.FloatField()
    total_orders_today = serializers.IntegerField()
