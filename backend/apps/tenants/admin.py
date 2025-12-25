"""
Admin configuration for Tenant models
"""
from django.contrib import admin
from .models import Tenant, Outlet


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'tax_rate', 'service_charge_rate', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'city', 'phone', 'is_active', 'created_at')
    list_filter = ('tenant', 'city', 'is_active', 'created_at')
    search_fields = ('name', 'address', 'city', 'phone')
    prepopulated_fields = {'slug': ('name',)}
