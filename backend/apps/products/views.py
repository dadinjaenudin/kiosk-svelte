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
    API endpoint for categories (Public access for Food Court Mode)
    """
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name']
    ordering = ['sort_order']
    
    def get_queryset(self):
        """
        FOOD COURT MODE: Show all categories from all tenants
        Support optional filtering by tenant_id via query params
        """
        # Base queryset - ALL categories from ALL tenants
        queryset = Category.all_objects.filter(is_active=True).select_related('tenant')
        
        # Optional: Filter by tenant_id from query params
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
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
        FOOD COURT MODE: Show all products from all tenants
        Support optional filtering by tenant_id via query params
        """
        # Base queryset - ALL products from ALL tenants
        queryset = Product.all_objects.filter(
            is_available=True
        ).select_related('category', 'tenant').prefetch_related('modifiers')
        
        # Optional: Filter by tenant_id from query params (for food court filter tabs)
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # Optional: Filter by category
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset
