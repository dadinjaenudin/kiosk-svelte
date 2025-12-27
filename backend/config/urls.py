"""
URL configuration for POS F&B System
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({'status': 'ok', 'service': 'POS Backend'})


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT
    path('api/auth/', include('apps.users.auth_urls')),  # Admin panel auth (Token-based)
    
    # App APIs
    path('api/', include('apps.tenants.urls')),  # Tenant & Outlet management
    path('api/', include('apps.users.urls')),    # User management
    path('api/products/', include('apps.products.urls')),
    path('api/', include('apps.orders.urls')),  # Order & Checkout
    path('api/', include('apps.promotions.urls')),  # Promotion management
    # path('api/payments/', include('apps.payments.urls')),
    # path('api/kitchen/', include('apps.kitchen.urls')),
    
    # Health check
    path('api/health/', health_check, name='health_check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
