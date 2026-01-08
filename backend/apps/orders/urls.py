"""
Orders URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.views import OrderViewSet
from apps.orders.views_admin import OrderManagementViewSet
from apps.orders.views_reports import ReportsViewSet
from apps.orders.views_order_group import PublicOrderGroupViewSet, OrderGroupAdminViewSet
from apps.orders.views_kitchen import KitchenOrderViewSet

# Public/Kiosk router
public_router = DefaultRouter()
public_router.register(r'orders', OrderViewSet, basename='order')
public_router.register(r'order-groups', PublicOrderGroupViewSet, basename='order-group')

# Kitchen router
kitchen_router = DefaultRouter()
kitchen_router.register(r'kitchen/orders', KitchenOrderViewSet, basename='kitchen-order')

# Admin router
admin_router = DefaultRouter()
admin_router.register(r'admin/orders', OrderManagementViewSet, basename='admin-order')
admin_router.register(r'admin/order-groups', OrderGroupAdminViewSet, basename='admin-order-group')
admin_router.register(r'admin/reports', ReportsViewSet, basename='admin-report')

urlpatterns = [
    path('', include(public_router.urls)),
    path('', include(kitchen_router.urls)),
    path('', include(admin_router.urls)),
]
