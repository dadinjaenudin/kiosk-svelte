"""
Reports API Views for Admin
Provides various reports: sales, products, orders, customers, etc.
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F, DecimalField
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.orders.models import Order, OrderItem
from apps.products.models import Product, Category
from apps.users.models import User
from apps.core.permissions import IsAdminOrTenantOwnerOrManager

logger = logging.getLogger(__name__)


class ReportsViewSet(viewsets.ViewSet):
    """
    Reports API for Admin Dashboard
    
    Endpoints:
    - GET /api/admin/reports/sales_summary/ - Sales summary report
    - GET /api/admin/reports/sales_by_period/ - Sales grouped by period
    - GET /api/admin/reports/top_products/ - Top selling products
    - GET /api/admin/reports/top_categories/ - Top selling categories
    - GET /api/admin/reports/sales_by_category/ - Sales breakdown by category
    - GET /api/admin/reports/customer_stats/ - Customer statistics
    - GET /api/admin/reports/order_stats/ - Order statistics
    - GET /api/admin/reports/revenue_trend/ - Revenue trend over time
    - GET /api/admin/reports/payment_methods/ - Payment method breakdown
    - GET /api/admin/reports/hourly_sales/ - Sales by hour of day
    """
    permission_classes = [IsAuthenticated, IsAdminOrTenantOwnerOrManager]
    
    def get_queryset_for_user(self, model, date_field='created_at', start_date=None, end_date=None):
        """
        Get filtered queryset based on user role and date range
        """
        user = self.request.user
        queryset = model.objects.all()
        
        # Apply tenant filtering
        if user.role == 'admin':
            # Admin sees all
            pass
        elif hasattr(user, 'tenant') and user.tenant:
            # Tenant sees only their data
            if hasattr(model, 'tenant'):
                queryset = queryset.filter(tenant=user.tenant)
            elif model == Order:
                queryset = queryset.filter(tenant=user.tenant)
        else:
            return model.objects.none()
        
        # Apply date filtering
        if start_date and end_date:
            filter_kwargs = {
                f'{date_field}__gte': start_date,
                f'{date_field}__lte': end_date
            }
            queryset = queryset.filter(**filter_kwargs)
        
        return queryset
    
    def get_date_range(self, request):
        """
        Parse date range from request params
        Default: last 30 days
        """
        period = request.query_params.get('period', '30days')
        
        end_date = timezone.now()
        
        if period == 'today':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'yesterday':
            start_date = (end_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif period == '7days':
            start_date = end_date - timedelta(days=7)
        elif period == '30days':
            start_date = end_date - timedelta(days=30)
        elif period == '90days':
            start_date = end_date - timedelta(days=90)
        elif period == 'this_month':
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'last_month':
            first_of_this_month = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = first_of_this_month
            start_date = (first_of_this_month - timedelta(days=1)).replace(day=1)
        elif period == 'custom':
            # Custom date range
            start_str = request.query_params.get('start_date')
            end_str = request.query_params.get('end_date')
            
            if start_str and end_str:
                start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            else:
                start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=30)
        
        return start_date, end_date
    
    @action(detail=False, methods=['get'])
    def sales_summary(self, request):
        """
        Sales summary report
        
        GET /api/admin/reports/sales_summary/?period=30days
        """
        start_date, end_date = self.get_date_range(request)
        
        # Get orders in date range
        orders = self.get_queryset_for_user(Order, 'created_at', start_date, end_date)
        
        # Completed orders only
        completed_orders = orders.filter(status='completed')
        
        # Calculate metrics
        total_revenue = completed_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        total_orders = completed_orders.count()
        
        average_order_value = completed_orders.aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0
        
        total_items_sold = OrderItem.objects.filter(
            order__in=completed_orders
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        # Compare with previous period
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date
        
        prev_orders = self.get_queryset_for_user(Order, 'created_at', prev_start, prev_end)
        prev_completed = prev_orders.filter(status='completed')
        
        prev_revenue = prev_completed.aggregate(total=Sum('total_amount'))['total'] or 0
        prev_orders_count = prev_completed.count()
        
        # Calculate growth
        revenue_growth = 0
        if prev_revenue > 0:
            revenue_growth = ((total_revenue - prev_revenue) / prev_revenue) * 100
        
        orders_growth = 0
        if prev_orders_count > 0:
            orders_growth = ((total_orders - prev_orders_count) / prev_orders_count) * 100
        
        return Response({
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'label': request.query_params.get('period', '30days')
            },
            'summary': {
                'total_revenue': float(total_revenue),
                'total_orders': total_orders,
                'average_order_value': float(average_order_value),
                'total_items_sold': total_items_sold,
                'revenue_growth': round(revenue_growth, 2),
                'orders_growth': round(orders_growth, 2)
            }
        })
    
    @action(detail=False, methods=['get'])
    def sales_by_period(self, request):
        """
        Sales grouped by period (day/week/month)
        
        GET /api/admin/reports/sales_by_period/?period=30days&group_by=day
        """
        start_date, end_date = self.get_date_range(request)
        group_by = request.query_params.get('group_by', 'day')
        
        orders = self.get_queryset_for_user(Order, 'created_at', start_date, end_date)
        completed_orders = orders.filter(status='completed')
        
        # Group by period
        if group_by == 'day':
            trunc_func = TruncDate('created_at')
        elif group_by == 'week':
            trunc_func = TruncWeek('created_at')
        elif group_by == 'month':
            trunc_func = TruncMonth('created_at')
        else:
            trunc_func = TruncDate('created_at')
        
        sales_data = completed_orders.annotate(
            period=trunc_func
        ).values('period').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id'),
            items=Sum('items__quantity')
        ).order_by('period')
        
        # Format response
        results = []
        for item in sales_data:
            results.append({
                'period': item['period'].isoformat() if item['period'] else None,
                'revenue': float(item['revenue'] or 0),
                'orders': item['orders'],
                'items': item['items'] or 0
            })
        
        return Response({
            'group_by': group_by,
            'data': results
        })
    
    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """
        Top selling products
        
        GET /api/admin/reports/top_products/?period=30days&limit=10
        """
        start_date, end_date = self.get_date_range(request)
        limit = int(request.query_params.get('limit', 10))
        
        orders = self.get_queryset_for_user(Order, 'created_at', start_date, end_date)
        completed_orders = orders.filter(status='completed')
        
        # Get top products
        top_products = OrderItem.objects.filter(
            order__in=completed_orders
        ).values(
            'product_id',
            'product__name',
            'product__image'
        ).annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('price'), output_field=DecimalField()),
            orders_count=Count('order', distinct=True)
        ).order_by('-quantity_sold')[:limit]
        
        results = []
        for item in top_products:
            results.append({
                'product_id': item['product_id'],
                'product_name': item['product__name'],
                'product_image': item['product__image'],
                'quantity_sold': item['quantity_sold'],
                'revenue': float(item['revenue'] or 0),
                'orders_count': item['orders_count']
            })
        
        return Response({
            'limit': limit,
            'data': results
        })
    
    @action(detail=False, methods=['get'])
    def top_categories(self, request):
        """
        Top selling categories
        
        GET /api/admin/reports/top_categories/?period=30days
        """
        start_date, end_date = self.get_date_range(request)
        
        orders = self.get_queryset_for_user(Order, 'created_at', start_date, end_date)
        completed_orders = orders.filter(status='completed')
        
        # Get top categories
        top_categories = OrderItem.objects.filter(
            order__in=completed_orders
        ).values(
            'product__category_id',
            'product__category__name'
        ).annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('price'), output_field=DecimalField()),
            orders_count=Count('order', distinct=True)
        ).order_by('-revenue')
        
        results = []
        for item in top_categories:
            if item['product__category_id']:  # Skip items without category
                results.append({
                    'category_id': item['product__category_id'],
                    'category_name': item['product__category__name'],
                    'quantity_sold': item['quantity_sold'],
                    'revenue': float(item['revenue'] or 0),
                    'orders_count': item['orders_count']
                })
        
        return Response({'data': results})
    
    @action(detail=False, methods=['get'])
    def sales_by_category(self, request):
        """
        Sales breakdown by category (for pie chart)
        
        GET /api/admin/reports/sales_by_category/?period=30days
        """
        return self.top_categories(request)
    
    @action(detail=False, methods=['get'])
    def customer_stats(self, request):
        """
        Customer statistics
        
        GET /api/admin/reports/customer_stats/?period=30days
        """
        start_date, end_date = self.get_date_range(request)
        
        orders = self.get_queryset_for_user(Order, 'created_at', start_date, end_date)
        
        # Total unique customers
        total_customers = orders.values('customer_name').distinct().count()
        
        # New customers (first order in period)
        # This is simplified - in production you'd track actual customer IDs
        new_customers = orders.filter(
            created_at__gte=start_date
        ).values('customer_name').distinct().count()
        
        # Average orders per customer
        avg_orders = 0
        if total_customers > 0:
            total_orders = orders.count()
            avg_orders = total_orders / total_customers
        
        # Repeat customers (more than 1 order)
        repeat_customers = orders.values('customer_name').annotate(
            order_count=Count('id')
        ).filter(order_count__gt=1).count()
        
        return Response({
            'total_customers': total_customers,
            'new_customers': new_customers,
            'repeat_customers': repeat_customers,
            'average_orders_per_customer': round(avg_orders, 2)
        })
    
    @action(detail=False, methods=['get'])
    def order_stats(self, request):
        """
        Order statistics by status
        
        GET /api/admin/reports/order_stats/?period=30days
        """
        start_date, end_date = self.get_date_range(request)
        
        orders = self.get_queryset_for_user(Order, 'created_at', start_date, end_date)
        
        # Count by status
        status_counts = orders.values('status').annotate(
            count=Count('id'),
            revenue=Sum('total_amount')
        )
        
        results = {}
        for item in status_counts:
            results[item['status']] = {
                'count': item['count'],
                'revenue': float(item['revenue'] or 0)
            }
        
        # Add totals
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        
        return Response({
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'by_status': results
        })
    
    @action(detail=False, methods=['get'])
    def revenue_trend(self, request):
        """
        Revenue trend over time (for line chart)
        
        GET /api/admin/reports/revenue_trend/?period=30days
        """
        return self.sales_by_period(request)
    
    @action(detail=False, methods=['get'])
    def payment_methods(self, request):
        """
        Payment method breakdown
        
        GET /api/admin/reports/payment_methods/?period=30days
        """
        start_date, end_date = self.get_date_range(request)
        
        orders = self.get_queryset_for_user(Order, 'created_at', start_date, end_date)
        completed_orders = orders.filter(status='completed')
        
        # Count by payment method
        payment_stats = completed_orders.values('payment_method').annotate(
            count=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('-revenue')
        
        results = []
        for item in payment_stats:
            results.append({
                'method': item['payment_method'] or 'Unknown',
                'count': item['count'],
                'revenue': float(item['revenue'] or 0)
            })
        
        return Response({'data': results})
    
    @action(detail=False, methods=['get'])
    def hourly_sales(self, request):
        """
        Sales by hour of day
        
        GET /api/admin/reports/hourly_sales/?period=7days
        """
        start_date, end_date = self.get_date_range(request)
        
        orders = self.get_queryset_for_user(Order, 'created_at', start_date, end_date)
        completed_orders = orders.filter(status='completed')
        
        # Group by hour
        hourly_data = completed_orders.extra(
            select={'hour': 'EXTRACT(hour FROM created_at)'}
        ).values('hour').annotate(
            orders=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('hour')
        
        # Initialize all hours (0-23)
        results = [{'hour': h, 'orders': 0, 'revenue': 0} for h in range(24)]
        
        # Fill in actual data
        for item in hourly_data:
            hour = int(item['hour'])
            results[hour] = {
                'hour': hour,
                'orders': item['orders'],
                'revenue': float(item['revenue'] or 0)
            }
        
        return Response({'data': results})
