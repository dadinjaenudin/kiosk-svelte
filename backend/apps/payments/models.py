"""
Payment models untuk payment processing
"""
from django.db import models
from apps.orders.models import Order
import uuid


class Payment(models.Model):
    """
    Payment transaction
    """
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('qris', 'QRIS'),
        ('gopay', 'GoPay'),
        ('ovo', 'OVO'),
        ('shopeepay', 'ShopeePay'),
        ('dana', 'DANA'),
        ('debit_card', 'Debit Card'),
        ('credit_card', 'Credit Card'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    external_id = models.CharField(max_length=200, blank=True, db_index=True)  # Payment gateway reference
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_provider = models.CharField(max_length=50, blank=True)  # midtrans, xendit, stripe
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Payment gateway response
    gateway_response = models.JSONField(default=dict, blank=True)
    qr_code_url = models.URLField(blank=True)
    payment_url = models.URLField(blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'status']),
            models.Index(fields=['order', 'status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.get_payment_method_display()} - Rp {self.amount:,.0f}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Generate transaction ID: PAY-YYYYMMDDHHMMSS-XXXX
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d%H%M%S')
            random_str = str(uuid.uuid4().hex[:4]).upper()
            self.transaction_id = f"PAY-{date_str}-{random_str}"
        super().save(*args, **kwargs)


class PaymentCallback(models.Model):
    """
    Payment webhook callback log
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='callbacks', null=True, blank=True)
    
    provider = models.CharField(max_length=50)
    callback_data = models.JSONField(default=dict)
    
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_callbacks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.provider} - {self.created_at}"
