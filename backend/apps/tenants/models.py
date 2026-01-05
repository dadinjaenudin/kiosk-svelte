"""
Tenant models untuk multi-tenant management
"""
from django.db import models
from django.utils.text import slugify


class Tenant(models.Model):
    """
    Tenant/Brand - represents a restaurant brand
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='tenants/logos/', null=True, blank=True)
    
    # Branding
    primary_color = models.CharField(max_length=7, default='#FF6B35')
    secondary_color = models.CharField(max_length=7, default='#F7931E')
    
    # Business info
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Tax settings
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    service_charge_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Outlet(models.Model):
    """
    Outlet/Store location
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='outlets')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Operating hours
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    # Network Configuration
    websocket_url = models.CharField(
        max_length=255, 
        blank=True, 
        default='ws://localhost:3001',
        help_text='WebSocket URL for Kitchen Sync Server (e.g., ws://192.168.1.10:3001)'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'outlets'
        ordering = ['tenant', 'name']
        unique_together = [['tenant', 'slug']]
    
    def __str__(self):
        return f"{self.tenant.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class KitchenStationType(models.Model):
    """
    Kitchen Station Type - Master table for kitchen station types
    Can be managed by tenant or shared across all tenants
    
    Examples:
    - MAIN: Main Kitchen (general purpose)
    - BEVERAGE: Drink Station / Bar
    - GRILL: Grill Station (burgers, steaks)
    - WOK: Wok Station (stir-fry)
    - PIZZA: Pizza Oven
    - DESSERT: Dessert Station
    - FRY: Fry Station (fries, fried items)
    - ASSEMBLY: Final Assembly / Packaging
    """
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='kitchen_station_types',
        null=True,
        blank=True,
        help_text='Leave empty for global types available to all tenants'
    )
    
    name = models.CharField(
        max_length=100, 
        help_text='Display name (e.g., "Main Kitchen", "Grill Station")'
    )
    code = models.CharField(
        max_length=20, 
        help_text='Unique code (e.g., "MAIN", "GRILL", "BEVERAGE")',
        db_index=True
    )
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50, 
        blank=True,
        help_text='Icon name or emoji (e.g., "🍳", "☕", "🍔")'
    )
    color = models.CharField(
        max_length=7, 
        default='#FF6B35',
        help_text='Hex color code for UI display'
    )
    
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(
        default=False,
        help_text='Global types are available to all tenants'
    )
    sort_order = models.IntegerField(
        default=0, 
        help_text='Display order (lower number = first)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kitchen_station_types'
        ordering = ['sort_order', 'name']
        unique_together = [['tenant', 'code']]  # Code unique per tenant (or global)
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['tenant', 'is_active']),
        ]
    
    def __str__(self):
        tenant_prefix = f"{self.tenant.name} - " if self.tenant else "Global - "
        return f"{tenant_prefix}{self.name} ({self.code})"


class KitchenStation(models.Model):
    """
    Kitchen Station - represents a physical kitchen station in an outlet
    Example: Food Kitchen, Drink Bar, Grill Station, Dessert Station
    """
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='kitchen_stations')
    name = models.CharField(max_length=100, help_text='Display name (e.g., "Food Kitchen", "Drink Bar")')
    code = models.CharField(max_length=20, help_text='Short code (e.g., "FOOD", "DRINK", "GRILL")')
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0, help_text='Display order (lower number = first)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kitchen_stations'
        ordering = ['outlet', 'sort_order', 'name']
        unique_together = [['outlet', 'code']]
        indexes = [
            models.Index(fields=['outlet', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.outlet.name} - {self.name}"
