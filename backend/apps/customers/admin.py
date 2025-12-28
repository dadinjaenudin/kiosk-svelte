"""
Admin configuration for Customers
"""
from django.contrib import admin
from apps.customers.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'membership_tier', 'points', 'is_active', 'created_at']
    list_filter = ['membership_tier', 'is_active', 'gender', 'is_subscribed']
    search_fields = ['name', 'phone', 'email', 'membership_number']
    readonly_fields = ['membership_number', 'created_at', 'updated_at', 'last_order_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'name', 'email', 'phone')
        }),
        ('Additional Info', {
            'fields': ('gender', 'date_of_birth', 'address', 'city', 'postal_code')
        }),
        ('Membership', {
            'fields': ('membership_number', 'membership_tier', 'points')
        }),
        ('Preferences', {
            'fields': ('preferred_outlet', 'notes', 'is_subscribed')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_order_at')
        }),
    )
