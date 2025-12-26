"""
Order serializers untuk API
"""
from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.products.models import Product
from apps.tenants.models import Tenant, Outlet
from decimal import Decimal


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'quantity', 'unit_price', 'modifiers', 'modifiers_price',
            'total_price', 'notes'
        ]
        read_only_fields = ['total_price']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    tenant_color = serializers.CharField(source='tenant.primary_color', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'tenant', 'tenant_name', 'tenant_color',
            'outlet', 'status', 'customer_name', 'customer_phone',
            'table_number', 'notes', 'subtotal', 'tax_amount',
            'service_charge_amount', 'discount_amount', 'total_amount',
            'payment_status', 'paid_amount', 'items', 'created_at',
            'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'order_number', 'subtotal', 'tax_amount', 
            'service_charge_amount', 'total_amount', 'paid_amount'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'order', 'payment_method',
            'payment_provider', 'amount', 'status', 'qr_code_url',
            'payment_url', 'notes', 'created_at', 'paid_at'
        ]
        read_only_fields = ['transaction_id', 'status', 'qr_code_url', 'payment_url']


class CheckoutItemSerializer(serializers.Serializer):
    """Serializer for checkout items"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    modifiers = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer for multi-tenant checkout
    Split cart items by tenant and create separate orders
    """
    items = CheckoutItemSerializer(many=True)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHODS)
    customer_name = serializers.CharField(required=False, allow_blank=True)
    customer_phone = serializers.CharField(required=False, allow_blank=True)
    table_number = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_items(self, items):
        """Validate that products exist"""
        if not items:
            raise serializers.ValidationError("Cart is empty")
        
        product_ids = [item['product_id'] for item in items]
        products = Product.all_objects.filter(id__in=product_ids, is_available=True)
        
        if products.count() != len(product_ids):
            raise serializers.ValidationError("Some products are not available")
        
        return items
    
    def create_orders(self, validated_data, outlet):
        """
        Create multiple orders grouped by tenant
        Returns: list of (order, payment) tuples
        """
        items_data = validated_data['items']
        payment_method = validated_data['payment_method']
        customer_name = validated_data.get('customer_name', '')
        customer_phone = validated_data.get('customer_phone', '')
        table_number = validated_data.get('table_number', '')
        notes = validated_data.get('notes', '')
        
        # Group items by tenant
        tenant_items = {}
        product_ids = [item['product_id'] for item in items_data]
        products = {p.id: p for p in Product.all_objects.filter(id__in=product_ids)}
        
        for item_data in items_data:
            product = products[item_data['product_id']]
            tenant_id = product.tenant_id
            
            if tenant_id not in tenant_items:
                tenant_items[tenant_id] = []
            
            tenant_items[tenant_id].append({
                'product': product,
                'quantity': item_data['quantity'],
                'modifiers': item_data.get('modifiers', []),
                'notes': item_data.get('notes', '')
            })
        
        # Create orders per tenant
        orders_and_payments = []
        
        for tenant_id, items in tenant_items.items():
            tenant = Tenant.objects.get(id=tenant_id)
            
            # Create order
            order = Order.objects.create(
                tenant=tenant,
                outlet=outlet,
                customer_name=customer_name,
                customer_phone=customer_phone,
                table_number=table_number,
                notes=notes,
                status='pending',
                payment_status='unpaid'
            )
            
            # Create order items
            for item in items:
                product = item['product']
                modifiers = item.get('modifiers', [])
                modifiers_price = sum(Decimal(str(m.get('price', 0))) for m in modifiers)
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    quantity=item['quantity'],
                    unit_price=product.price,
                    modifiers=modifiers,
                    modifiers_price=modifiers_price,
                    notes=item.get('notes', '')
                )
            
            # Calculate totals
            order.calculate_totals()
            
            # Create payment
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total_amount,
                status='pending'
            )
            
            orders_and_payments.append((order, payment))
        
        return orders_and_payments


class MultiTenantCheckoutResponseSerializer(serializers.Serializer):
    """Response serializer for multi-tenant checkout"""
    orders = OrderSerializer(many=True)
    payments = PaymentSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.CharField()
    message = serializers.CharField()
