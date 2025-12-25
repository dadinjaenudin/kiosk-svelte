"""
Admin configuration for Order models
"""
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'unit_price', 'modifiers', 'total_price')
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'tenant', 'outlet', 'status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'tenant', 'outlet', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'tenant', 'outlet', 'status', 'payment_status')
        }),
        ('Customer Info', {
            'fields': ('customer_name', 'customer_phone', 'table_number')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'service_charge_amount', 'discount_amount', 'total_amount')
        }),
        ('Staff', {
            'fields': ('cashier',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__status', 'product')
    search_fields = ('order__order_number', 'product__name')
