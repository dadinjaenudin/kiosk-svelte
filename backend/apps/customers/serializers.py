"""
Serializers for Customer API
"""
from rest_framework import serializers
from apps.customers.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer model
    """
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    preferred_outlet_name = serializers.CharField(source='preferred_outlet.name', read_only=True)
    
    # Computed fields
    total_orders = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    average_order_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'tenant', 'tenant_name',
            'name', 'email', 'phone',
            'gender', 'date_of_birth',
            'address', 'city', 'postal_code',
            'membership_number', 'membership_tier', 'points',
            'preferred_outlet', 'preferred_outlet_name',
            'notes', 'is_subscribed', 'is_active',
            'created_at', 'updated_at', 'last_order_at',
            'total_orders', 'total_spent', 'average_order_value'
        ]
        read_only_fields = ['id', 'tenant', 'membership_number', 'created_at', 'updated_at', 'last_order_at']
    
    def validate_phone(self, value):
        """Validate phone number"""
        if not value:
            raise serializers.ValidationError("Phone number is required")
        
        # Remove spaces and dashes
        phone = value.replace(' ', '').replace('-', '')
        
        # Check if phone is numeric (after removing + for international)
        if phone.startswith('+'):
            phone = phone[1:]
        
        if not phone.isdigit():
            raise serializers.ValidationError("Phone number must contain only numbers")
        
        return value
    
    def validate_email(self, value):
        """Validate email"""
        if value:
            # Check email format
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                raise serializers.ValidationError("Invalid email format")
        return value


class CustomerDetailSerializer(CustomerSerializer):
    """
    Detailed serializer for Customer with order history
    """
    recent_orders = serializers.SerializerMethodField()
    
    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + ['recent_orders']
    
    def get_recent_orders(self, obj):
        """Get recent 5 orders"""
        from apps.orders.models import Order
        recent = obj.orders.all()[:5]
        return [{
            'id': order.id,
            'order_number': order.order_number,
            'total_amount': str(order.total_amount),
            'status': order.status,
            'created_at': order.created_at.isoformat() if order.created_at else None
        } for order in recent]
