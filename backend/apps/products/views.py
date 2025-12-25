"""
Views for Product API
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for categories (Public access for Kiosk Mode)
    """
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name']
    ordering = ['sort_order']
    
    def get_queryset(self):
        """
        Use all_objects manager to bypass TenantManager filtering
        Filter by X-Tenant-ID header if provided
        """
        # Get tenant ID from header
        tenant_id = self.request.headers.get('X-Tenant-ID')
        
        if tenant_id:
            # Filter by specific tenant
            queryset = Category.all_objects.filter(
                tenant_id=tenant_id,
                is_active=True
            )
        else:
            # Return all if no tenant specified (backward compatible)
            queryset = Category.all_objects.filter(is_active=True)
        
        return queryset


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for products (Public access for Kiosk Mode)
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['category', 'name']
    
    def get_queryset(self):
        """
        Use all_objects manager to bypass TenantManager filtering
        Filter by X-Tenant-ID header if provided
        """
        # Get tenant ID from header
        tenant_id = self.request.headers.get('X-Tenant-ID')
        
        if tenant_id:
            # Filter by specific tenant
            queryset = Product.all_objects.filter(
                tenant_id=tenant_id,
                is_available=True
            ).select_related('category').prefetch_related('modifiers')
        else:
            # Return all if no tenant specified (backward compatible)
            queryset = Product.all_objects.filter(
                is_available=True
            ).select_related('category').prefetch_related('modifiers')
        
        return queryset
