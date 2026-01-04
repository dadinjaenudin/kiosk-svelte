from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Promotion(models.Model):
    """
    Promotion model for managing discounts and special offers
    """
    
    # Promo Types
    TYPE_PERCENTAGE = 'percentage'
    TYPE_FIXED = 'fixed'
    TYPE_BUY_X_GET_Y = 'buy_x_get_y'
    TYPE_BUNDLE = 'bundle'
    
    TYPE_CHOICES = [
        (TYPE_PERCENTAGE, 'Percentage Discount'),
        (TYPE_FIXED, 'Fixed Amount Discount'),
        (TYPE_BUY_X_GET_Y, 'Buy X Get Y'),
        (TYPE_BUNDLE, 'Bundle Deal'),
    ]
    
    # Status
    STATUS_DRAFT = 'draft'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_PAUSED = 'paused'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_PAUSED, 'Paused'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=200, help_text="Promotion name")
    description = models.TextField(blank=True, help_text="Detailed description")
    code = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        help_text="Optional promo code for customers to enter"
    )
    
    # Tenant relationship
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='promotions',
        help_text="Tenant who owns this promotion"
    )
    
    # Promo Configuration
    promo_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_PERCENTAGE
    )
    
    # Discount Value
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Discount amount (percentage or fixed)"
    )
    
    # For percentage discounts (0-100)
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Maximum discount amount for percentage-based promos"
    )
    
    # Minimum purchase requirement
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minimum purchase amount to qualify"
    )
    
    # For Buy X Get Y promos
    buy_quantity = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Buy X quantity (for Buy X Get Y promos)"
    )
    get_quantity = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Get Y quantity (for Buy X Get Y promos)"
    )
    
    # Schedule
    start_date = models.DateTimeField(help_text="Promotion start date and time")
    end_date = models.DateTimeField(help_text="Promotion end date and time")
    
    # Days of week (for recurring promos)
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=True)
    sunday = models.BooleanField(default=True)
    
    # Time restrictions
    time_start = models.TimeField(blank=True, null=True, help_text="Daily start time (optional)")
    time_end = models.TimeField(blank=True, null=True, help_text="Daily end time (optional)")
    
    # Usage Limits
    usage_limit = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of times this promo can be used (total)"
    )
    usage_limit_per_customer = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum uses per customer"
    )
    usage_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current usage count"
    )
    
    # Status & Flags
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    is_active = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False, help_text="Show in featured promotions")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_promotions'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active', 'status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_promo_type_display()})"
    
    def is_valid_now(self):
        """Check if promotion is currently valid"""
        now = timezone.now()
        
        # Check date range
        if not (self.start_date <= now <= self.end_date):
            return False
        
        # Check day of week
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        day_flags = [
            self.monday, self.tuesday, self.wednesday, 
            self.thursday, self.friday, self.saturday, self.sunday
        ]
        if not day_flags[weekday]:
            return False
        
        # Check time range (if specified)
        if self.time_start and self.time_end:
            current_time = now.time()
            if not (self.time_start <= current_time <= self.time_end):
                return False
        
        # Check usage limit
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        
        return self.is_active and self.status == self.STATUS_ACTIVE
    
    def calculate_discount(self, amount):
        """Calculate discount amount based on promo type"""
        if self.promo_type == self.TYPE_PERCENTAGE:
            discount = (amount * self.discount_value) / 100
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        elif self.promo_type == self.TYPE_FIXED:
            return min(self.discount_value, amount)
        return 0
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class PromotionProduct(models.Model):
    """
    Many-to-many relationship between Promotions and Products
    """
    
    # Product roles for Buy X Get Y promotions
    ROLE_BUY = 'buy'
    ROLE_GET = 'get'
    ROLE_BOTH = 'both'  # Default: product can be both bought and received
    
    ROLE_CHOICES = [
        (ROLE_BUY, 'Buy Product (X)'),
        (ROLE_GET, 'Get Product (Y)'),
        (ROLE_BOTH, 'Both Buy and Get'),
    ]
    
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name='promotion_products'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='product_promotions'
    )
    
    # Product role for Buy X Get Y promotions
    product_role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_BOTH,
        help_text="Role of this product in Buy X Get Y promotions"
    )
    
    # Optional: specific discount override for this product
    custom_discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Override discount for this specific product"
    )
    
    # Priority (for when multiple promos apply)
    priority = models.IntegerField(
        default=0,
        help_text="Higher priority promos are applied first"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['promotion', 'product']
        ordering = ['-priority', 'created_at']
    
    def __str__(self):
        return f"{self.promotion.name} -> {self.product.name} ({self.get_product_role_display()})"


class PromotionUsage(models.Model):
    """
    Track promotion usage by customers
    """
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='promotion_usages'
    )
    customer_identifier = models.CharField(
        max_length=255,
        blank=True,
        help_text="Customer ID, phone, or session identifier"
    )
    
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Actual discount amount applied"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['promotion', 'customer_identifier']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.promotion.name} - Order #{self.order.id}"
