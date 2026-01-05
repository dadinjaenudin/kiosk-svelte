"""
Order models untuk transaksi management
"""
from django.db import models
from django.conf import settings
from apps.tenants.models import Tenant, Outlet
from apps.products.models import Product
import uuid


class Order(models.Model):
    """
    Order/Transaction
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='orders')
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='orders')
    
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Customer info (optional for walk-in)
    customer_name = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_email = models.EmailField(blank=True)
    
    # Order details
    table_number = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    service_charge_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment
    payment_status = models.CharField(max_length=20, default='unpaid', db_index=True)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Source tracking
    SOURCE_CHOICES = (
        ('kiosk', 'Kiosk'),
        ('web', 'Web/Mobile'),
        ('cashier', 'Cashier POS'),
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='web', db_index=True)
    device_id = models.CharField(max_length=50, blank=True, null=True, help_text='Device identifier (e.g., kiosk-001)')
    
    # Staff
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders_as_cashier')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'status']),
            models.Index(fields=['outlet', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - Rp {self.total_amount:,.0f}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: ORD-YYYYMMDD-XXXX
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = str(uuid.uuid4().hex[:4]).upper()
            self.order_number = f"ORD-{date_str}-{random_str}"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate order totals"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.tax_amount = self.subtotal * (self.tenant.tax_rate / 100)
        self.service_charge_amount = self.subtotal * (self.tenant.service_charge_rate / 100)
        self.total_amount = self.subtotal + self.tax_amount + self.service_charge_amount - self.discount_amount
        self.save()


class OrderItem(models.Model):
    """
    Order item - individual product in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    
    product_name = models.CharField(max_length=200)  # Snapshot
    product_sku = models.CharField(max_length=50)
    
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Kitchen routing (snapshot from product at order time)
    kitchen_station_code = models.CharField(
        max_length=20, 
        default='MAIN',
        db_index=True,
        help_text='Kitchen station code for routing (snapshot from product)'
    )
    
    # Modifiers (stored as JSON)
    modifiers = models.JSONField(default=list, blank=True)
    modifiers_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = (self.unit_price + self.modifiers_price) * self.quantity
        super().save(*args, **kwargs)
