"""
Tenant models untuk multi-tenant management
"""
from django.db import models
from django.utils.text import slugify
import uuid


class Store(models.Model):
    """
    Store - Physical retail store location owned by a tenant
    Represents a physical store (e.g., Yogya Kapatihan, Borma Dago)
    A store can have multiple outlets/brands (e.g., Chicken Sumo, Magic Oven)
    Used for kiosk configuration and grouping outlets by store
    """
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='stores',
        help_text='Retail company that owns this store (e.g., YOGYA, BORMA)'
    )
    code = models.CharField(
        max_length=50, 
        unique=True, 
        help_text='Store identifier code (e.g., YOGYA-KAPATIHAN, BORMA-DAGO)'
    )
    name = models.CharField(
        max_length=200, 
        help_text='Store display name (e.g., "Yogya Kapatihan", "Borma Dago")'
    )
    
    # Address
    address = models.TextField(help_text='Full address of the location')
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Operating hours (NEW - moved from Outlet)
    opening_time = models.TimeField(
        null=True, 
        blank=True,
        help_text='Store opening time (e.g., 08:00:00)'
    )
    closing_time = models.TimeField(
        null=True, 
        blank=True,
        help_text='Store closing time (e.g., 21:00:00)'
    )
    
    # Kiosk Configuration
    kiosk_qr_code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        help_text='Unique QR code identifier for kiosk setup'
    )
    
    # Settings
    enable_multi_outlet_payment = models.BooleanField(
        default=True,
        help_text='Allow customers to order from multiple outlets in one transaction'
    )
    payment_split_method = models.CharField(
        max_length=20,
        choices=[
            ('proportional', 'Proportional to Order Total'),
            ('even', 'Split Evenly'),
            ('manual', 'Manual Split')
        ],
        default='proportional',
        help_text='How to split payment across multiple outlets'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stores'
        ordering = ['tenant', 'name']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['kiosk_qr_code']),
        ]
        unique_together = [['tenant', 'code']]
    
    def __str__(self):
        return f"{self.tenant.name} - {self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        # Generate QR code if not set
        if not self.kiosk_qr_code:
            self.kiosk_qr_code = f"STORE-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def get_active_outlets(self):
        """Get all active outlets/brands at this store (via M2M relationship)"""
        return self.outlets.filter(is_active=True)
    
    def get_available_brands(self):
        """Get all available brands at this store via StoreOutlet junction"""
        return self.outlets.filter(store_outlets__is_active=True)


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
    Outlet - Brand/Business unit (Global across all stores)
    Represents a brand (e.g., Chicken Sumo, Magic Oven, Magic Pizza)
    Can operate at multiple stores via StoreOutlet junction table
    Each outlet has its own menu (categories, products) and kitchen stations
    """
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='outlets',
        help_text='Retail company that owns this brand'
    )
    
    # Many-to-Many relationship with Store (via StoreOutlet junction)
    stores = models.ManyToManyField(
        Store,
        through='StoreOutlet',
        related_name='outlets',
        help_text='Stores where this brand is available'
    )
    
    brand_name = models.CharField(
        max_length=200,
        help_text='Brand name (e.g., Chicken Sumo, Magic Oven, Magic Pizza)'
    )
    name = models.CharField(
        max_length=200,
        help_text='Display name (usually same as brand_name)'
    )
    slug = models.SlugField(max_length=200)
    
    # Contact (Global brand contact)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Network Configuration (for kitchen sync)
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
        ordering = ['tenant', 'brand_name']
        unique_together = [['tenant', 'slug']]
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['brand_name']),
        ]
    
    def __str__(self):
        return f"{self.brand_name} ({self.tenant.name})"
    
    def save(self, *args, **kwargs):
        # Auto-set name from brand_name if not provided
        if not self.name:
            self.name = self.brand_name
        
        if not self.slug:
            self.slug = slugify(self.brand_name)
        super().save(*args, **kwargs)


class StoreOutlet(models.Model):
    """
    Junction table for Many-to-Many relationship between Store and Outlet
    Represents which brands are available at which stores
    """
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE, 
        related_name='store_outlets'
    )
    outlet = models.ForeignKey(
        Outlet, 
        on_delete=models.CASCADE, 
        related_name='store_outlets'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this brand is currently active at this store'
    )
    
    # Optional: Per-store customization
    custom_opening_time = models.TimeField(
        null=True, 
        blank=True,
        help_text='Override store opening time for this brand'
    )
    custom_closing_time = models.TimeField(
        null=True, 
        blank=True,
        help_text='Override store closing time for this brand'
    )
    display_order = models.IntegerField(
        default=0,
        help_text='Sort order in kiosk UI (lower number = first)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'store_outlets'
        unique_together = ['store', 'outlet']  # No duplicate brand in same store
        ordering = ['store', 'display_order', 'outlet__brand_name']
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['outlet', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.outlet.brand_name} at {self.store.name}"


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
