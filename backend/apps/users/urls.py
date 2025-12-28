"""
URL routing for User API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users import views
from apps.users.views_admin import UserManagementViewSet

# Public router
public_router = DefaultRouter()
public_router.register(r'users', views.UserViewSet, basename='user')

# Admin router
admin_router = DefaultRouter()
admin_router.register(r'admin/users', UserManagementViewSet, basename='admin-user')

urlpatterns = [
    path('', include(public_router.urls)),
    path('', include(admin_router.urls)),
]
