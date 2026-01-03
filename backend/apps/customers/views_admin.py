"""
Admin views for Customer Management
"""
from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer, CustomerDetailSerializer
from apps.core.permissions import (
    IsAdminOrTenantOwnerOrManager,
    IsManagerOrAbove,
    is_admin_user
)
from apps.core.context import get_current_tenant


class CustomerManagementViewSet(viewsets.ModelViewSet):
    """
    Admin API for Customer Management
    
    Endpoints:
    - GET /api/admin/customers/ - List customers
    - POST /api/admin/customers/ - Create customer
    - GET /api/admin/customers/{id}/ - Get customer detail
    - PUT /api/admin/customers/{id}/ - Update customer
    - PATCH /api/admin/customers/{id}/ - Partial update
    - DELETE /api/admin/customers/{id}/ - Delete customer
    - GET /api/admin/customers/stats/ - Customer statistics
    - POST /api/admin/customers/bulk_update/ - Bulk update customers
    - POST /api/admin/customers/{id}/add_points/ - Add points to customer
    - POST /api/admin/customers/{id}/redeem_points/ - Redeem customer points
    """
    
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['membership_tier', 'is_active', 'gender', 'is_subscribed', 'preferred_outlet']
    search_fields = ['name', 'email', 'phone', 'membership_number']
    ordering_fields = ['name', 'created_at', 'last_order_at', 'points']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter customers by current tenant.
        Admin/Superuser can see all customers.
        """
        user = self.request.user
        
        if is_admin_user(user):
            return Customer.objects.all()
        
        tenant = get_current_tenant()
        if tenant:
            return Customer.objects.filter(tenant=tenant)
        
        return Customer.objects.none()
    
    def get_serializer_class(self):
        """
        Use detailed serializer for retrieve actions
        """
        if self.action == 'retrieve':
            return CustomerDetailSerializer
        return CustomerSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Override create to add debug logging
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.warning(f"🔍 CREATE REQUEST - Data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"❌ VALIDATION ERRORS: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """
        Auto-set tenant when creating customer
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Log request data for debugging
        logger.warning(f"🔍 CREATE CUSTOMER - Request data: {self.request.data}")
        logger.warning(f"🔍 CREATE CUSTOMER - User: {self.request.user.username}, Is superuser: {self.request.user.is_superuser}")
        
        # Get tenant from request data or context
        tenant = None
        
        # If tenant is provided in request data, use it (for superuser)
        if 'tenant' in self.request.data:
            from apps.tenants.models import Tenant
            tenant_id = self.request.data.get('tenant')
            try:
                tenant = Tenant.objects.get(id=tenant_id)
                logger.warning(f"✅ Using tenant from request: {tenant.name}")
            except Tenant.DoesNotExist:
                logger.warning(f"❌ Tenant {tenant_id} not found")
                pass
        
        # Otherwise, get from context (for tenant-scoped users)
        if not tenant:
            tenant = get_current_tenant()
            if tenant:
                logger.warning(f"✅ Using tenant from context: {tenant.name}")
        
        # For superuser without tenant in context, use first tenant
        if not tenant and self.request.user.is_superuser:
            from apps.tenants.models import Tenant
            tenant = Tenant.objects.first()
            if tenant:
                logger.warning(f"✅ Using first tenant for superuser: {tenant.name}")
        
        if tenant:
            serializer.save(tenant=tenant)
            logger.warning(f"✅ Customer created successfully for tenant: {tenant.name}")
        else:
            # This should not happen, but handle gracefully
            logger.warning("❌ No tenant available!")
            raise serializers.ValidationError("No tenant available for customer creation")
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete - set is_active to False instead of deleting
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response({
            'status': 'success',
            'message': 'Customer deactivated successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get customer statistics
        
        GET /api/admin/customers/stats/
        
        Returns:
        - total: Total customer count
        - active: Active customer count  
        - inactive: Inactive customer count
        - by_tier: Breakdown by membership tier
        - by_gender: Breakdown by gender
        - new_this_month: New customers this month
        - total_points: Total loyalty points
        - avg_points: Average points per customer
        """
        queryset = self.get_queryset()
        
        # Calculate date for this month
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        stats = {
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'inactive': queryset.filter(is_active=False).count(),
            'by_tier': {},
            'by_gender': {},
            'new_this_month': queryset.filter(created_at__gte=first_day_of_month).count(),
            'total_points': 0,
            'avg_points': 0,
        }
        
        # Group by tier
        for customer in queryset:
            tier = customer.membership_tier or 'regular'
            stats['by_tier'][tier] = stats['by_tier'].get(tier, 0) + 1
        
        # Group by gender
        for customer in queryset:
            gender = customer.get_gender_display() if customer.gender else 'Not specified'
            stats['by_gender'][gender] = stats['by_gender'].get(gender, 0) + 1
        
        # Calculate points
        points_agg = queryset.aggregate(
            total=Sum('points'),
            average=Avg('points')
        )
        stats['total_points'] = points_agg['total'] or 0
        stats['avg_points'] = round(points_agg['average'] or 0, 2)
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update customers
        
        POST /api/admin/customers/bulk_update/
        
        Request body:
        {
            "customer_ids": [1, 2, 3],
            "updates": {
                "is_active": true,
                "membership_tier": "gold"
            }
        }
        """
        customer_ids = request.data.get('customer_ids', [])
        updates = request.data.get('updates', {})
        
        if not customer_ids:
            return Response({
                'error': 'customer_ids is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not updates:
            return Response({
                'error': 'updates is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter customers by tenant
        queryset = self.get_queryset()
        customers = queryset.filter(id__in=customer_ids)
        
        # Update customers
        count = customers.update(**updates, updated_at=timezone.now())
        
        return Response({
            'status': 'success',
            'message': f'{count} customers updated successfully',
            'updated_count': count
        })
    
    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        """
        Add loyalty points to customer
        
        POST /api/admin/customers/{id}/add_points/
        
        Request body:
        {
            "points": 100,
            "reason": "Birthday bonus"
        }
        """
        customer = self.get_object()
        points = request.data.get('points', 0)
        reason = request.data.get('reason', '')
        
        if not isinstance(points, int) or points <= 0:
            return Response({
                'error': 'Points must be a positive integer'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        customer.points += points
        customer.save()
        
        return Response({
            'status': 'success',
            'message': f'{points} points added successfully',
            'new_total': customer.points,
            'reason': reason
        })
    
    @action(detail=True, methods=['post'])
    def redeem_points(self, request, pk=None):
        """
        Redeem loyalty points from customer
        
        POST /api/admin/customers/{id}/redeem_points/
        
        Request body:
        {
            "points": 50,
            "reason": "Redeemed for discount"
        }
        """
        customer = self.get_object()
        points = request.data.get('points', 0)
        reason = request.data.get('reason', '')
        
        if not isinstance(points, int) or points <= 0:
            return Response({
                'error': 'Points must be a positive integer'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if customer.points < points:
            return Response({
                'error': f'Insufficient points. Customer has {customer.points} points'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        customer.points -= points
        customer.save()
        
        return Response({
            'status': 'success',
            'message': f'{points} points redeemed successfully',
            'new_total': customer.points,
            'reason': reason
        })
    
    @action(detail=False, methods=['get'])
    def top_customers(self, request):
        """
        Get top customers by total spent
        
        GET /api/admin/customers/top_customers/?limit=10
        """
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_queryset().filter(is_active=True)
        
        # Get customers with order stats
        from apps.orders.models import Order
        
        top_customers = []
        for customer in queryset[:100]:  # Limit initial query
            total_spent = customer.total_spent
            if total_spent > 0:
                top_customers.append({
                    'id': customer.id,
                    'name': customer.name,
                    'phone': customer.phone,
                    'email': customer.email,
                    'membership_tier': customer.membership_tier,
                    'total_orders': customer.total_orders,
                    'total_spent': float(total_spent),
                    'average_order_value': float(customer.average_order_value),
                })
        
        # Sort by total_spent
        top_customers.sort(key=lambda x: x['total_spent'], reverse=True)
        
        return Response(top_customers[:limit])
