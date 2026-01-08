"""
Order views untuk API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
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
        Admin can see all orders
        """
        queryset = Order.objects.select_related('tenant', 'outlet').prefetch_related('items')
        
        # Admin/superuser can see all orders
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or getattr(user, 'role', None) in ['admin', 'super_admin']):
            # Don't filter by tenant for admin
            pass
        else:
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
        # Debug: Log incoming request data
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"📥 Checkout request data: {request.data}")
        logger.info(f"📦 Items: {request.data.get('items', [])}")
        
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get outlet from X-Outlet-ID header or query param
        outlet_id = request.headers.get('X-Outlet-ID') or request.query_params.get('outlet_id')
        
        if outlet_id:
            try:
                outlet = Outlet.objects.get(id=outlet_id, is_active=True)
            except Outlet.DoesNotExist:
                return Response(
                    {'error': f'Outlet with ID {outlet_id} not found or inactive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Fallback to first outlet if no outlet specified
            outlet = Outlet.objects.filter(is_active=True).first()
        
        if not outlet:
            return Response(
                {'error': 'No outlet configured'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Get source from header or body
                source = request.headers.get('X-Source') or request.data.get('source', 'web')
                device_id = request.headers.get('X-Device-ID') or request.data.get('device_id')
                
                # Validate source
                valid_sources = ['kiosk', 'web', 'cashier']
                if source not in valid_sources:
                    source = 'web'
                
                # Create orders grouped by tenant
                orders_and_payments = serializer.create_orders(
                    serializer.validated_data,
                    outlet,
                    source=source,
                    device_id=device_id
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
                        # Keep status as 'pending' for kitchen to process
                        # order.status = 'confirmed'  # OLD: Changed to confirmed
                        order.status = 'pending'  # NEW: Keep pending for kitchen display
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
            status__in=['pending', 'preparing', 'ready']  # Updated: changed from 'confirmed' to 'pending'
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
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def dashboard_analytics(self, request):
        """
        Dashboard analytics endpoint
        Returns sales metrics, revenue charts, top products, and recent orders
        
        Query params:
        - period: today/week/month/custom (default: today)
        - start_date: for custom period (YYYY-MM-DD)
        - end_date: for custom period (YYYY-MM-DD)
        - tenant_id: filter by specific tenant (optional, defaults to all)
        """
        # Get filter parameters
        period = request.query_params.get('period', 'today')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        tenant_id = request.query_params.get('tenant_id') or request.headers.get('X-Tenant-ID')
        
        # Calculate date range
        now = timezone.now()
        
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'week':
            start_date = now - timedelta(days=7)
            end_date = now
        elif period == 'month':
            start_date = now - timedelta(days=30)
            end_date = now
        elif period == 'custom' and start_date_str and end_date_str:
            try:
                start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
                end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        
        # Base queryset
        orders_queryset = Order.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        # Filter by tenant if provided
        if tenant_id:
            orders_queryset = orders_queryset.filter(tenant_id=tenant_id)
        
        # Sales Metrics
        total_revenue = orders_queryset.filter(
            payment_status='paid'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        
        total_orders = orders_queryset.count()
        
        pending_orders = orders_queryset.filter(
            status__in=['pending', 'preparing']  # Updated: removed 'confirmed'
        ).count()
        
        completed_orders = orders_queryset.filter(
            status__in=['completed', 'served']
        ).count()
        
        # Calculate previous period for trends
        period_duration = end_date - start_date
        prev_start = start_date - period_duration
        prev_end = start_date
        
        prev_orders_queryset = Order.objects.filter(
            created_at__range=[prev_start, prev_end]
        )
        if tenant_id:
            prev_orders_queryset = prev_orders_queryset.filter(tenant_id=tenant_id)
        
        prev_revenue = prev_orders_queryset.filter(
            payment_status='paid'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        
        prev_total_orders = prev_orders_queryset.count()
        
        # Calculate trends
        revenue_trend = self._calculate_trend(float(total_revenue), float(prev_revenue))
        orders_trend = self._calculate_trend(total_orders, prev_total_orders)
        
        # Revenue Chart Data (daily breakdown)
        revenue_chart = self._get_revenue_chart_data(orders_queryset, start_date, end_date, period)
        
        # Top Products
        top_products = OrderItem.objects.filter(
            order__in=orders_queryset,
            order__payment_status='paid'
        ).values(
            'product_id',
            'product_name'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_revenue')[:10]
        
        # Recent Orders
        recent_orders = orders_queryset.select_related(
            'tenant', 'outlet'
        ).order_by('-created_at')[:10]
        
        recent_orders_data = []
        for order in recent_orders:
            time_diff = now - order.created_at
            minutes_ago = int(time_diff.total_seconds() / 60)
            
            if minutes_ago < 60:
                time_ago = f"{minutes_ago} min ago"
            elif minutes_ago < 1440:  # less than a day
                hours_ago = minutes_ago // 60
                time_ago = f"{hours_ago} hour{'s' if hours_ago > 1 else ''} ago"
            else:
                days_ago = minutes_ago // 1440
                time_ago = f"{days_ago} day{'s' if days_ago > 1 else ''} ago"
            
            recent_orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name or 'Walk-in Customer',
                'total_amount': float(order.total_amount),
                'status': order.status,
                'time_ago': time_ago,
                'created_at': order.created_at.isoformat()
            })
        
        # Response
        response_data = {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'metrics': {
                'total_revenue': float(total_revenue),
                'revenue_trend': revenue_trend,
                'total_orders': total_orders,
                'orders_trend': orders_trend,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
            },
            'revenue_chart': revenue_chart,
            'top_products': [
                {
                    'product_id': item['product_id'],
                    'product_name': item['product_name'],
                    'total_sold': item['total_sold'],
                    'total_revenue': float(item['total_revenue'])
                }
                for item in top_products
            ],
            'recent_orders': recent_orders_data
        }
        
        return Response(response_data)
    
    def _calculate_trend(self, current, previous):
        """Calculate percentage trend"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)
    
    def _get_revenue_chart_data(self, queryset, start_date, end_date, period):
        """Generate revenue chart data based on period"""
        chart_data = []
        
        if period == 'today':
            # Hourly breakdown for today
            for hour in range(24):
                hour_start = start_date.replace(hour=hour, minute=0, second=0)
                hour_end = hour_start + timedelta(hours=1)
                
                revenue = queryset.filter(
                    created_at__range=[hour_start, hour_end],
                    payment_status='paid'
                ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
                
                chart_data.append({
                    'label': f"{hour:02d}:00",
                    'value': float(revenue)
                })
        
        elif period in ['week', 'month']:
            # Daily breakdown
            current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            while current_date <= end_date:
                day_end = current_date + timedelta(days=1)
                
                revenue = queryset.filter(
                    created_at__range=[current_date, day_end],
                    payment_status='paid'
                ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
                
                chart_data.append({
                    'label': current_date.strftime('%d %b'),
                    'value': float(revenue)
                })
                
                current_date = day_end
        
        else:
            # Custom period - daily breakdown
            current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            while current_date <= end_date:
                day_end = current_date + timedelta(days=1)
                
                revenue = queryset.filter(
                    created_at__range=[current_date, day_end],
                    payment_status='paid'
                ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
                
                chart_data.append({
                    'label': current_date.strftime('%d %b'),
                    'value': float(revenue)
                })
                
                current_date = day_end
        
        return chart_data
