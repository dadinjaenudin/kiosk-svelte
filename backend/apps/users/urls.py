"""
URL routing for User API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
