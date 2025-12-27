from django.contrib import admin
from .models import Promotion, PromotionProduct, PromotionUsage


class PromotionProductInline(admin.TabularInline):
    model = PromotionProduct
    extra = 1
    fields = ['product', 'custom_discount_value', 'priority']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'tenant', 'promo_type', 'discount_value', 
        'status', 'start_date', 'end_date', 'usage_count', 'is_active'
    ]
    list_filter = ['status', 'promo_type', 'is_active', 'tenant', 'created_at']
    search_fields = ['name', 'description', 'code']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'code', 'tenant', 'created_by')
        }),
        ('Discount Configuration', {
            'fields': (
                'promo_type', 'discount_value', 'max_discount_amount',
                'min_purchase_amount'
            )
        }),
        ('Buy X Get Y Settings', {
            'fields': ('buy_quantity', 'get_quantity'),
            'classes': ('collapse',)
        }),
        ('Schedule', {
            'fields': (
                'start_date', 'end_date',
                ('monday', 'tuesday', 'wednesday', 'thursday'),
                ('friday', 'saturday', 'sunday'),
                'time_start', 'time_end'
            )
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'usage_limit_per_customer', 'usage_count')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'is_featured')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PromotionProductInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PromotionUsage)
class PromotionUsageAdmin(admin.ModelAdmin):
    list_display = ['promotion', 'order', 'customer_identifier', 'discount_amount', 'created_at']
    list_filter = ['promotion', 'created_at']
    search_fields = ['customer_identifier', 'promotion__name', 'order__order_number']
    readonly_fields = ['created_at']
