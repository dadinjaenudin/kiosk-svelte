"""
User models untuk authentication dan role management
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model dengan role-based access
    """
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('tenant_owner', 'Tenant Owner'),  # New role for franchise owners
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('kitchen', 'Kitchen Staff'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')
    phone_number = models.CharField(max_length=20, blank=True)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    
    # Multi-outlet support
    outlet = models.ForeignKey('tenants.Outlet', on_delete=models.SET_NULL, null=True, blank=True, related_name='users', 
                               help_text='Primary/default outlet for this user')
    accessible_outlets = models.ManyToManyField('tenants.Outlet', blank=True, related_name='accessible_users',
                                                help_text='Outlets this user can access (for managers)')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
