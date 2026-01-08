"""
Views for OrderGroup API (Multi-Outlet Orders)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal

from apps.orders.models import OrderGroup, Order, OrderItem
from apps.orders.serializers import (
    OrderGroupSerializer, 
    OrderGroupCreateSerializer,
    OrderSerializer
)
from apps.tenants.models import Outlet, Store
from apps.products.models import Product
from apps.core.permissions import IsManagerOrAbove


class PublicOrderGroupViewSet(viewsets.ModelViewSet):
    """
    Public ViewSet for OrderGroup (Kiosk Mode)
    
    create: Create multi-outlet order group
    retrieve: Get order group details
    mark_as_paid: Mark order group as paid
    """
    queryset = OrderGroup.objects.all()
    serializer_class = OrderGroupSerializer
    permission_classes = [AllowAny]  # Public access for kiosk
    lookup_field = 'group_number'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderGroupCreateSerializer
        return OrderGroupSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create order group with multiple outlet orders
        
        POST /api/public/order-groups/
        
        Request body:
        {
            "store_id": 1,
            "customer_name": "John Doe",
            "customer_phone": "081234567890",
            "source": "kiosk",
            "device_id": "KIOSK-001",
            "session_id": "sess-abc123",
            "carts": [
                {
                    "outlet_id": 1,
                    "items": [
                        {
                            "product_id": 10,
                            "quantity": 2,
                            "modifiers": [],
                            "notes": ""
                        }
                    ]
                },
                {
                    "outlet_id": 2,
                    "items": [...]
                }
            ]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Create OrderGroup
        order_group = OrderGroup.objects.create(
            store_id=data.get('store_id'),
            customer_name=data.get('customer_name', ''),
            customer_phone=data.get('customer_phone', ''),
            customer_email=data.get('customer_email', ''),
            source=data.get('source', 'kiosk'),
            device_id=data.get('device_id', ''),
            session_id=data.get('session_id', '')
        )
        
        # Create orders for each outlet
        created_orders = []
        
        for cart in data['carts']:
            outlet = get_object_or_404(Outlet, id=cart['outlet_id'], is_active=True)
            
            # Create Order
            order = Order.objects.create(
                tenant=outlet.tenant,
                outlet=outlet,
                order_group=order_group,
                customer_name=data.get('customer_name', ''),
                customer_phone=data.get('customer_phone', ''),
                source=data.get('source', 'kiosk'),
                device_id=data.get('device_id', ''),
                status='pending'
            )
            
            # Create Order Items
            for item_data in cart['items']:
                product = get_object_or_404(Product, id=item_data['product_id'])
                
                # Calculate modifiers price
                modifiers = item_data.get('modifiers', [])
                modifiers_price = Decimal('0.00')
                for mod in modifiers:
                    modifiers_price += Decimal(str(mod.get('price', 0)))
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    quantity=item_data['quantity'],
                    unit_price=product.price,
                    modifiers=modifiers,
                    modifiers_price=modifiers_price,
                    kitchen_station_code=product.kitchen_station_code,  # Snapshot
                    notes=item_data.get('notes', '')
                )
            
            # Calculate order totals
            order.calculate_totals()
            created_orders.append(order)
        
        # Calculate order group total
        order_group.calculate_total()
        
        # Return created order group with all orders
        response_serializer = OrderGroupSerializer(order_group)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_as_paid(self, request, group_number=None):
        """
        Mark order group as paid
        
        POST /api/public/order-groups/{group_number}/mark-paid/
        
        Body:
        {
            "payment_method": "cash" | "card" | "qris" | "ewallet"
        }
        """
        order_group = self.get_object()
        
        if order_group.payment_status == 'paid':
            return Response({
                'error': 'Order group already paid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = request.data.get('payment_method', 'cash')
        
        # Mark as paid
        order_group.mark_as_paid(payment_method=payment_method)
        
        serializer = self.get_serializer(order_group)
        return Response({
            'message': 'Payment successful',
            'order_group': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def receipt(self, request, group_number=None):
        """
        Get receipt data for order group
        
        GET /api/public/order-groups/{group_number}/receipt/
        """
        order_group = self.get_object()
        
        receipt_data = {
            'group_number': order_group.group_number,
            'location': {
                'name': order_group.location.name if order_group.location else 'N/A',
                'address': order_group.location.address if order_group.location else 'N/A',
            },
            'customer': {
                'name': order_group.customer_name,
                'phone': order_group.customer_phone,
            },
            'payment': {
                'method': order_group.payment_method,
                'status': order_group.payment_status,
                'total': float(order_group.total_amount),
                'paid': float(order_group.paid_amount),
            },
            'created_at': order_group.created_at,
            'paid_at': order_group.paid_at,
            'orders': []
        }
        
        # Add each order detail
        for order in order_group.orders.all().select_related('tenant', 'outlet').prefetch_related('items'):
            order_data = {
                'order_number': order.order_number,
                'tenant': order.tenant.name,
                'outlet': order.outlet.name,
                'subtotal': float(order.subtotal),
                'tax': float(order.tax_amount),
                'service_charge': float(order.service_charge_amount),
                'total': float(order.total_amount),
                'items': []
            }
            
            for item in order.items.all():
                order_data['items'].append({
                    'name': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'total': float(item.total_price),
                    'modifiers': item.modifiers,
                    'notes': item.notes
                })
            
            receipt_data['orders'].append(order_data)
        
        return Response(receipt_data)


class OrderGroupAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin ViewSet for OrderGroup Management
    
    Read-only access to order groups for admin
    """
    queryset = OrderGroup.objects.all().select_related('location').prefetch_related('orders')
    serializer_class = OrderGroupSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by store
        store_id = self.request.query_params.get('store_id')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
