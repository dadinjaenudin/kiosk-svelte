"""
Serializers for User API
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.permissions import ROLE_HIERARCHY

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with multi-outlet support
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    outlet_name = serializers.CharField(source='outlet.name', read_only=True)
    role_level = serializers.SerializerMethodField()
    accessible_outlets = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'phone_number',
            'tenant', 'tenant_name',
            'outlet', 'outlet_name', 'accessible_outlets',
            'role', 'role_level',
            'is_active', 'is_staff', 'is_superuser',
            'last_login', 'created_at'
        ]
        read_only_fields = [
            'id', 'username', 'tenant', 'tenant_name',
            'outlet_name', 'accessible_outlets', 'role_level',
            'is_staff', 'is_superuser', 'last_login', 'created_at'
        ]
    
    def get_role_level(self, obj):
        """
        Get user's role hierarchy level for frontend
        """
        if obj.is_superuser:
            return 100
        return ROLE_HIERARCHY.get(obj.role, 0)
    
    def get_accessible_outlets(self, obj):
        """
        Get list of outlets accessible to this user
        """
        # Super admin and admin can access all outlets
        if obj.role in ['super_admin', 'admin']:
            return 'all'
        
        # Tenant owner can access all outlets in tenant
        if obj.role == 'tenant_owner' and obj.tenant:
            from apps.tenants.serializers import OutletSerializer
            outlets = obj.tenant.outlets.filter(is_active=True)
            return OutletSerializer(outlets, many=True).data
        
        # Manager can access their accessible_outlets
        if obj.role == 'manager':
            from apps.tenants.serializers import OutletSerializer
            outlets = obj.accessible_outlets.filter(is_active=True)
            return OutletSerializer(outlets, many=True).data
        
        # Cashier/kitchen: return their primary outlet only
        if obj.outlet:
            from apps.tenants.serializers import OutletSerializer
            return [OutletSerializer(obj.outlet).data]
        
        return []


class UserProfileSerializer(UserSerializer):
    """
    Serializer for user profile (with password change)
    """
    
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['old_password', 'new_password']
    
    def validate(self, data):
        """
        Validate password change
        """
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if new_password and not old_password:
            raise serializers.ValidationError({
                'old_password': 'Old password is required to set new password'
            })
        
        if old_password and not new_password:
            raise serializers.ValidationError({
                'new_password': 'New password is required'
            })
        
        if old_password and new_password:
            user = self.instance
            if not user.check_password(old_password):
                raise serializers.ValidationError({
                    'old_password': 'Incorrect password'
                })
        
        return data
    
    def update(self, instance, validated_data):
        """
        Update user with password change support
        """
        old_password = validated_data.pop('old_password', None)
        new_password = validated_data.pop('new_password', None)
        
        # Update user fields
        user = super().update(instance, validated_data)
        
        # Change password if provided
        if new_password:
            user.set_password(new_password)
            user.save()
        
        return user
