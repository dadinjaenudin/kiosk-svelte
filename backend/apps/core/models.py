"""
Base models for multi-tenant architecture

Provides base model classes and managers that automatically filter
queries by the current tenant.
"""
from django.db import models
from django.core.exceptions import ValidationError
from apps.core.context import get_current_tenant


class TenantManager(models.Manager):
    """
    Manager that automatically filters queries by current tenant
    """
    
    def get_queryset(self):
        """
        Override to filter by current tenant
        """
        qs = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant:
            return qs.filter(tenant=tenant)
        
        # If no tenant in context, return empty queryset for safety
        # This prevents accidentally exposing all tenants' data
        return qs.none()


class TenantAwareManager(models.Manager):
    """
    Manager that provides both filtered and unfiltered querysets
    """
    
    def get_queryset(self):
        """
        Override to filter by current tenant
        """
        qs = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant:
            return qs.filter(tenant=tenant)
        
        return qs.none()
    
    def all_tenants(self):
        """
        Get queryset for all tenants (bypass filter)
        Use with caution - only for superuser operations
        """
        return super().get_queryset()


class TenantModel(models.Model):
    """
    Abstract base model for tenant-specific models
    
    Automatically:
    - Adds tenant foreign key
    - Filters queries by current tenant
    - Sets tenant on save
    """
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        db_index=True,
        help_text='Tenant that owns this record'
    )
    
    # Default manager with auto-filtering
    objects = TenantManager()
    
    # Manager for all tenants (superuser only)
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
        # Add tenant to default ordering for performance
        ordering = ['tenant', '-id']
        indexes = [
            models.Index(fields=['tenant']),
        ]
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-set tenant from context
        """
        # Auto-set tenant if not already set
        if not self.tenant_id:
            tenant = get_current_tenant()
            if tenant:
                self.tenant = tenant
            else:
                raise ValidationError(
                    'Cannot save without tenant context. '
                    'Ensure tenant is set in middleware or explicitly on the model.'
                )
        
        # Validate tenant matches current tenant (if set)
        current_tenant = get_current_tenant()
        if current_tenant and self.tenant_id != current_tenant.id:
            raise ValidationError(
                f'Cannot save object for tenant {self.tenant_id} '
                f'when current tenant is {current_tenant.id}'
            )
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete to ensure tenant context
        """
        current_tenant = get_current_tenant()
        if current_tenant and self.tenant_id != current_tenant.id:
            raise ValidationError(
                f'Cannot delete object for tenant {self.tenant_id} '
                f'when current tenant is {current_tenant.id}'
            )
        
        super().delete(*args, **kwargs)


class OutletModel(models.Model):
    """
    Abstract base model for outlet-specific models
    
    Extends TenantModel to also track outlet
    """
    
    outlet = models.ForeignKey(
        'tenants.Outlet',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        db_index=True,
        help_text='Outlet that owns this record'
    )
    
    class Meta:
        abstract = True
        ordering = ['tenant', 'outlet', '-id']
        indexes = [
            models.Index(fields=['tenant', 'outlet']),
        ]


class TimestampedModel(models.Model):
    """
    Abstract base model with created and updated timestamps
    """
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class TenantTimestampedModel(TenantModel, TimestampedModel):
    """
    Combination of TenantModel and TimestampedModel
    
    Most models should inherit from this
    """
    
    class Meta:
        abstract = True
