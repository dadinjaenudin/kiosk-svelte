"""
Views for Tenant API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.tenants.models import Tenant, Outlet, KitchenStation, KitchenStationType
from apps.tenants.serializers import (
    TenantSerializer,
    TenantDetailSerializer,
    OutletSerializer,
    OutletDetailSerializer,
    KitchenStationSerializer,
    KitchenStationTypeSerializer
)
from apps.core.context import get_current_tenant
from apps.core.permissions import (
    CanManageTenants,
    IsManagerOrAbove,
    is_admin_user
)


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


class PublicOutletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public ViewSet for Outlets (Kiosk Mode)
    
    list: List all active outlets (optionally filter by tenant_id)
    retrieve: Get outlet details
    """
    
    queryset = Outlet.objects.filter(is_active=True).select_related('tenant')
    serializer_class = OutletSerializer
    permission_classes = [AllowAny]  # Public access for kiosk
    
    def get_queryset(self):
        """
        Optionally filter by tenant_id query parameter
        
        GET /api/public/outlets/
        GET /api/public/outlets/?tenant_id=67
        """
        queryset = super().get_queryset()
        
        # Filter by tenant if provided
        tenant_id = self.request.query_params.get('tenant_id', None)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset.order_by('tenant__name', 'name')


class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Tenant
    
    list: List all tenants (superuser only)
    retrieve: Get tenant details
    me: Get current tenant info
    """
    
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, CanManageTenants]
    
    def get_queryset(self):
        """
        Filter tenants based on user permissions.
        Admin can see all, others see only their own.
        """
        user = self.request.user
        
        if is_admin_user(user):
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
    ViewSet for Outlet Management (Multi-outlet support)
    
    list: List outlets for current tenant (filtered by user access)
    create: Create new outlet (tenant_owner only)
    retrieve: Get outlet details
    update: Update outlet (tenant_owner only)
    delete: Soft delete outlet (tenant_owner only)
    accessible: Get outlets accessible to current user
    set_current: Set current outlet context
    """
    
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAbove]
    
    def get_queryset(self):
        """
        Filter outlets by current tenant and user access
        """
        user = self.request.user
        tenant = get_current_tenant()
        
        if not tenant:
            return Outlet.objects.none()
        
        # Admin/Super Admin: See all outlets in tenant
        if is_admin_user(user):
            return Outlet.objects.filter(tenant=tenant, is_active=True)
        
        # Tenant Owner: See all outlets in their tenant
        if user.role == 'tenant_owner':
            return Outlet.objects.filter(tenant=tenant, is_active=True)
        
        # Manager: See accessible outlets
        if user.role == 'manager':
            return user.accessible_outlets.filter(tenant=tenant, is_active=True)
        
        # Cashier/Kitchen: See only their assigned outlet
        if user.outlet:
            return Outlet.objects.filter(id=user.outlet.id, is_active=True)
        
        return Outlet.objects.none()
    
    def get_serializer_class(self):
        """
        Use detailed serializer for retrieve actions
        """
        if self.action == 'retrieve':
            return OutletDetailSerializer
        return OutletSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def all_outlets(self, request):
        """
        Get all outlets (for admin/superadmin use in forms)
        
        GET /api/outlets/all_outlets/
        
        Returns ALL outlets across all tenants for admin use
        (e.g., in user management forms to assign outlets)
        """
        user = request.user
        
        # Only allow admin/superadmin to see all outlets
        if not is_admin_user(user):
            return Response({
                'error': 'Only admins can view all outlets'
            }, status=403)
        
        # Get all active outlets across all tenants
        outlets = Outlet.objects.filter(is_active=True).select_related('tenant').order_by('tenant__name', 'name')
        serializer = self.get_serializer(outlets, many=True)
        
        return Response({
            'results': serializer.data,
            'count': outlets.count()
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def accessible(self, request):
        """
        Get outlets accessible to current user
        
        GET /api/outlets/accessible/
        
        Returns list of outlets the user can access based on their role:
        - super_admin/admin: All outlets
        - tenant_owner: All outlets in their tenant
        - manager: Their accessible_outlets
        - cashier/kitchen: Their assigned outlet only
        """
        user = request.user
        tenant = get_current_tenant()
        
        outlets = self.get_queryset()
        serializer = self.get_serializer(outlets, many=True)
        
        return Response({
            'outlets': serializer.data,
            'count': outlets.count(),
            'user_role': user.role,
            'current_tenant': tenant.name if tenant else None
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_current(self, request, pk=None):
        """
        Set current outlet context for user
        
        POST /api/outlets/{id}/set_current/
        
        Sets the outlet in session for subsequent requests.
        User must have access to the outlet.
        """
        from apps.core.context import set_current_outlet
        
        outlet = self.get_object()
        user = request.user
        
        # Verify user can access this outlet
        accessible_outlets = self.get_queryset()
        if not accessible_outlets.filter(id=outlet.id).exists():
            return Response({
                'error': 'Access denied',
                'detail': 'You do not have access to this outlet'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Set in context and session
        set_current_outlet(outlet)
        request.session['current_outlet_id'] = outlet.id
        
        return Response({
            'success': True,
            'message': f'Current outlet set to {outlet.name}',
            'outlet': self.get_serializer(outlet).data
        })
    
    def create(self, request, *args, **kwargs):
        """
        Create outlet (tenant_owner only)
        """
        # Only tenant_owner can create outlets
        if request.user.role not in ['super_admin', 'admin', 'tenant_owner']:
            return Response({
                'error': 'Permission denied',
                'detail': 'Only tenant owners can create outlets'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Auto-set tenant
        tenant = get_current_tenant()
        if tenant:
            request.data['tenant'] = tenant.id
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Update outlet (tenant_owner only)
        """
        if request.user.role not in ['super_admin', 'admin', 'tenant_owner']:
            return Response({
                'error': 'Permission denied',
                'detail': 'Only tenant owners can update outlets'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete outlet (tenant_owner only) - Soft delete
        """
        if request.user.role not in ['super_admin', 'admin', 'tenant_owner']:
            return Response({
                'error': 'Permission denied',
                'detail': 'Only tenant owners can delete outlets'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Soft delete - set is_active to False
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response({
            'success': True,
            'message': f'Outlet {instance.name} has been deactivated'
        }, status=status.HTTP_200_OK)


class KitchenStationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for KitchenStation management
    
    list: Get all kitchen stations (filtered by outlet if provided)
    retrieve: Get specific kitchen station
    create: Create new kitchen station
    update: Update kitchen station
    destroy: Delete kitchen station
    """
    serializer_class = KitchenStationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter stations by outlet or accessible outlets for user
        """
        queryset = KitchenStation.objects.select_related('outlet')
        
        # Filter by outlet if provided in query params
        outlet_id = self.request.query_params.get('outlet')
        if outlet_id:
            queryset = queryset.filter(outlet_id=outlet_id)
        else:
            # Filter by user's accessible outlets
            user = self.request.user
            if user.role in ['super_admin', 'admin']:
                # Admin can see all stations
                pass
            elif user.role in ['tenant_owner', 'manager']:
                # Tenant owner/manager can see their tenant's stations
                tenant = get_current_tenant()
                if tenant:
                    queryset = queryset.filter(outlet__tenant=tenant)
            else:
                # Other roles see only their outlet's stations
                if hasattr(user, 'outlet') and user.outlet:
                    queryset = queryset.filter(outlet=user.outlet)
        
        return queryset.filter(is_active=True).order_by('outlet', 'sort_order', 'name')
    
    def perform_create(self, serializer):
        """Create kitchen station with validation"""
        serializer.save()
    
    def perform_update(self, serializer):
        """Update kitchen station"""
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete kitchen station"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response({
            'success': True,
            'message': f'Kitchen station {instance.name} has been deactivated'
        }, status=status.HTTP_200_OK)


class KitchenStationTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for KitchenStationType management
    
    list: Get all kitchen station types (global + tenant-specific)
    retrieve: Get specific kitchen station type
    create: Create new kitchen station type
    update: Update kitchen station type
    destroy: Delete kitchen station type
    """
    serializer_class = KitchenStationTypeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return global types + tenant-specific types for current tenant
        """
        user = self.request.user
        
        # Start with all global types
        queryset = KitchenStationType.objects.filter(is_global=True)
        
        # Add tenant-specific types
        tenant_id = self.request.query_params.get('tenant')
        if tenant_id:
            # Filter by specific tenant (for admin)
            tenant_types = KitchenStationType.objects.filter(tenant_id=tenant_id, is_global=False)
        else:
            # Get current tenant's types
            tenant = get_current_tenant()
            if tenant:
                tenant_types = KitchenStationType.objects.filter(tenant=tenant, is_global=False)
            else:
                tenant_types = KitchenStationType.objects.none()
        
        # Combine querysets
        queryset = queryset | tenant_types
        
        # Allow admin to see all types
        if is_admin_user(user):
            queryset = KitchenStationType.objects.all()
        
        return queryset.order_by('sort_order', 'name')
    
    def perform_create(self, serializer):
        """Create kitchen station type"""
        # If not global and no tenant specified, use current tenant
        if not serializer.validated_data.get('is_global') and not serializer.validated_data.get('tenant'):
            tenant = get_current_tenant()
            if tenant:
                serializer.save(tenant=tenant)
            else:
                serializer.save()
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Update kitchen station type"""
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """Hard delete kitchen station type (only if not in use)"""
        instance = self.get_object()
        
        # Check if type is used in any categories
        from apps.products.models import Category
        categories_using = Category.objects.filter(kitchen_station_code=instance.code)
        
        if categories_using.exists():
            return Response({
                'success': False,
                'error': f'Cannot delete station type "{instance.name}" - it is used by {categories_using.count()} categories'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if type is used in any product overrides
        from apps.products.models import Product
        products_using = Product.objects.filter(kitchen_station_code_override=instance.code)
        
        if products_using.exists():
            return Response({
                'success': False,
                'error': f'Cannot delete station type "{instance.name}" - it is used by {products_using.count()} products as override'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Safe to delete
        instance.delete()
        
        return Response({
            'success': True,
            'message': f'Kitchen station type {instance.name} has been deleted'
        }, status=status.HTTP_200_OK)

