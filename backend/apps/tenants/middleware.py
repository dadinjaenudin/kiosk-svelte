"""
Tenant middleware untuk multi-tenant support
"""
from django.utils.deprecation import MiddlewareMixin

class TenantMiddleware(MiddlewareMixin):
    """
    Middleware untuk set current tenant berdasarkan request
    """
    def process_request(self, request):
        # TODO: Implement tenant detection logic
        # For now, just pass through
        pass
