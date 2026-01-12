from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import models
from django.db.models import Q, Count, Sum, Prefetch

from .models import Promotion, PromotionProduct, PromotionUsage
from .serializers import (
    PromotionSerializer,
    PromotionListSerializer,
    PromotionUsageSerializer,
    ProductSimpleSerializer
)
from apps.products.models import Product
from apps.core.permissions import is_admin_user


class PromotionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Promotion CRUD operations
    """
    permission_classes = [AllowAny]  # Changed to AllowAny for Kiosk public access
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'promo_type', 'is_active', 'is_featured', 'tenant']
    search_fields = ['name', 'description', 'code']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'usage_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # Get tenant filter from query params (for admin users)
        tenant_id = self.request.query_params.get('tenant')
        
        # PUBLIC ACCESS (Anonymous users - Kiosk Mode): Show all active promotions
        if user.is_anonymous:
            queryset = Promotion.objects.filter(is_active=True)
            
            # Optional: Filter by tenant_id from query params
            if tenant_id:
                try:
                    queryset = queryset.filter(tenant_id=int(tenant_id))
                except (ValueError, TypeError):
                    pass
        # Super admins can see all promotions
        elif is_admin_user(user):
            queryset = Promotion.objects.all()
            
            # Apply tenant filter for admin if provided
            if tenant_id:
                try:
                    queryset = queryset.filter(tenant_id=int(tenant_id))
                except (ValueError, TypeError):
                    pass
        # Tenant owners/managers see their tenant's promos
        elif hasattr(user, 'tenant') and user.tenant:
            queryset = Promotion.objects.filter(tenant=user.tenant)
        else:
            queryset = Promotion.objects.none()
        
        # Apply additional filters from query params
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(start_date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(end_date__lte=date_to)
        
        return queryset.select_related('tenant', 'created_by').prefetch_related(
            Prefetch(
                'promotion_products',
                queryset=PromotionProduct.objects.select_related('product')
            )
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PromotionListSerializer
        return PromotionSerializer
    
    def perform_create(self, serializer):
        # Auto-set tenant for tenant users
        user = self.request.user
        if user.tenant and user.role != 'admin':
            serializer.save(tenant=user.tenant)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a promotion"""
        promotion = self.get_object()
        
        # Check if dates are valid
        now = timezone.now()
        if promotion.start_date > now:
            return Response(
                {'error': 'Cannot activate promotion before start date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if promotion.end_date < now:
            return Response(
                {'error': 'Cannot activate expired promotion'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        promotion.is_active = True
        promotion.status = Promotion.STATUS_ACTIVE
        promotion.save()
        
        serializer = self.get_serializer(promotion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a promotion"""
        promotion = self.get_object()
        promotion.is_active = False
        promotion.status = Promotion.STATUS_PAUSED
        promotion.save()
        
        serializer = self.get_serializer(promotion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview promotion effects on products"""
        promotion = self.get_object()
        products = promotion.promotion_products.all()
        
        preview_data = []
        for promo_product in products:
            product = promo_product.product
            original_price = product.price
            
            # Calculate discounted price
            if promotion.promo_type == Promotion.TYPE_PERCENTAGE:
                discount = (original_price * promotion.discount_value) / 100
                if promotion.max_discount_amount:
                    discount = min(discount, promotion.max_discount_amount)
            elif promotion.promo_type == Promotion.TYPE_FIXED:
                discount = min(promotion.discount_value, original_price)
            else:
                discount = 0
            
            discounted_price = original_price - discount
            
            preview_data.append({
                'product_id': product.id,
                'product_name': product.name,
                'original_price': original_price,
                'discount_amount': discount,
                'discounted_price': discounted_price,
                'discount_percentage': (discount / original_price * 100) if original_price > 0 else 0
            })
        
        return Response({
            'promotion': self.get_serializer(promotion).data,
            'products': preview_data,
            'total_products': len(preview_data)
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently active promotions"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            is_active=True,
            status=Promotion.STATUS_ACTIVE,
            start_date__lte=now,
            end_date__gte=now
        )
        
        # Filter by valid day of week
        weekday = now.weekday()
        day_filters = {
            0: Q(monday=True),
            1: Q(tuesday=True),
            2: Q(wednesday=True),
            3: Q(thursday=True),
            4: Q(friday=True),
            5: Q(saturday=True),
            6: Q(sunday=True),
        }
        queryset = queryset.filter(day_filters[weekday])
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get promotion statistics"""
        queryset = self.get_queryset()
        
        total_promotions = queryset.count()
        active_promotions = queryset.filter(
            is_active=True,
            status=Promotion.STATUS_ACTIVE
        ).count()
        
        draft_promotions = queryset.filter(status=Promotion.STATUS_DRAFT).count()
        expired_promotions = queryset.filter(status=Promotion.STATUS_EXPIRED).count()
        
        # Usage stats
        total_usage = queryset.aggregate(total=Sum('usage_count'))['total'] or 0
        
        # Total discount given
        total_discount = PromotionUsage.objects.filter(
            promotion__in=queryset
        ).aggregate(total=Sum('discount_amount'))['total'] or 0
        
        return Response({
            'total_promotions': total_promotions,
            'active_promotions': active_promotions,
            'draft_promotions': draft_promotions,
            'expired_promotions': expired_promotions,
            'total_usage': total_usage,
            'total_discount_given': total_discount
        })


class PromotionUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing promotion usage history
    """
    serializer_class = PromotionUsageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['promotion', 'customer_identifier']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'admin':
            return PromotionUsage.objects.all()
        elif user.tenant:
            return PromotionUsage.objects.filter(promotion__tenant=user.tenant)
        return PromotionUsage.objects.none()


class ProductSelectorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for product selector in promotion form
    Uses _base_manager to bypass tenant filtering
    """
    serializer_class = ProductSimpleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    filterset_fields = ['tenant', 'is_available']
    
    def get_queryset(self):
        user = self.request.user
        
        # Use _base_manager to bypass TenantManager filtering
        from apps.products.models import Product
        
        # Admin can see all products or filter by tenant
        if user.is_superuser or user.role in ['admin', 'super_admin']:
            queryset = Product._base_manager.all()
        elif user.tenant:
            queryset = Product._base_manager.filter(tenant=user.tenant)
        else:
            queryset = Product._base_manager.none()
        
        # Filter by tenant from query parameter if provided (for admin users)
        tenant_id = self.request.query_params.get('tenant')
        if tenant_id and (user.is_superuser or user.role in ['admin', 'super_admin']):
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset.filter(is_available=True).select_related('tenant')

