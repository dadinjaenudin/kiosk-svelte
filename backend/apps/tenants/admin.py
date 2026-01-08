"""
Admin configuration for Tenant models
"""
from django.contrib import admin
from .models import Tenant, Outlet, Store, StoreOutlet


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'tax_rate', 'service_charge_rate', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'tenant', 'city', 'is_active', 'created_at')
    list_filter = ('tenant', 'city', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'address', 'city')
    readonly_fields = ('kiosk_qr_code', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('tenant', 'code', 'name')
        }),
        ('Address', {
            'fields': ('address', 'city', 'province', 'postal_code', 'latitude', 'longitude')
        }),
        ('Operating Hours', {
            'fields': ('opening_time', 'closing_time')
        }),
        ('Kiosk Setup', {
            'fields': ('kiosk_qr_code', 'enable_multi_outlet_payment', 'payment_split_method')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'tenant', 'phone', 'is_active', 'created_at')
    list_filter = ('tenant', 'is_active', 'created_at')
    search_fields = ('brand_name', 'name', 'phone')
    prepopulated_fields = {'slug': ('brand_name',)}
    
    fieldsets = (
        ('Brand Info', {
            'fields': ('tenant', 'brand_name', 'name', 'slug')
        }),
        ('Contact', {
            'fields': ('phone', 'email')
        }),
        ('Network', {
            'fields': ('websocket_url',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StoreOutlet)
class StoreOutletAdmin(admin.ModelAdmin):
    list_display = ('outlet_brand', 'store_name', 'store_code', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active', 'store__tenant', 'created_at')
    search_fields = ('outlet__brand_name', 'store__name', 'store__code')
    list_editable = ('is_active', 'display_order')
    
    fieldsets = (
        ('Assignment', {
            'fields': ('store', 'outlet')
        }),
        ('Status', {
            'fields': ('is_active', 'display_order')
        }),
        ('Custom Hours (Optional)', {
            'fields': ('custom_opening_time', 'custom_closing_time'),
            'description': 'Override store operating hours for this brand'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def outlet_brand(self, obj):
        return obj.outlet.brand_name
    outlet_brand.short_description = 'Brand'
    
    def store_name(self, obj):
        return obj.store.name
    store_name.short_description = 'Store'
    
    def store_code(self, obj):
        return obj.store.code
    store_code.short_description = 'Store Code'
