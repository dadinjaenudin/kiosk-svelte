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
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'is_available', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductModifier)
class ProductModifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'modifier_type', 'price', 'is_available')
    list_filter = ('modifier_type', 'is_available')
    search_fields = ('name', 'product__name')


@admin.register(OutletProduct)
class OutletProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'outlet', 'price_override', 'stock_quantity', 'is_available')
    list_filter = ('outlet', 'is_available')
    search_fields = ('product__name', 'outlet__name')
