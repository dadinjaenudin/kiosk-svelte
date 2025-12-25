"""
Admin configuration for Product models
"""
from django.contrib import admin
from .models import Category, Product, ProductModifier, OutletProduct


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'sort_order', 'is_active', 'created_at')
    list_filter = ('tenant', 'is_active', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'is_available', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'sku', 'description')


@admin.register(ProductModifier)
class ProductModifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'type', 'price_adjustment', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'product__name')


@admin.register(OutletProduct)
class OutletProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'outlet', 'price_override', 'stock_quantity', 'is_available')
    list_filter = ('outlet', 'is_available')
    search_fields = ('product__name', 'outlet__name')
