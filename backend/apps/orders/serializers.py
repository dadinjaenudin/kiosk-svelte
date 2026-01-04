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
    
    # Kitchen Station Info
    kitchen_station_id = serializers.IntegerField(
        source='product.kitchen_station.id',
        read_only=True,
        allow_null=True
    )
    kitchen_station_name = serializers.CharField(
        source='product.kitchen_station.name',
        read_only=True,
        allow_null=True
    )
    kitchen_station_code = serializers.CharField(
        source='product.kitchen_station.code',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'quantity', 'unit_price', 'modifiers', 'modifiers_price',
            'total_price', 'notes',
            'kitchen_station_id', 'kitchen_station_name', 'kitchen_station_code'
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
            'payment_status', 'paid_amount', 'source', 'device_id',
            'items', 'created_at', 'updated_at', 'completed_at'
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
        """Validate that products exist and are available"""
        if not items:
            raise serializers.ValidationError("Cart is empty")
        
        product_ids = [item['product_id'] for item in items]
        unique_product_ids = set(product_ids)  # Get unique product IDs to handle duplicates
        
        # Get all products (including unavailable ones) to check existence
        all_products = Product.all_objects.filter(id__in=unique_product_ids)
        available_products = all_products.filter(is_available=True)
        
        # Check if all products exist
        if all_products.count() != len(unique_product_ids):
            missing_ids = unique_product_ids - set(all_products.values_list('id', flat=True))
            raise serializers.ValidationError(f"Products not found: {list(missing_ids)}")
        
        # Check if all products are available
        if available_products.count() != len(unique_product_ids):
            unavailable_ids = set(all_products.values_list('id', flat=True)) - set(available_products.values_list('id', flat=True))
            unavailable_products = all_products.filter(id__in=unavailable_ids)
            unavailable_names = [f"{p.name} (ID: {p.id})" for p in unavailable_products]
            raise serializers.ValidationError(f"Products not available: {', '.join(unavailable_names)}")
        
        return items
    
    def create_orders(self, validated_data, outlet, source='web', device_id=None):
        """
        Create multiple orders grouped by tenant
        Returns: list of (order, payment) tuples
        
        Args:
            validated_data: Validated checkout data
            outlet: Outlet instance
            source: Order source ('kiosk', 'web', 'cashier')
            device_id: Device identifier (optional)
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
            product_id = item_data['product_id']
            
            # Check if product exists
            if product_id not in products:
                raise serializers.ValidationError(f"Product with ID {product_id} not found")
            
            product = products[product_id]
            tenant_id = product.tenant_id
            
            # Check if product has tenant
            if not tenant_id:
                raise serializers.ValidationError(f"Product '{product.name}' (ID: {product_id}) does not have a tenant assigned")
            
            if tenant_id not in tenant_items:
                tenant_items[tenant_id] = []
            
            tenant_items[tenant_id].append({
                'product': product,
                'quantity': item_data['quantity'],
                'modifiers': item_data.get('modifiers', []),
                'notes': item_data.get('notes', '')
            })
        
        # Check if we have any items
        if not tenant_items:
            raise serializers.ValidationError("No valid items to checkout")
        
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
                payment_status='unpaid',
                source=source,
                device_id=device_id
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
