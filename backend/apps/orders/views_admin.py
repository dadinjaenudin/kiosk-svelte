"""
Admin views for Order Management
"""
import logging
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import OrderSerializer, OrderItemSerializer
from apps.core.permissions import (
    IsAdminOrTenantOwnerOrManager,
    CanManageOrders,
    is_admin_user
)

logger = logging.getLogger(__name__)


class OrderFilter:
    """Custom order filters"""
    
    @staticmethod
    def filter_by_date_range(queryset, start_date=None, end_date=None):
        """Filter by date range"""
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            # Include end date by adding 23:59:59
            end_datetime = datetime.combine(end_date, datetime.max.time())
            queryset = queryset.filter(created_at__lte=end_datetime)
        return queryset
    
    @staticmethod
    def filter_by_status(queryset, status_list):
        """Filter by status list"""
        if status_list:
            return queryset.filter(status__in=status_list)
        return queryset
    
    @staticmethod
    def filter_by_payment_status(queryset, payment_status):
        """Filter by payment status"""
        if payment_status:
            return queryset.filter(payment_status=payment_status)
        return queryset
    
    @staticmethod
    def filter_by_search(queryset, search_term):
        """Search by order number, customer name, or phone"""
        if search_term:
            return queryset.filter(
                Q(order_number__icontains=search_term) |
                Q(customer_name__icontains=search_term) |
                Q(customer_phone__icontains=search_term) |
                Q(table_number__icontains=search_term)
            )
        return queryset


class OrderManagementViewSet(viewsets.ModelViewSet):
    """
    Order Management ViewSet for Admin Panel
    
    Features:
    - List orders with filters
    - Detail view
    - Update order status
    - Reprint receipt
    - Order statistics
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, CanManageOrders]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'outlet', 'tenant']
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'table_number']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get orders based on user role and outlet context:
        - Admin/Superuser: all orders
        - Tenant Owner: all orders in their tenant
        - Manager: orders from accessible outlets
        - Cashier/Kitchen: orders from their assigned outlet
        """
        from apps.core.context import get_current_tenant, get_current_outlet
        
        user = self.request.user
        queryset = Order.objects.select_related('tenant', 'outlet', 'cashier').prefetch_related('items')
        
        # Filter by user role
        if is_admin_user(user):
            # Admin sees all orders
            pass
        elif user.role == 'tenant_owner':
            # Tenant owner sees only their tenant's orders
            queryset = queryset.filter(tenant=user.tenant)
        elif user.role == 'manager':
            # Manager sees orders from accessible outlets
            if user.tenant:
                queryset = queryset.filter(tenant=user.tenant)
                # Further filter by accessible outlets
                current_outlet = get_current_outlet()
                if current_outlet:
                    queryset = queryset.filter(outlet=current_outlet)
                elif user.accessible_outlets.exists():
                    # If no current outlet, show all accessible outlets
                    queryset = queryset.filter(outlet__in=user.accessible_outlets.all())
            else:
                queryset = queryset.none()
        elif user.role in ['cashier', 'kitchen']:
            # Cashier/Kitchen see only their outlet's orders
            if user.outlet:
                queryset = queryset.filter(outlet=user.outlet)
            else:
                queryset = queryset.none()
        else:
            # Other roles see nothing
            queryset = queryset.none()
        
        # Apply custom filters from query params
        status_list = self.request.query_params.getlist('status')
        if status_list:
            queryset = OrderFilter.filter_by_status(queryset, status_list)
        
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = OrderFilter.filter_by_payment_status(queryset, payment_status)
        
        # Date range filter
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if start_date or end_date:
            queryset = OrderFilter.filter_by_date_range(queryset, start_date, end_date)
        
        # Search filter
        search = self.request.query_params.get('search')
        if search:
            queryset = OrderFilter.filter_by_search(queryset, search)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update order status
        
        Body: { "status": "preparing" }
        """
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Valid options: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status
        old_status = order.status
        order.status = new_status
        
        # If status is completed, set completed_at
        if new_status == 'completed' and not order.completed_at:
            order.completed_at = timezone.now()
        
        order.save()
        
        return Response({
            'message': 'Order status updated successfully',
            'order_number': order.order_number,
            'old_status': old_status,
            'new_status': new_status,
            'order': self.get_serializer(order).data
        })
    
    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """
        Get order timeline/history
        
        Returns status changes with timestamps
        """
        try:
            order = self.get_object()
            
            timeline = [
                {
                    'status': 'draft',
                    'label': 'Draft',
                    'timestamp': order.created_at.isoformat() if order.status != 'draft' else None,
                    'completed': True if order.status != 'draft' else False
                },
                {
                    'status': 'pending',
                    'label': 'Order Placed',
                    'timestamp': order.created_at.isoformat() if order.created_at else None,
                    'completed': True
                },
                {
                    'status': 'confirmed',
                    'label': 'Confirmed',
                    'timestamp': order.updated_at.isoformat() if order.status in ['confirmed', 'preparing', 'ready', 'served', 'completed'] and order.updated_at else None,
                    'completed': order.status in ['confirmed', 'preparing', 'ready', 'served', 'completed']
                },
                {
                    'status': 'preparing',
                    'label': 'Preparing',
                    'timestamp': order.updated_at.isoformat() if order.status in ['preparing', 'ready', 'served', 'completed'] and order.updated_at else None,
                    'completed': order.status in ['preparing', 'ready', 'served', 'completed']
                },
                {
                    'status': 'ready',
                    'label': 'Ready to Serve',
                    'timestamp': order.updated_at.isoformat() if order.status in ['ready', 'served', 'completed'] and order.updated_at else None,
                    'completed': order.status in ['ready', 'served', 'completed']
                },
                {
                    'status': 'served',
                    'label': 'Served',
                    'timestamp': order.updated_at.isoformat() if order.status in ['served', 'completed'] and order.updated_at else None,
                    'completed': order.status in ['served', 'completed']
                },
                {
                    'status': 'completed',
                    'label': 'Completed',
                    'timestamp': order.completed_at.isoformat() if order.status == 'completed' and order.completed_at else None,
                    'completed': order.status == 'completed'
                }
            ]
            
            # If cancelled, add cancelled status
            if order.status == 'cancelled':
                timeline.append({
                    'status': 'cancelled',
                    'label': 'Cancelled',
                    'timestamp': order.updated_at.isoformat() if order.updated_at else None,
                    'completed': True
                })
            
            return Response({
                'order_number': order.order_number,
                'current_status': order.status,
                'timeline': timeline
            })
        except Exception as e:
            logger.error(f"Error generating timeline for order {pk}: {str(e)}")
            return Response({
                'error': 'Failed to generate timeline',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        """
        Get receipt data for printing
        
        Returns formatted receipt data
        """
        order = self.get_object()
        
        receipt_data = {
            'order_number': order.order_number,
            'tenant': {
                'name': order.tenant.name,
                'address': order.tenant.address,
                'phone': order.tenant.phone,
                'logo_url': order.tenant.logo.url if order.tenant.logo else None
            },
            'outlet': {
                'name': order.outlet.name,
                'address': order.outlet.address,
                'phone': order.outlet.phone
            },
            'order_date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'customer': {
                'name': order.customer_name or 'Walk-in Customer',
                'phone': order.customer_phone or '-',
                'table': order.table_number or '-'
            },
            'items': [],
            'subtotal': float(order.subtotal),
            'tax_amount': float(order.tax_amount),
            'service_charge_amount': float(order.service_charge_amount),
            'discount_amount': float(order.discount_amount),
            'total_amount': float(order.total_amount),
            'payment_status': order.payment_status,
            'paid_amount': float(order.paid_amount),
            'cashier': order.cashier.username if order.cashier else 'System'
        }
        
        # Add items
        for item in order.items.all():
            item_data = {
                'name': item.product_name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'modifiers': item.modifiers,
                'modifiers_price': float(item.modifiers_price),
                'total_price': float(item.total_price),
                'notes': item.notes
            }
            receipt_data['items'].append(item_data)
        
        return Response(receipt_data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get order statistics
        
        Query params:
        - period: today, week, month, year (default: today)
        """
        period = request.query_params.get('period', 'today')
        
        # Determine date range
        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get queryset (respects user role filters)
        queryset = self.get_queryset().filter(created_at__gte=start_date)
        
        # Calculate statistics
        total_orders = queryset.count()
        total_revenue = queryset.filter(
            payment_status='paid'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Orders by status
        orders_by_status = queryset.values('status').annotate(count=Count('id'))
        status_breakdown = {item['status']: item['count'] for item in orders_by_status}
        
        # Payment status breakdown
        orders_by_payment = queryset.values('payment_status').annotate(count=Count('id'))
        payment_breakdown = {item['payment_status']: item['count'] for item in orders_by_payment}
        
        # Top selling items
        top_items = OrderItem.objects.filter(
            order__in=queryset
        ).values(
            'product_name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_quantity')[:10]
        
        return Response({
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': now.isoformat(),
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'orders_by_status': status_breakdown,
            'orders_by_payment_status': payment_breakdown,
            'top_selling_items': list(top_items),
            'average_order_value': float(total_revenue / total_orders) if total_orders > 0 else 0
        })
