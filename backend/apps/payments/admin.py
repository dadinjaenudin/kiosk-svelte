"""
Admin configuration for Payment models
"""
from django.contrib import admin
from .models import Payment, PaymentCallback


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'gateway_provider', 'created_at')
    search_fields = ('transaction_id', 'order__order_number', 'gateway_transaction_id')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('transaction_id', 'order', 'payment_method', 'amount', 'status')
        }),
        ('Gateway Info', {
            'fields': ('gateway_provider', 'gateway_transaction_id', 'qr_code_url', 'payment_url')
        }),
        ('Response Data', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PaymentCallback)
class PaymentCallbackAdmin(admin.ModelAdmin):
    list_display = ('payment', 'gateway_provider', 'event_type', 'received_at')
    list_filter = ('gateway_provider', 'event_type', 'received_at')
    search_fields = ('payment__transaction_id',)
    readonly_fields = ('received_at',)
