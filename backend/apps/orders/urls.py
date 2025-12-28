"""
Orders URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.views import OrderViewSet
from apps.orders.views_admin import OrderManagementViewSet
from apps.orders.views_reports import ReportsViewSet

# Public/Kiosk router
public_router = DefaultRouter()
public_router.register(r'orders', OrderViewSet, basename='order')

# Admin router
admin_router = DefaultRouter()
admin_router.register(r'admin/orders', OrderManagementViewSet, basename='admin-order')
admin_router.register(r'admin/reports', ReportsViewSet, basename='admin-report')

urlpatterns = [
    path('', include(public_router.urls)),
    path('', include(admin_router.urls)),
]
