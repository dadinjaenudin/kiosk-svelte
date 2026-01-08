"""
Product models untuk menu management
"""
from django.db import models
from apps.core.models import TenantModel
from apps.tenants.models import Tenant, Outlet


class Category(TenantModel):
    """
    Product category - Per Outlet/Brand
    Each brand has its own menu structure and categories
    """
    outlet = models.ForeignKey(
        Outlet, 
        on_delete=models.CASCADE, 
        related_name='categories',
        null=True,  # Temporarily nullable for migration
        blank=True,
        help_text='Brand that owns this category (e.g., Chicken Sumo, Magic Oven)'
    )
    # Keep tenant for backward compatibility and easier queries
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='categories',
        help_text='Automatically set from outlet.tenant'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Kitchen Station Routing
    kitchen_station_code = models.CharField(
        max_length=20,
        default='MAIN',
        help_text='Auto-route products in this category to kitchen station (e.g., MAIN, BEVERAGE, GRILL, DESSERT)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        ordering = ['outlet', 'sort_order', 'name']
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['outlet', 'is_active']),
            models.Index(fields=['tenant', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.outlet.brand_name} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Auto-set tenant from outlet
        if self.outlet and not self.tenant_id:
            self.tenant = self.outlet.tenant
        super().save(*args, **kwargs)


class Product(TenantModel):
    """
    Product/Menu item - Per Outlet/Brand
    Each brand has its own menu and products
    Category-Based Routing: Products auto-route to kitchen stations based on category
    """
    outlet = models.ForeignKey(
        Outlet, 
        on_delete=models.CASCADE, 
        related_name='products',
        null=True,  # Temporarily nullable for migration
        blank=True,
        help_text='Brand that owns this product (e.g., Chicken Sumo, Magic Oven)'
    )
    # Keep tenant for backward compatibility and easier queries
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='products',
        help_text='Automatically set from outlet.tenant'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products'
    )
    
    # Kitchen Station Override (optional)
    kitchen_station_code_override = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='Override category default routing (e.g., MAIN, BEVERAGE, GRILL). Leave blank to use category default.'
    )
    
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Stock
    track_stock = models.BooleanField(default=False)
    stock_quantity = models.IntegerField(default=0)
    low_stock_alert = models.IntegerField(default=10)
    
    # Flags
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, help_text='Popular/Bestseller item')
    has_promo = models.BooleanField(default=False, help_text='Item has active promotion')
    promo_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Promotional price')
    
    # Metadata
    preparation_time = models.IntegerField(default=10, help_text='Preparation time in minutes')
    calories = models.IntegerField(null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text='Comma-separated tags')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['outlet', 'category', 'name']
        indexes = [
            models.Index(fields=['outlet', 'is_active']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.outlet.brand_name} - {self.name} - Rp {self.price:,.0f}"
    
    def save(self, *args, **kwargs):
        # Auto-set tenant from outlet
        if self.outlet and not self.tenant_id:
            self.tenant = self.outlet.tenant
        super().save(*args, **kwargs)
    
    @property
    def kitchen_station_code(self):
        """Get effective kitchen station code (override or category default)"""
        if self.kitchen_station_code_override:
            return self.kitchen_station_code_override
        return self.category.kitchen_station_code if self.category else 'MAIN'
    
    @property
    def is_low_stock(self):
        if self.track_stock:
            return self.stock_quantity <= self.low_stock_alert
        return False


class ProductModifier(models.Model):
    """
    Product modifiers (size, toppings, level pedas, etc)
    Can be attached to specific products or be global per outlet
    """
    MODIFIER_TYPES = (
        ('size', 'Size'),
        ('topping', 'Topping'),
        ('spicy', 'Spicy Level'),
        ('extra', 'Extra'),
        ('sauce', 'Sauce'),
    )
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='modifiers', 
        null=True, 
        blank=True,
        help_text='Specific product (leave empty for global outlet modifiers)'
    )
    outlet = models.ForeignKey(
        Outlet,
        on_delete=models.CASCADE,
        related_name='modifiers',
        null=True,
        blank=True,
        help_text='Outlet/Brand for global modifiers (e.g., all Chicken Sumo products can have "Extra Spicy")'
    )
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=MODIFIER_TYPES, default='extra')
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'product_modifiers'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['outlet', 'is_active']),
        ]
    
    def __str__(self):
        if self.product:
            return f"{self.product.name} - {self.name} (+Rp {self.price_adjustment:,.0f})"
        elif self.outlet:
            return f"{self.outlet.brand_name} - {self.name} (+Rp {self.price_adjustment:,.0f})"
        return f"{self.name} (+Rp {self.price_adjustment:,.0f})"


class OutletProduct(models.Model):
    """
    Product availability and pricing per outlet
    """
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='outlet_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='outlet_products')
    
    # Outlet-specific pricing
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    
    # Outlet-specific stock
    stock_quantity = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'outlet_products'
        unique_together = [['outlet', 'product']]
    
    def __str__(self):
        return f"{self.outlet.name} - {self.product.name}"
    
    @property
    def effective_price(self):
        return self.price_override or self.product.price
