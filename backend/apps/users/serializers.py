"""
Serializers for User API
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.permissions import get_user_permissions

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    outlet_name = serializers.CharField(source='default_outlet.name', read_only=True)
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'phone_number',
            'tenant', 'tenant_name',
            'default_outlet', 'outlet_name',
            'role', 'permissions',
            'is_active', 'is_staff', 'is_superuser',
            'last_login', 'created_at'
        ]
        read_only_fields = [
            'id', 'username', 'tenant', 'tenant_name',
            'outlet_name', 'permissions',
            'is_staff', 'is_superuser', 'last_login', 'created_at'
        ]
    
    def get_permissions(self, obj):
        """
        Get user's permissions list
        """
        return get_user_permissions(obj)


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
