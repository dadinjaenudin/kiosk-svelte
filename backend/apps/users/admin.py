"""
Admin configuration for User model
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin with multi-outlet support
    """
    list_display = ('username', 'email', 'role', 'tenant', 'outlet', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'tenant', 'outlet')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    filter_horizontal = ('accessible_outlets',)  # For ManyToMany field
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'phone_number', 'tenant', 'outlet', 'accessible_outlets')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'phone_number', 'tenant', 'outlet', 'accessible_outlets')
        }),
    )
