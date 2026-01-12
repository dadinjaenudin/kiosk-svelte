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
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from apps.tenants.models import Tenant, Outlet
from apps.core.context import (
    set_current_tenant,
    set_current_outlet,
    set_current_user,
    clear_tenant_context
)

logger = logging.getLogger(__name__)
User = get_user_model()


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
        '/api/tenants/public/',  # Public tenant/store endpoints for kiosk
        '/api/admin/tenants/',  # Admin tenant management (superuser only)
        '/api/admin/settings/',  # Admin settings management (admin access)
        '/api/admin/users/',  # User management (admin access)
        '/api/products/',  # Public kiosk API - browse all products
        '/api/product-selector/',  # Product selector for promotions (admin access)
        '/api/categories/',  # Public categories API
        '/api/orders/',  # Public order API - multi-tenant checkout
        '/api/promotions/',  # Promotion management (admin access)
        '/api/outlets/accessible/',  # Get accessible outlets for current user
        '/api/outlets/all_outlets/',  # Get all outlets for admin forms
        '/api/kitchen/',  # Kitchen display system (multi-tenant, outlet-based filtering)
        '/api/kitchen-station-types/',  # Kitchen station types management (admin access)
        '/api/kitchen-stations/',  # Kitchen stations management (admin access)
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
        
        # Try to get user from token if not already authenticated
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        else:
            # Try to get user from Authorization header (for DRF Token auth)
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Token '):
                token_key = auth_header.split(' ')[1]
                try:
                    token = Token.objects.select_related('user').get(key=token_key)
                    user = token.user
                    request.user = user  # Set user on request
                    logger.debug(f"User authenticated from token: {user.username}")
                except Token.DoesNotExist:
                    logger.warning(f"Invalid token: {token_key[:10]}...")
        
        # If authenticated user, get tenant from user
        if user:
            set_current_user(user)
            logger.debug(f"Authenticated user: {user.username}, role: {user.role}, is_superuser: {user.is_superuser}")
            
            # Super admin can bypass tenant requirement
            if user.is_superuser or user.role in ['super_admin', 'admin']:
                logger.debug(f"Super admin bypass granted for: {user.username}")
                return None
            
            # Use user's tenant if header not provided
            if not tenant_id and hasattr(user, 'tenant_id') and user.tenant_id:
                tenant_id = user.tenant_id
                logger.debug(f"Using tenant from user: {user.username} -> tenant_id: {tenant_id}")
        else:
            logger.debug(f"No authenticated user found for request to {path}")
        
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
