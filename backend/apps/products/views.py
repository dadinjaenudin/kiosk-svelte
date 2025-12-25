"""
Views for Product API
"""
import logging
from rest_framework import viewsets, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for categories (Public access for Kiosk Mode)
    """
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Public access for kiosk
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name']
    ordering = ['sort_order']
    
    def get_queryset(self):
        """
        Override to use all_objects manager for public access
        Bypasses TenantManager filtering for kiosk mode
        """
        try:
            qs = Category.all_objects.filter(is_active=True)
            logger.info(f"CategoryViewSet queryset count: {qs.count()}")
            return qs
        except Exception as e:
            logger.error(f"Error in CategoryViewSet.get_queryset: {e}")
            raise
    
    def list(self, request, *args, **kwargs):
        """Override list to add detailed logging"""
        try:
            logger.info(f"CategoryViewSet.list called - Request: {request.method} {request.path}")
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in CategoryViewSet.list: {e}", exc_info=True)
            return Response(
                {'error': str(e), 'detail': 'Failed to fetch categories'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for products (Public access for Kiosk Mode)
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Public access for kiosk
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['category', 'name']
    
    def get_queryset(self):
        """
        Override to use all_objects manager for public access
        Bypasses TenantManager filtering for kiosk mode
        """
        try:
            qs = Product.all_objects.filter(is_available=True).select_related('category').prefetch_related('modifiers')
            logger.info(f"ProductViewSet queryset count: {qs.count()}")
            return qs
        except Exception as e:
            logger.error(f"Error in ProductViewSet.get_queryset: {e}")
            raise
    
    def list(self, request, *args, **kwargs):
        """Override list to add detailed logging"""
        try:
            logger.info(f"ProductViewSet.list called - Request: {request.method} {request.path}")
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in ProductViewSet.list: {e}", exc_info=True)
            return Response(
                {'error': str(e), 'detail': 'Failed to fetch products'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
