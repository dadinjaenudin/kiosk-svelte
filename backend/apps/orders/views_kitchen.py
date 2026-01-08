from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta

from apps.orders.models import Order, OrderItem
from apps.orders.serializers_kitchen import (
    KitchenOrderSerializer,
    KitchenOrderStatusUpdateSerializer,
    KitchenStatsSerializer
)
from apps.tenants.models import Outlet, Store


class KitchenOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Kitchen Order ViewSet - For kitchen display system
    Provides endpoints for viewing and managing orders in kitchen
    """
    serializer_class = KitchenOrderSerializer
    permission_classes = [AllowAny]  # TODO: Add authentication for production
    
    def get_queryset(self):
        """
        Filter orders based on query params:
        - outlet: Filter by outlet/brand ID
        - store: Filter by store ID
        - status: Filter by order status
        - station: Filter by kitchen station (via product category)
        """
        queryset = Order.objects.select_related(
            'tenant', 'outlet', 'store', 'order_group'
        ).prefetch_related(
            'items__product'
        ).exclude(
            status__in=['draft', 'cancelled']
        )
        
        # Filter by outlet/brand
        outlet_id = self.request.query_params.get('outlet')
        if outlet_id:
            queryset = queryset.filter(outlet_id=outlet_id)
        
        # Filter by store
        store_id = self.request.query_params.get('store')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by today only (default)
        today_only = self.request.query_params.get('today_only', 'true')
        if today_only.lower() == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(created_at__date=today)
        
        return queryset.order_by('created_at')
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending orders (new orders waiting to be prepared)"""
        queryset = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def preparing(self, request):
        """Get all orders being prepared"""
        queryset = self.get_queryset().filter(status='preparing')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ready(self, request):
        """Get all orders ready for pickup/serving"""
        queryset = self.get_queryset().filter(status='ready')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Start preparing an order
        Transition: pending → preparing
        """
        order = self.get_object()
        
        if order.status != 'pending':
            return Response(
                {'error': f'Cannot start order with status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'preparing'
        order.save()
        
        serializer = self.get_serializer(order)
        
        # TODO: Broadcast to Socket.IO
        # emit_order_update(order, 'started')
        
        return Response({
            'message': 'Order started',
            'order': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark order as ready
        Transition: preparing → ready
        """
        order = self.get_object()
        
        if order.status != 'preparing':
            return Response(
                {'error': f'Cannot complete order with status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'ready'
        order.completed_at = timezone.now()
        order.save()
        
        serializer = self.get_serializer(order)
        
        # TODO: Broadcast to Socket.IO
        # emit_order_update(order, 'ready')
        # TODO: Send customer notification
        
        return Response({
            'message': 'Order marked as ready',
            'order': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def serve(self, request, pk=None):
        """
        Mark order as served (picked up by customer)
        Transition: ready → served
        """
        order = self.get_object()
        
        if order.status != 'ready':
            return Response(
                {'error': f'Cannot serve order with status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'served'
        if not order.completed_at:
            order.completed_at = timezone.now()
        order.save()
        
        serializer = self.get_serializer(order)
        
        # TODO: Broadcast to Socket.IO
        # emit_order_update(order, 'served')
        
        return Response({
            'message': 'Order marked as served',
            'order': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        if order.status in ['completed', 'served', 'cancelled']:
            return Response(
                {'error': f'Cannot cancel order with status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer_input = KitchenOrderStatusUpdateSerializer(data=request.data)
        if serializer_input.is_valid():
            order.status = 'cancelled'
            if serializer_input.validated_data.get('notes'):
                order.notes = (order.notes or '') + '\n' + f"Cancelled: {serializer_input.validated_data['notes']}"
            order.save()
            
            serializer = self.get_serializer(order)
            
            # TODO: Broadcast to Socket.IO
            # emit_order_update(order, 'cancelled')
            
            return Response({
                'message': 'Order cancelled',
                'order': serializer.data
            })
        
        return Response(serializer_input.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get kitchen statistics for today"""
        outlet_id = request.query_params.get('outlet')
        store_id = request.query_params.get('store')
        
        today = timezone.now().date()
        queryset = Order.objects.filter(created_at__date=today)
        
        if outlet_id:
            queryset = queryset.filter(outlet_id=outlet_id)
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        # Calculate stats
        pending_count = queryset.filter(status='pending').count()
        preparing_count = queryset.filter(status='preparing').count()
        ready_count = queryset.filter(status='ready').count()
        completed_today = queryset.filter(
            status__in=['completed', 'served']
        ).count()
        total_orders_today = queryset.exclude(status='cancelled').count()
        
        # Calculate average prep time (for completed orders)
        completed_orders = queryset.filter(
            status__in=['completed', 'served'],
            completed_at__isnull=False
        )
        
        if completed_orders.exists():
            total_time = sum([
                (order.completed_at - order.created_at).total_seconds() / 60
                for order in completed_orders
            ])
            avg_prep_time = total_time / completed_orders.count()
        else:
            avg_prep_time = 0.0
        
        data = {
            'pending_count': pending_count,
            'preparing_count': preparing_count,
            'ready_count': ready_count,
            'completed_today': completed_today,
            'avg_prep_time': round(avg_prep_time, 2),
            'total_orders_today': total_orders_today,
        }
        
        serializer = KitchenStatsSerializer(data)
        return Response(serializer.data)
