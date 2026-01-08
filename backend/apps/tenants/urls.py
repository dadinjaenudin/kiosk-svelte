"""
URL routing for Tenant API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tenants import views
from apps.tenants.views_admin import TenantManagementViewSet, TenantSettingsViewSet, OutletManagementViewSet
from apps.tenants.views_store import PublicStoreViewSet, StoreAdminViewSet

# Public router for kiosk
public_router = DefaultRouter()
public_router.register(r'tenants', views.PublicTenantViewSet, basename='public-tenant')
public_router.register(r'outlets', views.PublicOutletViewSet, basename='public-outlet')
public_router.register(r'stores', PublicStoreViewSet, basename='public-store')

# Authenticated router
router = DefaultRouter()
router.register(r'tenants', views.TenantViewSet, basename='tenant')
router.register(r'outlets', views.OutletViewSet, basename='outlet')
router.register(r'kitchen-stations', views.KitchenStationViewSet, basename='kitchen-station')
router.register(r'kitchen-station-types', views.KitchenStationTypeViewSet, basename='kitchen-station-type')

# Admin router for settings
admin_router = DefaultRouter()
admin_router.register(r'tenants', TenantManagementViewSet, basename='admin-tenants')
admin_router.register(r'settings/tenant', TenantSettingsViewSet, basename='admin-tenant-settings')
admin_router.register(r'settings/outlets', OutletManagementViewSet, basename='admin-outlet-management')
admin_router.register(r'stores', StoreAdminViewSet, basename='admin-stores')

urlpatterns = [
    path('public/', include(public_router.urls)),  # Public kiosk endpoints
    path('', include(router.urls)),  # Authenticated endpoints
    path('admin/', include(admin_router.urls)),  # Admin settings endpoints
]
