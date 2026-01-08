"""
Order models untuk transaksi management
"""
from django.db import models
from django.conf import settings
from apps.tenants.models import Tenant, Outlet, Store
from apps.products.models import Product
import uuid
from datetime import datetime


class OrderGroup(models.Model):
    """
    Order Group - Groups multiple orders from different outlets in one payment transaction
    Used for kiosk where customer orders from multiple brands at a store
    """
    group_number = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        help_text='Unique identifier for this order group (e.g., GRP-20260106-ABCD)'
    )
    
    store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_groups',
        help_text='Physical store where orders were placed'
    )
    
    # Customer info
    customer_name = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_email = models.EmailField(blank=True)
    
    # Payment
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('refunded', 'Refunded'),
    )
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid', 
        db_index=True
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('qris', 'QRIS'),
        ('ewallet', 'E-Wallet'),
        ('split', 'Split Payment'),
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        blank=True
    )
    
    # Totals (aggregated from all orders in group)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Source tracking
    SOURCE_CHOICES = (
        ('kiosk', 'Kiosk'),
        ('web', 'Web/Mobile'),
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='kiosk')
    device_id = models.CharField(
        max_length=50, 
        blank=True, 
        help_text='Kiosk device identifier'
    )
    
    # Session tracking
    session_id = models.CharField(
        max_length=100, 
        blank=True,
        help_text='Frontend session ID for tracking'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'order_groups'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'payment_status']),
            models.Index(fields=['store', '-created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        order_count = self.orders.count()
        return f"{self.group_number} - {order_count} orders - Rp {self.total_amount:,.0f}"
    
    def save(self, *args, **kwargs):
        if not self.group_number:
            # Generate group number: GRP-YYYYMMDD-XXXX
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = str(uuid.uuid4().hex[:4]).upper()
            self.group_number = f"GRP-{date_str}-{random_str}"
        super().save(*args, **kwargs)
    
    def calculate_total(self):
        """Calculate total from all orders in group"""
        self.total_amount = sum(
            order.total_amount for order in self.orders.all()
        )
        self.save()
    
    def mark_as_paid(self, payment_method='cash'):
        """Mark order group as paid and update all orders"""
        self.payment_status = 'paid'
        self.payment_method = payment_method
        self.paid_amount = self.total_amount
        self.paid_at = datetime.now()
        self.save()
        
        # Update all orders in group
        # FIXED: Keep status='pending' for kitchen display
        self.orders.update(
            payment_status='paid',
            paid_amount=models.F('total_amount'),
            status='pending'  # Keep pending for kitchen processing
        )
    
    def get_outlet_breakdown(self):
        """Get payment breakdown per outlet"""
        breakdown = {}
        for order in self.orders.select_related('outlet', 'tenant'):
            outlet_key = f"{order.tenant.name} - {order.outlet.name}"
            breakdown[outlet_key] = {
                'order_number': order.order_number,
                'outlet': order.outlet.name,
                'tenant': order.tenant.name,
                'amount': float(order.total_amount),
                'items_count': order.items.count()
            }
        return breakdown


class Order(models.Model):
    """
    Order/Transaction - Individual order per outlet/brand
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
    
    # Store where order was placed (for kitchen routing)
    store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text='Physical store where this order was placed (for kitchen display routing)'
    )
    
    # Link to order group (for multi-outlet orders)
    order_group = models.ForeignKey(
        OrderGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='orders',
        help_text='Group this order belongs to (for multi-outlet payments)'
    )
    
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
