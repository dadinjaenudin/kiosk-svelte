"""
Serializers for Tenant API
"""
from rest_framework import serializers
from apps.tenants.models import Tenant, Outlet


class TenantSerializer(serializers.ModelSerializer):
    """
    Serializer for Tenant model
    """
    
    outlet_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'slug', 'name', 'description',
            'phone', 'email', 'website',
            'subscription_plan', 'subscription_status',
            'tax_rate', 'service_charge_rate',
            'settings', 'logo_url', 'primary_color',
            'is_active', 'created_at', 'outlet_count'
        ]
        read_only_fields = ['id', 'created_at', 'outlet_count']
    
    def get_outlet_count(self, obj):
        """Get number of outlets for this tenant"""
        return obj.outlets.filter(is_active=True).count()


class TenantDetailSerializer(TenantSerializer):
    """
    Detailed serializer for Tenant with outlets
    """
    
    outlets = serializers.SerializerMethodField()
    
    class Meta(TenantSerializer.Meta):
        fields = TenantSerializer.Meta.fields + ['outlets']
    
    def get_outlets(self, obj):
        """Get all outlets for this tenant"""
        outlets = obj.outlets.filter(is_active=True)
        return OutletSerializer(outlets, many=True).data


class OutletSerializer(serializers.ModelSerializer):
    """
    Serializer for Outlet model
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Outlet
        fields = [
            'id', 'tenant', 'tenant_name', 'slug', 'name',
            'address', 'city', 'province', 'postal_code', 'country',
            'phone', 'email',
            'latitude', 'longitude',
            'operating_hours',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'tenant_name', 'created_at']
    
    def validate(self, data):
        """
        Validate outlet data
        """
        # Ensure tenant matches current tenant
        from apps.core.context import get_current_tenant
        
        tenant = get_current_tenant()
        if tenant and data.get('tenant') != tenant:
            raise serializers.ValidationError(
                'Cannot create outlet for different tenant'
            )
        
        return data


class OutletDetailSerializer(OutletSerializer):
    """
    Detailed serializer for Outlet
    """
    
    pass
