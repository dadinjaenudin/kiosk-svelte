"""
Thread-local storage for tenant context

This module provides thread-local storage for the current tenant and outlet,
allowing middleware to set the context that can be accessed throughout the
request lifecycle without passing it explicitly.
"""
import threading

_thread_locals = threading.local()


def set_current_tenant(tenant):
    """
    Set the current tenant for this thread
    
    Args:
        tenant: Tenant instance or None
    """
    _thread_locals.tenant = tenant


def get_current_tenant():
    """
    Get the current tenant for this thread
    
    Returns:
        Tenant instance or None
    """
    return getattr(_thread_locals, 'tenant', None)


def set_current_outlet(outlet):
    """
    Set the current outlet for this thread
    
    Args:
        outlet: Outlet instance or None
    """
    _thread_locals.outlet = outlet


def get_current_outlet():
    """
    Get the current outlet for this thread
    
    Returns:
        Outlet instance or None
    """
    return getattr(_thread_locals, 'outlet', None)


def set_current_user(user):
    """
    Set the current user for this thread
    
    Args:
        user: User instance or None
    """
    _thread_locals.user = user


def get_current_user():
    """
    Get the current user for this thread
    
    Returns:
        User instance or None
    """
    return getattr(_thread_locals, 'user', None)


def clear_tenant_context():
    """
    Clear the current tenant context
    
    Should be called at the end of each request to prevent memory leaks
    """
    _thread_locals.tenant = None
    _thread_locals.outlet = None
    _thread_locals.user = None
