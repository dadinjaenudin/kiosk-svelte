"""
Serializers for Tenant API
"""
from rest_framework import serializers
from apps.tenants.models import Tenant, Outlet, KitchenStation, KitchenStationType, Store, StoreOutlet


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for Store model - Physical retail store"""
    outlets_count = serializers.SerializerMethodField()
    active_outlets_count = serializers.SerializerMethodField()
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    tenant_id = serializers.IntegerField(source='tenant.id', read_only=True)
    
    class Meta:
        model = Store
        fields = [
            'id', 'tenant', 'tenant_id', 'tenant_name', 'code', 'name', 'address', 'city', 'province', 'postal_code',
            'latitude', 'longitude', 'kiosk_qr_code', 'enable_multi_outlet_payment',
            'payment_split_method', 'opening_time', 'closing_time', 'is_active', 
            'outlets_count', 'active_outlets_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['kiosk_qr_code', 'tenant_name', 'tenant_id', 'created_at', 'updated_at']
    
    def get_outlets_count(self, obj):
        # Query via StoreOutlet junction
        return obj.store_outlets.count()
    
    def get_active_outlets_count(self, obj):
        # Query via StoreOutlet junction where both store and outlet are active
        return obj.store_outlets.filter(
            is_active=True,
            outlet__is_active=True
        ).count()


class StoreDetailSerializer(StoreSerializer):
    """Detailed serializer with outlets list"""
    outlets = serializers.SerializerMethodField()
    
    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + ['outlets']
    
    def get_outlets(self, obj):
        # Query via StoreOutlet junction - active outlets at this store
        store_outlets = obj.store_outlets.filter(
            is_active=True,
            outlet__is_active=True
        ).select_related('outlet', 'outlet__tenant').order_by('display_order', 'outlet__brand_name')
        
        return [{
            'id': so.outlet.id,
            'brand_name': so.outlet.brand_name,
            'name': so.outlet.name,
            'slug': so.outlet.slug,
            'tenant_id': so.outlet.tenant.id,
            'tenant_name': so.outlet.tenant.name,
            'tenant_logo': so.outlet.tenant.logo.url if so.outlet.tenant.logo else None,
            'primary_color': so.outlet.tenant.primary_color,
            'secondary_color': so.outlet.tenant.secondary_color,
            # Use custom times from StoreOutlet if set, otherwise use Store's times
            'opening_time': str(so.custom_opening_time) if so.custom_opening_time else str(obj.opening_time) if obj.opening_time else None,
            'closing_time': str(so.custom_closing_time) if so.custom_closing_time else str(obj.closing_time) if obj.closing_time else None,
            'is_active': so.is_active,
            'display_order': so.display_order,
        } for so in store_outlets]


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
    Serializer for Outlet model - Global Brand (Many-to-Many with Store)
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    stores_count = serializers.SerializerMethodField()
    active_stores_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Outlet
        fields = [
            'id', 'tenant', 'tenant_name',
            'brand_name', 'name', 'slug',
            'phone', 'email',
            'websocket_url',
            'stores_count', 'active_stores_count',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'tenant_name', 'name', 'stores_count', 'active_stores_count', 'created_at']
    
    def get_stores_count(self, obj):
        """Get number of stores where this outlet/brand is available"""
        return obj.store_outlets.count()
    
    def get_active_stores_count(self, obj):
        """Get number of active stores where this outlet/brand is available"""
        return obj.store_outlets.filter(
            is_active=True,
            store__is_active=True
        ).count()
    
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


class StoreOutletSerializer(serializers.ModelSerializer):
    """
    Serializer for StoreOutlet junction model (Many-to-Many relationship)
    """
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_code = serializers.CharField(source='store.code', read_only=True)
    outlet_name = serializers.CharField(source='outlet.name', read_only=True)
    brand_name = serializers.CharField(source='outlet.brand_name', read_only=True)
    tenant_name = serializers.CharField(source='outlet.tenant.name', read_only=True)
    
    class Meta:
        model = StoreOutlet
        fields = [
            'id', 'store', 'store_name', 'store_code',
            'outlet', 'outlet_name', 'brand_name', 'tenant_name',
            'is_active', 'custom_opening_time', 'custom_closing_time',
            'display_order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'store_name', 'store_code', 'outlet_name', 'brand_name', 'tenant_name', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure unique store-outlet combination"""
        store = data.get('store')
        outlet = data.get('outlet')
        
        if store and outlet:
            # Check for existing assignment
            qs = StoreOutlet.objects.filter(store=store, outlet=outlet)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise serializers.ValidationError({
                    'outlet': f'Outlet "{outlet.brand_name}" is already assigned to store "{store.name}"'
                })
        
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
    
    class Meta:
        model = KitchenStation
        fields = [
            'id', 'outlet', 'outlet_name', 'name', 'code', 
            'description', 'is_active', 'sort_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
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


class KitchenStationTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for KitchenStationType model
    """
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, allow_null=True)
    
    class Meta:
        model = KitchenStationType
        fields = [
            'id',
            'tenant',
            'tenant_name',
            'name',
            'code',
            'description',
            'icon',
            'color',
            'is_active',
            'is_global',
            'sort_order',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'tenant_name']
    
    def validate(self, data):
        """
        Ensure either tenant or is_global is set, but not both
        """
        tenant = data.get('tenant')
        is_global = data.get('is_global', False)
        
        if is_global and tenant:
            raise serializers.ValidationError(
                "Global types cannot be assigned to a specific tenant"
            )
        
        if not is_global and not tenant:
            raise serializers.ValidationError(
                "Non-global types must be assigned to a tenant"
            )
        
        return data
    
    def validate_code(self, value):
        """
        Ensure code is uppercase and alphanumeric
        """
        if not value.replace('_', '').isalnum() or not value.isupper():
            raise serializers.ValidationError(
                "Code must be uppercase alphanumeric only (e.g., MAIN, BEVERAGE)"
            )
        return value

