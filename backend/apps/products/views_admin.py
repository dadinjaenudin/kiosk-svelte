"""
Admin views for Product Management with Image Upload
"""
import logging
from rest_framework import viewsets, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, F
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import models
import os

from apps.products.models import Product, Category, ProductModifier
from apps.products.serializers import ProductSerializer, CategorySerializer, ProductModifierSerializer
from apps.core.permissions import IsAdminOrTenantOwnerOrManager

logger = logging.getLogger(__name__)


class CategoryAdminSerializer(CategorySerializer):
    """Extended category serializer for admin with write support"""
    
    class Meta(CategorySerializer.Meta):
        read_only_fields = ['created_at', 'updated_at']


class ProductAdminSerializer(ProductSerializer):
    """Extended product serializer for admin with write support"""
    
    class Meta(ProductSerializer.Meta):
        read_only_fields = ['created_at', 'updated_at']


class CategoryManagementViewSet(viewsets.ModelViewSet):
    """
    Admin API for Category Management
    
    Endpoints:
    - GET /api/admin/categories/ - List categories
    - POST /api/admin/categories/ - Create category
    - GET /api/admin/categories/{id}/ - Get category detail
    - PUT /api/admin/categories/{id}/ - Update category
    - PATCH /api/admin/categories/{id}/ - Partial update
    - DELETE /api/admin/categories/{id}/ - Delete category
    """
    serializer_class = CategoryAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTenantOwnerOrManager]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tenant', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        """
        Filter categories based on user role
        """
        user = self.request.user
        
        if user.role == 'admin':
            # Super admin sees all categories
            return Category.objects.all().select_related('tenant')
        elif user.tenant:
            # Tenant users see only their categories
            return Category.objects.filter(tenant=user.tenant)
        
        return Category.objects.none()
    
    def perform_create(self, serializer):
        """Auto-assign tenant for tenant users"""
        user = self.request.user
        if user.tenant and user.role != 'admin':
            serializer.save(tenant=user.tenant)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get category statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_categories': queryset.count(),
            'active_categories': queryset.filter(is_active=True).count(),
            'inactive_categories': queryset.filter(is_active=False).count(),
            'categories_with_products': queryset.annotate(
                product_count=Count('products')
            ).filter(product_count__gt=0).count()
        }
        
        return Response(stats)


class ProductManagementViewSet(viewsets.ModelViewSet):
    """
    Admin API for Product Management with Image Upload
    
    Endpoints:
    - GET /api/admin/products/ - List products
    - POST /api/admin/products/ - Create product (with image upload)
    - GET /api/admin/products/{id}/ - Get product detail
    - PUT /api/admin/products/{id}/ - Update product (with image upload)
    - PATCH /api/admin/products/{id}/ - Partial update
    - DELETE /api/admin/products/{id}/ - Delete product
    - POST /api/admin/products/{id}/upload_image/ - Upload/update product image
    - DELETE /api/admin/products/{id}/delete_image/ - Delete product image
    """
    serializer_class = ProductAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTenantOwnerOrManager]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'tenant', 'category', 'is_active', 'is_available', 
        'is_featured', 'is_popular', 'has_promo', 'track_stock'
    ]
    search_fields = ['name', 'description', 'sku', 'tags']
    ordering_fields = ['name', 'price', 'stock_quantity', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter products based on user role
        """
        user = self.request.user
        
        if user.role == 'admin':
            # Super admin sees all products
            queryset = Product.objects.all()
        elif user.tenant:
            # Tenant users see only their products
            queryset = Product.objects.filter(tenant=user.tenant)
        else:
            queryset = Product.objects.none()
        
        return queryset.select_related('tenant', 'category').prefetch_related('modifiers')
    
    def perform_create(self, serializer):
        """Auto-assign tenant and handle image upload"""
        user = self.request.user
        
        # Auto-assign tenant for tenant users
        if user.tenant and user.role != 'admin':
            product = serializer.save(tenant=user.tenant)
        else:
            product = serializer.save()
        
        # Log creation
        logger.info(f"Product created: {product.name} (ID: {product.id}) by {user.username}")
        
        return product
    
    def perform_update(self, serializer):
        """Handle image upload on update"""
        product = serializer.save()
        logger.info(f"Product updated: {product.name} (ID: {product.id}) by {self.request.user.username}")
        return product
    
    def perform_destroy(self, instance):
        """Delete product and its image"""
        product_name = instance.name
        product_id = instance.id
        
        # Delete image file if exists
        if instance.image:
            try:
                default_storage.delete(instance.image.name)
            except Exception as e:
                logger.warning(f"Failed to delete image for product {product_id}: {str(e)}")
        
        instance.delete()
        logger.info(f"Product deleted: {product_name} (ID: {product_id}) by {self.request.user.username}")
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        """
        Upload or update product image
        
        POST /api/admin/products/{id}/upload_image/
        Content-Type: multipart/form-data
        Body: image file
        """
        product = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response(
                {'error': f'Invalid file type. Allowed: {", ".join(allowed_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if image_file.size > max_size:
            return Response(
                {'error': f'File too large. Max size: {max_size / 1024 / 1024}MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old image if exists
        if product.image:
            try:
                default_storage.delete(product.image.name)
            except Exception as e:
                logger.warning(f"Failed to delete old image: {str(e)}")
        
        # Save new image
        product.image = image_file
        product.save()
        
        serializer = self.get_serializer(product)
        return Response({
            'message': 'Image uploaded successfully',
            'product': serializer.data
        })
    
    @action(detail=True, methods=['delete'])
    def delete_image(self, request, pk=None):
        """
        Delete product image
        
        DELETE /api/admin/products/{id}/delete_image/
        """
        product = self.get_object()
        
        if not product.image:
            return Response(
                {'error': 'Product has no image'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete image file
        try:
            default_storage.delete(product.image.name)
        except Exception as e:
            logger.warning(f"Failed to delete image file: {str(e)}")
        
        # Clear image field
        product.image = None
        product.save()
        
        return Response({
            'message': 'Image deleted successfully'
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get product statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_products': queryset.count(),
            'active_products': queryset.filter(is_active=True).count(),
            'available_products': queryset.filter(is_available=True).count(),
            'featured_products': queryset.filter(is_featured=True).count(),
            'popular_products': queryset.filter(is_popular=True).count(),
            'products_with_promo': queryset.filter(has_promo=True).count(),
            'low_stock_products': queryset.filter(
                track_stock=True,
                stock_quantity__lte=models.F('low_stock_alert')
            ).count(),
            'total_value': queryset.aggregate(
                total=Sum(models.F('stock_quantity') * models.F('price'))
            )['total'] or 0
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate a product
        
        POST /api/admin/products/{id}/duplicate/
        """
        source_product = self.get_object()
        
        # Create duplicate
        duplicate = Product.objects.create(
            tenant=source_product.tenant,
            category=source_product.category,
            sku=f"{source_product.sku}-copy-{Product.objects.filter(sku__startswith=source_product.sku).count()}",
            name=f"{source_product.name} (Copy)",
            description=source_product.description,
            price=source_product.price,
            cost=source_product.cost,
            track_stock=source_product.track_stock,
            stock_quantity=0,  # Reset stock
            low_stock_alert=source_product.low_stock_alert,
            is_active=False,  # Inactive by default
            is_featured=False,
            is_available=False,
            preparation_time=source_product.preparation_time,
            calories=source_product.calories,
            tags=source_product.tags
        )
        
        # Copy modifiers
        for modifier in source_product.modifiers.all():
            ProductModifier.objects.create(
                product=duplicate,
                name=modifier.name,
                type=modifier.type,
                price_adjustment=modifier.price_adjustment,
                is_active=modifier.is_active,
                sort_order=modifier.sort_order
            )
        
        serializer = self.get_serializer(duplicate)
        return Response({
            'message': 'Product duplicated successfully',
            'product': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update products
        
        POST /api/admin/products/bulk_update/
        Body: {
            "product_ids": [1, 2, 3],
            "updates": {
                "is_active": true,
                "is_available": true,
                ...
            }
        }
        """
        product_ids = request.data.get('product_ids', [])
        updates = request.data.get('updates', {})
        
        if not product_ids:
            return Response(
                {'error': 'No product IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not updates:
            return Response(
                {'error': 'No updates provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate products belong to user
        products = self.get_queryset().filter(id__in=product_ids)
        
        if products.count() != len(product_ids):
            return Response(
                {'error': 'Some products not found or not accessible'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update products
        updated_count = products.update(**updates)
        
        return Response({
            'message': f'{updated_count} products updated successfully',
            'updated_count': updated_count
        })


class ProductModifierAdminSerializer(ProductModifierSerializer):
    """Extended modifier serializer for admin with product info"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    
    class Meta(ProductModifierSerializer.Meta):
        fields = ProductModifierSerializer.Meta.fields + ['product_name', 'product_id']
        read_only_fields = []


class ProductModifierManagementViewSet(viewsets.ModelViewSet):
    """
    Admin API for Product Modifier Management (Toppings & Additions)
    
    Endpoints:
    - GET /api/admin/modifiers/ - List all modifiers
    - POST /api/admin/modifiers/ - Create modifier
    - GET /api/admin/modifiers/{id}/ - Get modifier detail
    - PUT /api/admin/modifiers/{id}/ - Update modifier
    - PATCH /api/admin/modifiers/{id}/ - Partial update
    - DELETE /api/admin/modifiers/{id}/ - Delete modifier
    - GET /api/admin/modifiers/stats/ - Get modifier statistics
    """
    serializer_class = ProductModifierAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTenantOwnerOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_active', 'product']
    search_fields = ['name', 'product__name']
    ordering_fields = ['name', 'type', 'price_adjustment', 'sort_order']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        """
        Filter modifiers based on user role
        - Admin: sees all modifiers
        - Tenant: sees modifiers for their products only
        """
        user = self.request.user
        
        if user.role == 'admin':
            # Admin sees all
            return ProductModifier.objects.select_related('product', 'product__tenant').all()
        elif hasattr(user, 'tenant') and user.tenant:
            # Tenant sees modifiers for their products
            return ProductModifier.objects.filter(
                product__tenant=user.tenant
            ).select_related('product', 'product__tenant')
        else:
            return ProductModifier.objects.none()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get modifier statistics
        
        GET /api/admin/modifiers/stats/
        """
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'inactive': queryset.filter(is_active=False).count(),
            'by_type': {}
        }
        
        # Count by type
        type_counts = queryset.values('type').annotate(count=Count('id'))
        for item in type_counts:
            stats['by_type'][item['type']] = item['count']
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update modifiers
        
        POST /api/admin/modifiers/bulk_update/
        Body: {
            "modifier_ids": [1, 2, 3],
            "updates": {
                "is_active": true,
                ...
            }
        }
        """
        modifier_ids = request.data.get('modifier_ids', [])
        updates = request.data.get('updates', {})
        
        if not modifier_ids:
            return Response(
                {'error': 'No modifier IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not updates:
            return Response(
                {'error': 'No updates provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate modifiers belong to user
        modifiers = self.get_queryset().filter(id__in=modifier_ids)
        
        if modifiers.count() != len(modifier_ids):
            return Response(
                {'error': 'Some modifiers not found or not accessible'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update modifiers
        updated_count = modifiers.update(**updates)
        
        return Response({
            'message': f'{updated_count} modifiers updated successfully',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """
        Get modifiers grouped by product
        
        GET /api/admin/modifiers/by_product/?product_id=1
        """
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'product_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(product_id=product_id)
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data)
