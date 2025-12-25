"""
Permission system for multi-tenant POS

Provides role-based and custom permission checking for users.
"""
from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied


# Permission definitions by role
ROLE_PERMISSIONS = {
    'owner': [
        # Full access - all permissions
        'tenant.edit',
        'tenant.delete',
        'outlet.create',
        'outlet.edit',
        'outlet.delete',
        'user.create',
        'user.edit',
        'user.delete',
        'product.create',
        'product.edit',
        'product.delete',
        'category.create',
        'category.edit',
        'category.delete',
        'order.create',
        'order.edit',
        'order.delete',
        'order.view_all',
        'payment.process',
        'payment.refund',
        'payment.view_all',
        'report.view_all',
        'report.export',
        'inventory.manage',
    ],
    'admin': [
        'outlet.create',
        'outlet.edit',
        'user.create',
        'user.edit',
        'product.create',
        'product.edit',
        'product.delete',
        'category.create',
        'category.edit',
        'category.delete',
        'order.create',
        'order.edit',
        'order.view_all',
        'payment.process',
        'payment.view_all',
        'report.view_all',
        'report.export',
        'inventory.manage',
    ],
    'manager': [
        'user.view',
        'product.create',
        'product.edit',
        'category.create',
        'category.edit',
        'order.view_all',
        'order.edit',
        'report.view',
        'inventory.manage',
    ],
    'cashier': [
        'order.create',
        'order.view',
        'order.edit',
        'payment.process',
        'report.view_own',
    ],
    'kitchen': [
        'order.view_kitchen',
        'order.update_status',
    ],
    'waiter': [
        'order.create',
        'order.view',
        'order.edit',
    ],
}


def has_permission(user, permission):
    """
    Check if user has a specific permission
    
    Args:
        user: User instance
        permission: Permission string (e.g., 'product.create')
    
    Returns:
        bool: True if user has permission
    """
    # Superuser has all permissions
    if user.is_superuser:
        return True
    
    # Check if user is authenticated
    if not user.is_authenticated:
        return False
    
    # Get role permissions
    role = getattr(user, 'role', None)
    if not role:
        return False
    
    role_perms = ROLE_PERMISSIONS.get(role, [])
    
    # Check custom permissions
    custom_perms = getattr(user, 'permissions', [])
    if isinstance(custom_perms, str):
        import json
        try:
            custom_perms = json.loads(custom_perms)
        except:
            custom_perms = []
    
    all_perms = role_perms + custom_perms
    
    return permission in all_perms


def has_role(user, role):
    """
    Check if user has a specific role
    
    Args:
        user: User instance
        role: Role string (e.g., 'admin')
    
    Returns:
        bool: True if user has role
    """
    if user.is_superuser:
        return True
    
    return getattr(user, 'role', None) == role


def require_permission(permission):
    """
    Decorator to require specific permission for a view
    
    Usage:
        @require_permission('product.create')
        def create_product(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required',
                    'detail': 'You must be logged in to access this resource'
                }, status=401)
            
            if not has_permission(request.user, permission):
                return JsonResponse({
                    'error': 'Permission denied',
                    'detail': f'You do not have permission: {permission}'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


def require_role(role):
    """
    Decorator to require specific role for a view
    
    Usage:
        @require_role('admin')
        def admin_view(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required'
                }, status=401)
            
            if not has_role(request.user, role):
                return JsonResponse({
                    'error': 'Permission denied',
                    'detail': f'Requires role: {role}'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


class PermissionMixin:
    """
    Mixin for DRF views to check permissions
    """
    
    required_permission = None
    required_role = None
    
    def check_permissions(self, request):
        """
        Override to add custom permission checks
        """
        super().check_permissions(request)
        
        # Check required permission
        if self.required_permission:
            if not has_permission(request.user, self.required_permission):
                raise PermissionDenied(
                    f'Permission required: {self.required_permission}'
                )
        
        # Check required role
        if self.required_role:
            if not has_role(request.user, self.required_role):
                raise PermissionDenied(
                    f'Role required: {self.required_role}'
                )


def get_user_permissions(user):
    """
    Get all permissions for a user
    
    Returns:
        list: List of permission strings
    """
    if user.is_superuser:
        # Return all permissions
        all_perms = []
        for perms in ROLE_PERMISSIONS.values():
            all_perms.extend(perms)
        return list(set(all_perms))
    
    role = getattr(user, 'role', None)
    role_perms = ROLE_PERMISSIONS.get(role, [])
    
    # Add custom permissions
    custom_perms = getattr(user, 'permissions', [])
    if isinstance(custom_perms, str):
        import json
        try:
            custom_perms = json.loads(custom_perms)
        except:
            custom_perms = []
    
    return list(set(role_perms + custom_perms))
