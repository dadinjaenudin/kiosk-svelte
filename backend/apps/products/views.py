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
        return Category.all_objects.filter(is_active=True)


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
        return Product.all_objects.filter(is_available=True).select_related('category').prefetch_related('modifiers')
