"""
Admin configuration for Payment models
"""
from django.contrib import admin
from .models import Payment, PaymentCallback


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'payment_provider', 'created_at')
    search_fields = ('transaction_id', 'order__order_number', 'external_id')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at', 'paid_at')
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('transaction_id', 'order', 'payment_method', 'amount', 'status')
        }),
        ('Gateway Info', {
            'fields': ('payment_provider', 'external_id', 'qr_code_url', 'payment_url')
        }),
        ('Response Data', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'expired_at')
        }),
    )


@admin.register(PaymentCallback)
class PaymentCallbackAdmin(admin.ModelAdmin):
    list_display = ('payment', 'provider', 'is_processed', 'created_at')
    list_filter = ('provider', 'is_processed', 'created_at')
    search_fields = ('payment__transaction_id',)
    readonly_fields = ('created_at', 'processed_at')
