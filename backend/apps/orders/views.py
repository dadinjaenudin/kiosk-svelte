"""
Order views untuk API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.orders.serializers import (
    OrderSerializer, CheckoutSerializer,
    MultiTenantCheckoutResponseSerializer
)
from apps.tenants.models import Outlet


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for orders
    Read-only for now, orders created via checkout endpoint
    """
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]  # TODO: Add proper permissions
    
    def get_queryset(self):
        """
        Get orders
        Filter by tenant if provided in header
        """
        queryset = Order.objects.select_related('tenant', 'outlet').prefetch_related('items')
        
        # Filter by tenant if X-Tenant-ID header provided
        tenant_id = self.request.headers.get('X-Tenant-ID')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def checkout(self, request):
        """
        Multi-tenant checkout endpoint
        Split cart by tenant and create separate orders
        
        Request body:
        {
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "modifiers": [{"name": "Extra Cheese", "price": 5000}],
                    "notes": "No onions"
                }
            ],
            "payment_method": "cash",
            "customer_name": "John Doe",
            "customer_phone": "08123456789",
            "table_number": "A1",
            "notes": "Extra spicy"
        }
        
        Response:
        {
            "orders": [...],  # Array of orders (one per tenant)
            "payments": [...],  # Array of payments (one per tenant)
            "total_amount": 150000,
            "payment_method": "cash",
            "message": "Checkout successful. 3 orders created."
        }
        """
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get outlet (default to first outlet for now)
        # TODO: Get outlet from X-Outlet-ID header or request
        outlet = Outlet.objects.first()
        
        if not outlet:
            return Response(
                {'error': 'No outlet configured'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Create orders grouped by tenant
                orders_and_payments = serializer.create_orders(
                    serializer.validated_data,
                    outlet
                )
                
                orders = [op[0] for op in orders_and_payments]
                payments = [op[1] for op in orders_and_payments]
                
                # Calculate total
                total_amount = sum(order.total_amount for order in orders)
                
                # Process payment (for now, just mark as success for cash)
                payment_method = serializer.validated_data['payment_method']
                if payment_method == 'cash':
                    for payment in payments:
                        payment.status = 'success'
                        payment.save()
                    
                    for order in orders:
                        order.payment_status = 'paid'
                        order.status = 'confirmed'
                        order.save()
                
                # Serialize response
                response_data = {
                    'orders': OrderSerializer(orders, many=True).data,
                    'payments': [
                        {
                            'id': p.id,
                            'transaction_id': p.transaction_id,
                            'order_id': p.order_id,
                            'payment_method': p.payment_method,
                            'amount': str(p.amount),
                            'status': p.status
                        } for p in payments
                    ],
                    'total_amount': str(total_amount),
                    'payment_method': payment_method,
                    'message': f'Checkout successful. {len(orders)} order(s) created.'
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def kitchen_display(self, request):
        """
        Get orders for kitchen display
        Filter by tenant and show only preparing/ready orders
        """
        tenant_id = request.headers.get('X-Tenant-ID')
        
        if not tenant_id:
            return Response(
                {'error': 'X-Tenant-ID header required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orders = Order.objects.filter(
            tenant_id=tenant_id,
            status__in=['confirmed', 'preparing', 'ready']
        ).select_related('tenant', 'outlet').prefetch_related('items').order_by('created_at')
        
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def update_status(self, request, pk=None):
        """
        Update order status
        """
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
