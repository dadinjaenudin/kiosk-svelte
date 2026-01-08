"""
Views for Store API (Kiosk Multi-Outlet Support)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.tenants.models import Store, Outlet, StoreOutlet
from apps.tenants.serializers import StoreSerializer, StoreDetailSerializer
from apps.core.permissions import IsManagerOrAbove
import uuid


class PublicStoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public ViewSet for Store (Kiosk Mode)
    
    list: List all active stores
    retrieve: Get store details with outlets
    validate_code: Validate store code for kiosk setup
    by_qr_code: Get store by QR code
    """
    
    queryset = Store.objects.filter(is_active=True).select_related('tenant')
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]  # Public access for kiosk
    lookup_field = 'code'  # Use code instead of ID
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve"""
        if self.action == 'retrieve':
            return StoreDetailSerializer
        return StoreSerializer
    
    @action(detail=True, methods=['get'], url_path='validate')
    def validate_code(self, request, code=None):
        """
        Validate store code for kiosk setup
        
        GET /api/public/stores/{code}/validate/
        
        Returns:
            {
                "valid": true,
                "store": {...},
                "outlets_count": 3
            }
        """
        try:
            store = self.get_object()
            serializer = StoreDetailSerializer(store)
            
            # OPSI 2: Count via StoreOutlet junction
            outlets_count = store.store_outlets.filter(
                is_active=True,
                outlet__is_active=True
            ).count()
            
            return Response({
                'valid': True,
                'store': serializer.data,
                'outlets_count': outlets_count
            })
        except Store.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Invalid store code'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='by-qr/(?P<qr_code>[^/.]+)')
    def by_qr_code(self, request, qr_code=None):
        """
        Get store by QR code
        
        GET /api/public/stores/by-qr/{qr_code}/
        
        Returns store with all active outlets
        """
        store = get_object_or_404(
            Store, 
            kiosk_qr_code=qr_code, 
            is_active=True
        )
        
        serializer = StoreDetailSerializer(store)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def outlets(self, request, code=None):
        """
        Get outlets for a specific store
        
        GET /api/public/stores/{code}/outlets/
        
        Query params:
            - is_open: Filter by operating hours (true/false)
        """
        store = self.get_object()
        
        # OPSI 2: Query via StoreOutlet junction
        store_outlets = store.store_outlets.filter(
            is_active=True,
            outlet__is_active=True
        ).select_related('outlet', 'outlet__tenant').order_by('display_order', 'outlet__brand_name')
        
        # TODO: Add is_open filter based on current time
        
        data = []
        for so in store_outlets:
            outlet = so.outlet
            # Use custom times from StoreOutlet if set, otherwise use Store's times
            opening_time = so.custom_opening_time if so.custom_opening_time else store.opening_time
            closing_time = so.custom_closing_time if so.custom_closing_time else store.closing_time
            
            data.append({
                'id': outlet.id,
                'brand_name': outlet.brand_name,
                'name': outlet.name,
                'slug': outlet.slug,
                'tenant': {
                    'id': outlet.tenant.id,
                    'name': outlet.tenant.name,
                    'logo': outlet.tenant.logo.url if outlet.tenant.logo else None,
                    'primary_color': outlet.tenant.primary_color,
                    'secondary_color': outlet.tenant.secondary_color,
                },
                'opening_time': str(opening_time) if opening_time else None,
                'closing_time': str(closing_time) if closing_time else None,
                'is_active': so.is_active,
                'display_order': so.display_order,
            })
        
        return Response({
            'store': store.code,
            'store_name': store.name,
            'tenant_name': store.tenant.name,
            'outlets_count': len(data),
            'outlets': data
        })
    
    @action(detail=True, methods=['get'])
    def products(self, request, code=None):
        """
        Get all products available at a specific store (across all brands)
        
        GET /api/public/stores/{code}/products/
        
        Query params:
            - brand: Filter by brand (outlet slug)
            - category: Filter by category ID
            - search: Search product name
            - is_featured: Filter featured products
            - is_popular: Filter popular products
        
        Returns all products from all outlets/brands operating at this store.
        This is for the main product browsing page in kiosk.
        """
        from apps.products.models import Product
        from apps.products.serializers import ProductSerializer
        
        store = self.get_object()
        
        # Get all active outlets at this store via StoreOutlet
        outlet_ids = store.store_outlets.filter(
            is_active=True,
            outlet__is_active=True
        ).values_list('outlet_id', flat=True)
        
        # Get all products from these outlets (use all_objects to bypass tenant filtering)
        products = Product.all_objects.filter(
            outlet_id__in=outlet_ids,
            is_available=True
        ).select_related('outlet', 'outlet__tenant', 'category')
        
        # Apply filters
        brand_slug = request.query_params.get('brand')
        if brand_slug:
            products = products.filter(outlet__slug=brand_slug)
        
        category_id = request.query_params.get('category')
        if category_id:
            products = products.filter(category_id=category_id)
        
        search = request.query_params.get('search')
        if search:
            products = products.filter(name__icontains=search)
        
        is_featured = request.query_params.get('is_featured')
        if is_featured == 'true':
            products = products.filter(is_featured=True)
        
        is_popular = request.query_params.get('is_popular')
        if is_popular == 'true':
            products = products.filter(is_popular=True)
        
        # Serialize products
        serializer = ProductSerializer(products, many=True, context={'request': request})
        
        return Response({
            'store': store.code,
            'store_name': store.name,
            'products_count': products.count(),
            'products': serializer.data
        })


class StoreAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for Store Management
    
    Full CRUD for stores - filtered by tenant
    """
    queryset = Store.objects.all().select_related('tenant')
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    
    def get_queryset(self):
        """Return stores for current tenant"""
        queryset = super().get_queryset()
        
        # Get tenant from request
        tenant_id = getattr(self.request, 'tenant_id', None)
        
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create store with auto-assign tenant"""
        tenant_id = getattr(self.request, 'tenant_id', None)
        
        if tenant_id and not serializer.validated_data.get('tenant_id'):
            serializer.save(tenant_id=tenant_id)
        else:
            serializer.save()
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return StoreDetailSerializer
        return StoreSerializer
    
    @action(detail=True, methods=['post'])
    def regenerate_qr(self, request, pk=None):
        """
        Regenerate QR code for store
        
        POST /api/admin/stores/{id}/regenerate_qr/
        """
        store = self.get_object()
        
        # Generate new QR code
        store.kiosk_qr_code = f"STORE-{uuid.uuid4().hex[:12].upper()}"
        store.save()
        
        serializer = self.get_serializer(store)
        return Response({
            'message': 'QR code regenerated successfully',
            'store': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def outlets(self, request, pk=None):
        """
        Get outlets assigned to this store
        
        GET /api/admin/stores/{id}/outlets/
        """
        store = self.get_object()
        store_outlets = StoreOutlet.objects.filter(store=store, is_active=True).select_related('outlet')
        
        outlets_data = []
        for so in store_outlets:
            outlet_data = {
                'id': so.outlet.id,
                'name': so.outlet.name,
                'brand_name': so.outlet.brand_name,
                'phone': so.outlet.phone,
                'email': so.outlet.email,
                'is_active': so.outlet.is_active,
                'store_outlet_id': so.id,
                'custom_opening_time': so.custom_opening_time,
                'custom_closing_time': so.custom_closing_time,
            }
            outlets_data.append(outlet_data)
        
        return Response(outlets_data)
    
    @action(detail=True, methods=['post'])
    def add_outlet(self, request, pk=None):
        """
        Add outlet to store
        
        POST /api/admin/stores/{id}/add_outlet/
        Body: {"outlet": outlet_id}
        """
        store = self.get_object()
        outlet_id = request.data.get('outlet')
        
        if not outlet_id:
            return Response({'error': 'outlet is required'}, status=400)
        
        try:
            outlet = Outlet.objects.get(id=outlet_id)
        except Outlet.DoesNotExist:
            return Response({'error': 'Outlet not found'}, status=404)
        
        # Check if already assigned
        if StoreOutlet.objects.filter(store=store, outlet=outlet).exists():
            return Response({'error': 'Outlet already assigned to this store'}, status=400)
        
        # Create relationship
        store_outlet = StoreOutlet.objects.create(
            store=store,
            outlet=outlet,
            is_active=True
        )
        
        return Response({
            'message': f'Outlet {outlet.name} added to store {store.name}',
            'store_outlet_id': store_outlet.id
        })
    
    @action(detail=True, methods=['post'])
    def remove_outlet(self, request, pk=None):
        """
        Remove outlet from store
        
        POST /api/admin/stores/{id}/remove_outlet/
        Body: {"outlet": outlet_id}
        """
        store = self.get_object()
        outlet_id = request.data.get('outlet')
        
        if not outlet_id:
            return Response({'error': 'outlet is required'}, status=400)
        
        try:
            store_outlet = StoreOutlet.objects.get(store=store, outlet_id=outlet_id)
            store_outlet.delete()  # Hard delete or soft: store_outlet.is_active = False; store_outlet.save()
            
            return Response({
                'message': f'Outlet removed from store {store.name}'
            })
        except StoreOutlet.DoesNotExist:
            return Response({'error': 'Outlet not assigned to this store'}, status=404)
