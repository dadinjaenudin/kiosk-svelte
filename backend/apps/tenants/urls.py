"""
URL routing for Tenant API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tenants import views

# Public router for kiosk
public_router = DefaultRouter()
public_router.register(r'tenants', views.PublicTenantViewSet, basename='public-tenant')

# Authenticated router
router = DefaultRouter()
router.register(r'tenants', views.TenantViewSet, basename='tenant')
router.register(r'outlets', views.OutletViewSet, basename='outlet')

urlpatterns = [
    path('public/', include(public_router.urls)),  # Public kiosk endpoints
    path('', include(router.urls)),  # Authenticated endpoints
]
