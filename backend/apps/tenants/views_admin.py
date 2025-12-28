"""
Admin views for Tenant and Outlet Settings Management
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.tenants.models import Tenant, Outlet
from apps.tenants.serializers import (
    TenantSerializer,
    TenantDetailSerializer,
    OutletSerializer,
    OutletDetailSerializer
)
from apps.core.permissions import IsAdminOrTenantOwnerOrManager
from apps.core.context import get_current_tenant


class TenantSettingsViewSet(viewsets.ModelViewSet):
    """
    Admin API for Tenant Settings Management
    
    Endpoints:
    - GET /api/admin/settings/tenant/ - Get tenant settings
    - PUT /api/admin/settings/tenant/{id}/ - Update tenant settings
    - PATCH /api/admin/settings/tenant/{id}/ - Partial update
    - POST /api/admin/settings/tenant/{id}/upload_logo/ - Upload logo
    - DELETE /api/admin/settings/tenant/{id}/delete_logo/ - Delete logo
    """
    
    queryset = Tenant.objects.all()
    serializer_class = TenantDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTenantOwnerOrManager]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_queryset(self):
        """
        Filter tenants based on user permissions
        - Super admin: Can see all tenants
        - Regular admin/owner: Only their tenant
        """
        if self.request.user.is_superuser:
            return Tenant.objects.all()
        
        # Get current tenant from context
        tenant = get_current_tenant()
        if tenant:
            return Tenant.objects.filter(id=tenant.id)
        
        return Tenant.objects.none()
    
    def list(self, request, *args, **kwargs):
        """
        Get current tenant settings
        Returns the tenant for the current user
        """
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'error': 'No tenant found',
                'detail': 'User is not associated with any tenant'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Return the first (should be only one for non-superuser)
        tenant = queryset.first()
        serializer = self.get_serializer(tenant)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Update tenant settings
        Supports both full and partial updates
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Handle logo upload separately if present
        if 'logo' in request.FILES:
            instance.logo = request.FILES['logo']
            instance.save()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_logo(self, request, pk=None):
        """
        Upload tenant logo
        
        POST /api/admin/settings/tenant/{id}/upload_logo/
        
        Request: multipart/form-data with 'logo' file
        """
        tenant = self.get_object()
        
        if 'logo' not in request.FILES:
            return Response({
                'error': 'No logo file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old logo if exists
        if tenant.logo:
            tenant.logo.delete(save=False)
        
        # Save new logo
        tenant.logo = request.FILES['logo']
        tenant.save()
        
        serializer = self.get_serializer(tenant)
        return Response({
            'status': 'success',
            'message': 'Logo uploaded successfully',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['delete'])
    def delete_logo(self, request, pk=None):
        """
        Delete tenant logo
        
        DELETE /api/admin/settings/tenant/{id}/delete_logo/
        """
        tenant = self.get_object()
        
        if not tenant.logo:
            return Response({
                'error': 'No logo to delete'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete logo file
        tenant.logo.delete(save=True)
        
        return Response({
            'status': 'success',
            'message': 'Logo deleted successfully'
        })


class OutletManagementViewSet(viewsets.ModelViewSet):
    """
    Admin API for Outlet Management
    
    Endpoints:
    - GET /api/admin/settings/outlets/ - List outlets
    - POST /api/admin/settings/outlets/ - Create outlet
    - GET /api/admin/settings/outlets/{id}/ - Get outlet detail
    - PUT /api/admin/settings/outlets/{id}/ - Update outlet
    - PATCH /api/admin/settings/outlets/{id}/ - Partial update
    - DELETE /api/admin/settings/outlets/{id}/ - Delete outlet (soft delete)
    - GET /api/admin/settings/outlets/stats/ - Outlet statistics
    """
    
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTenantOwnerOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'city', 'province']
    search_fields = ['name', 'address', 'city', 'phone', 'email']
    ordering_fields = ['name', 'city', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """
        Filter outlets by current tenant
        - Super admin: Can see all outlets
        - Regular admin/owner: Only their tenant's outlets
        """
        if self.request.user.is_superuser:
            return Outlet.objects.all()
        
        # Get current tenant
        tenant = get_current_tenant()
        if tenant:
            return Outlet.objects.filter(tenant=tenant)
        
        return Outlet.objects.none()
    
    def get_serializer_class(self):
        """
        Use detailed serializer for retrieve actions
        """
        if self.action == 'retrieve':
            return OutletDetailSerializer
        return OutletSerializer
    
    def perform_create(self, serializer):
        """
        Auto-set tenant when creating outlet
        """
        tenant = get_current_tenant()
        if tenant:
            serializer.save(tenant=tenant)
        else:
            serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete - set is_active to False instead of deleting
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response({
            'status': 'success',
            'message': 'Outlet deactivated successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get outlet statistics
        
        GET /api/admin/settings/outlets/stats/
        
        Returns:
        - total: Total outlet count
        - active: Active outlet count
        - inactive: Inactive outlet count
        - by_city: Breakdown by city
        - by_province: Breakdown by province
        """
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'inactive': queryset.filter(is_active=False).count(),
            'by_city': {},
            'by_province': {}
        }
        
        # Group by city
        for outlet in queryset:
            city = outlet.city or 'Unknown'
            stats['by_city'][city] = stats['by_city'].get(city, 0) + 1
        
        # Group by province
        for outlet in queryset:
            province = outlet.province or 'Unknown'
            stats['by_province'][province] = stats['by_province'].get(province, 0) + 1
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update outlets
        
        POST /api/admin/settings/outlets/bulk_update/
        
        Request body:
        {
            "outlet_ids": [1, 2, 3],
            "updates": {
                "is_active": true
            }
        }
        """
        outlet_ids = request.data.get('outlet_ids', [])
        updates = request.data.get('updates', {})
        
        if not outlet_ids:
            return Response({
                'error': 'outlet_ids is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not updates:
            return Response({
                'error': 'updates is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter outlets by tenant
        queryset = self.get_queryset()
        outlets = queryset.filter(id__in=outlet_ids)
        
        # Update outlets
        count = outlets.update(**updates)
        
        return Response({
            'status': 'success',
            'message': f'{count} outlets updated successfully',
            'updated_count': count
        })
