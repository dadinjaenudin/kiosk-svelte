"""
Custom pagination classes for the API
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with configurable page_size
    Allows large page_size for dropdowns (up to 10000 items)
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 10000
    
    def get_page_size(self, request):
        """
        Override to ensure page_size parameter is respected
        """
        if self.page_size_query_param:
            try:
                page_size = int(request.query_params.get(self.page_size_query_param, self.page_size))
                if page_size > 0:
                    return min(page_size, self.max_page_size)
            except (KeyError, ValueError):
                pass
        return self.page_size
