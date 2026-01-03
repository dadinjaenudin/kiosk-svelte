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
    postal_code = models.CharField(max_length=10)
    
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
