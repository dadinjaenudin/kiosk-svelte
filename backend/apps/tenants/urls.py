"""
URL routing for Tenant API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tenants import views

router = DefaultRouter()
router.register(r'tenants', views.TenantViewSet, basename='tenant')
router.register(r'outlets', views.OutletViewSet, basename='outlet')

urlpatterns = [
    path('', include(router.urls)),
]
