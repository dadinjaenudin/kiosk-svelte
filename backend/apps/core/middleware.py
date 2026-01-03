"""
Middleware for multi-tenant POS system

Handles tenant context setting and validation.
"""
from apps.core.context import set_current_tenant, clear_current_tenant
from apps.tenants.models import Tenant


class SetTenantContextMiddleware:
    """
    Middleware to automatically set tenant context based on user.
    
    Flow:
    1. Admin/Super Admin: Can access all tenants
       - Can override tenant via query param: ?tenant=<tenant_id>
       - If no param, no tenant filter (shows all)
    
    2. Regular Users: Only access their own tenant
       - Tenant is set from user.tenant
       - Cannot override via query param
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Clear any existing tenant context
        clear_current_tenant()
        
        # Only set tenant for authenticated users
        if request.user and request.user.is_authenticated:
            tenant = self._get_tenant_for_user(request)
            
            if tenant:
                set_current_tenant(tenant)
        
        response = self.get_response(request)
        
        # Clean up tenant context after request
        clear_current_tenant()
        
        return response
    
    def _get_tenant_for_user(self, request):
        """
        Determine which tenant to set for the current user.
        
        Returns:
            Tenant instance or None
        """
        user = request.user
        
        # Admin/Super Admin can access all tenants
        if user.is_superuser or getattr(user, 'role', None) in ['super_admin', 'admin']:
            # Check if tenant is specified in query params
            tenant_id = request.GET.get('tenant')
            
            if tenant_id:
                try:
                    return Tenant.objects.get(id=tenant_id)
                except (Tenant.DoesNotExist, ValueError):
                    # Invalid tenant ID, return None (show all)
                    return None
            
            # No tenant param, return None (admin sees all tenants)
            return None
        
        # Regular users - use their assigned tenant
        user_tenant = getattr(user, 'tenant', None)
        
        return user_tenant


class SetOutletContextMiddleware:
    """
    Middleware to automatically set outlet context for multi-outlet support.
    
    Flow:
    1. Admin/Super Admin/Tenant Owner: Can access all outlets in tenant
       - Can override outlet via query param: ?outlet=<outlet_id>
       - Or use session-stored outlet
       - Or use user's primary outlet
    
    2. Managers: Can access their accessible_outlets
       - Can switch between accessible outlets
       - Outlet stored in session
    
    3. Cashier/Kitchen: Only access their assigned outlet
       - Outlet is set from user.outlet
       - Cannot override
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        from apps.core.context import set_current_outlet, get_current_outlet
        
        # Only set outlet for authenticated users
        if request.user and request.user.is_authenticated:
            outlet = self._get_outlet_for_user(request)
            
            if outlet:
                set_current_outlet(outlet)
                # Store in session for persistence
                request.session['current_outlet_id'] = outlet.id
        
        response = self.get_response(request)
        
        return response
    
    def _get_outlet_for_user(self, request):
        """
        Determine which outlet to set for the current user.
        
        Priority:
        1. Query parameter ?outlet=<id> (if user has permission)
        2. Session stored outlet
        3. User's primary outlet (user.outlet)
        4. First accessible outlet
        
        Returns:
            Outlet instance or None
        """
        from apps.tenants.models import Outlet
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # High-privilege roles can switch outlets freely
        can_switch_outlets = user_role in ['super_admin', 'admin', 'tenant_owner', 'manager']
        
        # 1. Check query parameter (highest priority for switching)
        outlet_id = request.GET.get('outlet')
        if outlet_id and can_switch_outlets:
            try:
                outlet = Outlet.objects.get(id=outlet_id)
                # Verify access
                if self._user_can_access_outlet(user, outlet):
                    return outlet
            except (Outlet.DoesNotExist, ValueError):
                pass
        
        # 2. Check session-stored outlet
        session_outlet_id = request.session.get('current_outlet_id')
        if session_outlet_id:
            try:
                outlet = Outlet.objects.get(id=session_outlet_id)
                if self._user_can_access_outlet(user, outlet):
                    return outlet
            except Outlet.DoesNotExist:
                # Outlet deleted, clear session
                request.session.pop('current_outlet_id', None)
        
        # 3. Use user's primary outlet
        user_outlet = getattr(user, 'outlet', None)
        if user_outlet:
            return user_outlet
        
        # 4. For managers, use first accessible outlet
        if user_role == 'manager':
            accessible_outlets = user.accessible_outlets.filter(is_active=True).first()
            if accessible_outlets:
                return accessible_outlets
        
        # 5. For tenant_owner, use first outlet in their tenant
        if user_role == 'tenant_owner' and user.tenant:
            first_outlet = user.tenant.outlets.filter(is_active=True).first()
            if first_outlet:
                return first_outlet
        
        return None
    
    def _user_can_access_outlet(self, user, outlet):
        """
        Check if user has permission to access this outlet.
        
        Returns:
            bool
        """
        user_role = getattr(user, 'role', None)
        user_tenant = getattr(user, 'tenant', None)
        
        # Super admin and admin can access all outlets
        if user_role in ['super_admin', 'admin']:
            return True
        
        # Outlet must belong to user's tenant
        if user_tenant and outlet.tenant_id != user_tenant.id:
            return False
        
        # Tenant owner can access all outlets in their tenant
        if user_role == 'tenant_owner':
            return True
        
        # Manager can access outlets in accessible_outlets
        if user_role == 'manager':
            return user.accessible_outlets.filter(id=outlet.id).exists()
        
        # Cashier/Kitchen can only access their assigned outlet
        user_outlet = getattr(user, 'outlet', None)
        if user_outlet:
            return user_outlet.id == outlet.id
        
        return False
