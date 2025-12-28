"""
Tenant Middleware

Extracts tenant and outlet information from request headers and
sets them in thread-local storage for use throughout the request.

Headers:
    X-Tenant-ID: Tenant ID
    X-Outlet-ID: Outlet ID (optional)
"""
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from apps.tenants.models import Tenant, Outlet
from apps.core.context import (
    set_current_tenant,
    set_current_outlet,
    set_current_user,
    clear_tenant_context
)

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to extract and set tenant context from request headers
    """
    
    # URLs that don't require tenant context
    EXCLUDE_URLS = [
        '/api/auth/login/',
        '/api/auth/register/',
        '/api/auth/refresh/',
        '/api/health/',
        '/api/public/',  # Public kiosk endpoints (tenants, etc)
        '/api/products/',  # Public kiosk API - browse all products
        '/api/orders/',  # Public order API - multi-tenant checkout
        '/api/admin/',  # Admin panel API endpoints
        '/api/promotions/',  # Promotion management (admin access)
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """
        Extract tenant from headers and set in thread-local storage
        """
        # Clear any existing context
        clear_tenant_context()
        
        # Check if URL should be excluded
        path = request.path
        if any(path.startswith(url) for url in self.EXCLUDE_URLS):
            return None
        
        # Get tenant ID from header
        tenant_id = request.headers.get('X-Tenant-ID')
        
        # If authenticated user, get tenant from user
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
            
            # Super admins don't need tenant context
            if request.user.role == 'admin':
                logger.debug(f"Super admin user: {request.user.username} - tenant not required")
                return None
            
            # Use user's tenant if header not provided
            if not tenant_id and hasattr(request.user, 'tenant_id'):
                tenant_id = request.user.tenant_id
        
        # If no tenant ID, return error for non-excluded URLs
        if not tenant_id:
            logger.warning(f"No tenant ID provided for {path}")
            return JsonResponse({
                'error': 'Tenant ID required',
                'detail': 'X-Tenant-ID header is missing'
            }, status=400)
        
        # Get tenant from database
        try:
            tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            set_current_tenant(tenant)
            request.tenant = tenant  # Also set on request for convenience
            
            logger.debug(f"Tenant set: {tenant.name} (ID: {tenant.id})")
        except Tenant.DoesNotExist:
            logger.error(f"Tenant not found: {tenant_id}")
            return JsonResponse({
                'error': 'Tenant not found',
                'detail': f'Tenant with ID {tenant_id} does not exist or is inactive'
            }, status=404)
        
        # Get outlet ID from header (optional)
        outlet_id = request.headers.get('X-Outlet-ID')
        
        if outlet_id:
            try:
                outlet = Outlet.objects.get(
                    id=outlet_id,
                    tenant=tenant,
                    is_active=True
                )
                set_current_outlet(outlet)
                request.outlet = outlet
                
                logger.debug(f"Outlet set: {outlet.name} (ID: {outlet.id})")
            except Outlet.DoesNotExist:
                logger.warning(f"Outlet not found: {outlet_id} for tenant {tenant_id}")
                # Don't fail if outlet not found, just log warning
                request.outlet = None
        
        return None
    
    def process_response(self, request, response):
        """
        Clear tenant context after request is processed
        """
        clear_tenant_context()
        return response
    
    def process_exception(self, request, exception):
        """
        Clear tenant context if exception occurs
        """
        clear_tenant_context()
        return None
