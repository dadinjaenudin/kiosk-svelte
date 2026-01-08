"""
Views for Store API (Kiosk Multi-Outlet Support)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.tenants.models import Store, Outlet
from apps.tenants.serializers import StoreSerializer, StoreDetailSerializer
from apps.core.permissions import IsManagerOrAbove


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
            serializer = LocationDetailSerializer(location)
            
            return Response({
                'valid': True,
                'location': serializer.data,
                'outlets_count': location.get_active_outlets().count()
            })
        except Location.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Invalid location code'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='by-qr/(?P<qr_code>[^/.]+)')
    def by_qr_code(self, request, qr_code=None):
        """
        Get location by QR code
        
        GET /api/public/locations/by-qr/{qr_code}/
        
        Returns location with all active outlets
        """
        location = get_object_or_404(
            Location, 
            kiosk_qr_code=qr_code, 
            is_active=True
        )
        
        serializer = LocationDetailSerializer(location)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def outlets(self, request, code=None):
        """
        Get outlets for a specific location
        
        GET /api/public/locations/{code}/outlets/
        
        Query params:
            - tenant_id: Filter by tenant
            - is_open: Filter by operating hours (true/false)
        """
        location = self.get_object()
        outlets = location.get_active_outlets()
        
        # Filter by tenant if specified
        tenant_id = request.query_params.get('tenant_id')
        if tenant_id:
            outlets = outlets.filter(tenant_id=tenant_id)
        
        # TODO: Add is_open filter based on current time
        
        data = []
        for outlet in outlets.select_related('tenant'):
            data.append({
                'id': outlet.id,
                'name': outlet.name,
                'slug': outlet.slug,
                'tenant': {
                    'id': outlet.tenant.id,
                    'name': outlet.tenant.name,
                    'logo': outlet.tenant.logo.url if outlet.tenant.logo else None,
                    'primary_color': outlet.tenant.primary_color,
                    'secondary_color': outlet.tenant.secondary_color,
                },
                'address': outlet.address,
                'opening_time': outlet.opening_time,
                'closing_time': outlet.closing_time,
                'is_active': outlet.is_active,
            })
        
        return Response({
            'location': location.code,
            'location_name': location.name,
            'outlets_count': len(data),
            'outlets': data
        })


class LocationAdminViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for Location Management
    
    Full CRUD for locations - filtered by tenant
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    
    def get_queryset(self):
        """Return all locations (multi-tenant physical places)"""
        queryset = super().get_queryset()
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create location (no tenant assignment needed)"""
        serializer.save()
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return LocationDetailSerializer
        return LocationSerializer
    
    @action(detail=True, methods=['post'])
    def regenerate_qr(self, request, pk=None):
        """
        Regenerate QR code for location
        
        POST /api/admin/locations/{id}/regenerate_qr/
        """
        location = self.get_object()
        
        # Generate new QR code
        import uuid
        location.kiosk_qr_code = f"LOC-{uuid.uuid4().hex[:12].upper()}"
        location.save()
        
        serializer = self.get_serializer(location)
        return Response({
            'message': 'QR code regenerated successfully',
            'location': serializer.data
        })
