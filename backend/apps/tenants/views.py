"""
Views for Tenant API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.tenants.models import Tenant, Outlet
from apps.tenants.serializers import (
    TenantSerializer,
    TenantDetailSerializer,
    OutletSerializer,
    OutletDetailSerializer
)
from apps.core.permissions import has_permission, require_permission
from apps.core.context import get_current_tenant


class PublicTenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public ViewSet for Tenant (Kiosk Mode)
    
    list: List all active tenants
    retrieve: Get tenant details
    outlets: Get outlets for a tenant
    """
    
    queryset = Tenant.objects.filter(is_active=True)
    serializer_class = TenantSerializer
    permission_classes = [AllowAny]  # Public access for kiosk
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve"""
        if self.action == 'retrieve':
            return TenantDetailSerializer
        return TenantSerializer
    
    @action(detail=True, methods=['get'])
    def outlets(self, request, pk=None):
        """
        Get outlets for a specific tenant
        
        GET /api/public/tenants/{id}/outlets/
        """
        tenant = self.get_object()
        outlets = Outlet.objects.filter(tenant=tenant, is_active=True)
        serializer = OutletSerializer(outlets, many=True)
        return Response(serializer.data)


class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Tenant
    
    list: List all tenants (superuser only)
    retrieve: Get tenant details
    me: Get current tenant info
    """
    
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter tenants based on user permissions
        """
        if self.request.user.is_superuser:
            return Tenant.objects.all()
        
        # Regular users can only see their own tenant
        tenant = get_current_tenant()
        if tenant:
            return Tenant.objects.filter(id=tenant.id)
        
        return Tenant.objects.none()
    
    def get_serializer_class(self):
        """
        Use detailed serializer for retrieve actions
        """
        if self.action == 'retrieve' or self.action == 'me':
            return TenantDetailSerializer
        return TenantSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current tenant information
        
        GET /api/tenants/me/
        """
        tenant = get_current_tenant()
        
        if not tenant:
            return Response({
                'error': 'No tenant context',
                'detail': 'Tenant ID not provided in headers'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(tenant)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Update tenant (owner only)
        """
        if not has_permission(request.user, 'tenant.edit'):
            return Response({
                'error': 'Permission denied',
                'detail': 'Only tenant owner can edit tenant settings'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)


class OutletViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Outlet
    
    list: List all outlets for current tenant
    create: Create new outlet
    retrieve: Get outlet details
    update: Update outlet
    delete: Delete outlet
    """
    
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter outlets by current tenant
        """
        tenant = get_current_tenant()
        
        if not tenant:
            return Outlet.objects.none()
        
        return Outlet.objects.filter(tenant=tenant, is_active=True)
    
    def get_serializer_class(self):
        """
        Use detailed serializer for retrieve actions
        """
        if self.action == 'retrieve':
            return OutletDetailSerializer
        return OutletSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create outlet (admin/owner only)
        """
        if not has_permission(request.user, 'outlet.create'):
            return Response({
                'error': 'Permission denied',
                'detail': 'You do not have permission to create outlets'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Auto-set tenant
        tenant = get_current_tenant()
        if tenant:
            request.data['tenant'] = tenant.id
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Update outlet (admin/owner only)
        """
        if not has_permission(request.user, 'outlet.edit'):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete outlet (owner only)
        """
        if not has_permission(request.user, 'outlet.delete'):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Soft delete - set is_active to False
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
