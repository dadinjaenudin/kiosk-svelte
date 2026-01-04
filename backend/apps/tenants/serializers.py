"""
Serializers for Tenant API
"""
from rest_framework import serializers
from apps.tenants.models import Tenant, Outlet, KitchenStation


class TenantSerializer(serializers.ModelSerializer):
    """
    Serializer for Tenant model
    """
    
    outlet_count = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'slug', 'name', 'description',
            'phone', 'email', 'website',
            'tax_rate', 'service_charge_rate',
            'logo_url', 'primary_color', 'secondary_color',
            'is_active', 'created_at', 'outlet_count'
        ]
        read_only_fields = ['id', 'created_at', 'outlet_count']
    
    def get_outlet_count(self, obj):
        """Get number of outlets for this tenant"""
        return obj.outlets.filter(is_active=True).count()
    
    def get_logo_url(self, obj):
        """Get logo URL"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


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
    operating_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Outlet
        fields = [
            'id', 'tenant', 'tenant_name', 'slug', 'name',
            'address', 'city', 'province', 'postal_code',
            'phone', 'email',
            'latitude', 'longitude',
            'opening_time', 'closing_time', 'operating_hours',
            'websocket_url',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'tenant_name', 'created_at']
        extra_kwargs = {
            'postal_code': {'required': False, 'allow_blank': True}
        }
    
    def get_operating_hours(self, obj):
        """Get formatted operating hours"""
        if obj.opening_time and obj.closing_time:
            return f"{obj.opening_time.strftime('%H:%M')} - {obj.closing_time.strftime('%H:%M')}"
        return None
    
    def validate(self, data):
        """
        Validate outlet data
        """
        # Ensure tenant matches current tenant (only for creation)
        from apps.core.context import get_current_tenant
        
        # Skip tenant validation for updates (instance exists)
        if self.instance is not None:
            return data
        
        # For creation, ensure tenant is provided and matches current tenant
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


class KitchenStationSerializer(serializers.ModelSerializer):
    """
    Serializer for KitchenStation model
    """
    outlet_name = serializers.CharField(source='outlet.name', read_only=True)
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KitchenStation
        fields = [
            'id', 'outlet', 'outlet_name', 'name', 'code', 
            'description', 'is_active', 'sort_order',
            'product_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_product_count(self, obj):
        """Get number of products assigned to this station"""
        return obj.products.filter(is_active=True).count()
    
    def validate(self, data):
        """Validate unique code per outlet"""
        outlet = data.get('outlet')
        code = data.get('code')
        
        if outlet and code:
            # Check for existing station with same code in same outlet
            qs = KitchenStation.objects.filter(outlet=outlet, code=code)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise serializers.ValidationError({
                    'code': f'Station with code "{code}" already exists in this outlet'
                })
        
        return data

