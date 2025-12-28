"""
URL configuration for Products API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet
from .views_admin import (
    CategoryManagementViewSet, 
    ProductManagementViewSet,
    ProductModifierManagementViewSet
)

# Public router (for Kiosk)
public_router = DefaultRouter()
public_router.register(r'categories', CategoryViewSet, basename='category')
public_router.register(r'products', ProductViewSet, basename='product')

# Admin router
admin_router = DefaultRouter()
admin_router.register(r'admin/categories', CategoryManagementViewSet, basename='admin-category')
admin_router.register(r'admin/products', ProductManagementViewSet, basename='admin-product')
admin_router.register(r'admin/modifiers', ProductModifierManagementViewSet, basename='admin-modifier')

urlpatterns = [
    path('', include(public_router.urls)),
    path('', include(admin_router.urls)),
]
