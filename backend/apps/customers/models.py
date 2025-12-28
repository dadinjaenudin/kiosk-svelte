"""
Customer models untuk customer management
"""
from django.db import models
from apps.tenants.models import Tenant, Outlet


class Customer(models.Model):
    """
    Customer - represents a customer/member
    """
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    # Tenant relationship
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='customers')
    
    # Basic info
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, db_index=True)
    
    # Additional info
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Membership
    membership_number = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True)
    membership_tier = models.CharField(max_length=50, default='regular')  # regular, silver, gold, platinum
    points = models.IntegerField(default=0)
    
    # Preferences
    preferred_outlet = models.ForeignKey(Outlet, on_delete=models.SET_NULL, null=True, blank=True, related_name='preferred_customers')
    notes = models.TextField(blank=True)
    
    # Marketing
    is_subscribed = models.BooleanField(default=True)  # Email/SMS marketing
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_order_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        unique_together = [['tenant', 'phone']]  # Phone unique per tenant
        indexes = [
            models.Index(fields=['tenant', '-created_at']),
            models.Index(fields=['tenant', 'phone']),
            models.Index(fields=['tenant', 'membership_tier']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.phone}"
    
    def save(self, *args, **kwargs):
        # Auto-generate membership number if not set
        if not self.membership_number:
            import uuid
            self.membership_number = f"CUST-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def total_orders(self):
        """Get total number of orders"""
        return self.orders.count()
    
    @property
    def total_spent(self):
        """Get total amount spent"""
        from django.db.models import Sum
        result = self.orders.filter(payment_status='paid').aggregate(total=Sum('total_amount'))
        return result['total'] or 0
    
    @property
    def average_order_value(self):
        """Get average order value"""
        total_orders = self.total_orders
        if total_orders > 0:
            return self.total_spent / total_orders
        return 0
