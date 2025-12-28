"""
URL routing for Customer API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.customers.views_admin import CustomerManagementViewSet

# Admin router
admin_router = DefaultRouter()
admin_router.register(r'admin/customers', CustomerManagementViewSet, basename='admin-customer')

urlpatterns = [
    path('', include(admin_router.urls)),
]
