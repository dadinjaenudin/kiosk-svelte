"""
URL routes for authentication
"""
from django.urls import path
from apps.users import auth_views

urlpatterns = [
    path('login/', auth_views.login_view, name='auth-login'),
    path('logout/', auth_views.logout_view, name='auth-logout'),
    path('me/', auth_views.me_view, name='auth-me'),
    path('refresh/', auth_views.refresh_token_view, name='auth-refresh'),
    path('change-password/', auth_views.change_password_view, name='auth-change-password'),
]
