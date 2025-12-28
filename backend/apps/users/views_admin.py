"""
Admin views for User Management
"""
import logging
from rest_framework import viewsets, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.hashers import make_password
from django.db.models import Q, Count

from apps.users.models import User
from apps.users.serializers import UserSerializer
from apps.core.permissions import IsAdminOrTenantOwnerOrManager

logger = logging.getLogger(__name__)


class UserAdminSerializer(UserSerializer):
    """Extended user serializer for admin with write support"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    outlet_name = serializers.CharField(source='outlet.name', read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['tenant_name', 'outlet_name']
        read_only_fields = ['last_login', 'date_joined', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    Admin API for User Management
    
    Endpoints:
    - GET /api/admin/users/ - List users
    - POST /api/admin/users/ - Create user
    - GET /api/admin/users/{id}/ - Get user detail
    - PUT /api/admin/users/{id}/ - Update user
    - PATCH /api/admin/users/{id}/ - Partial update
    - DELETE /api/admin/users/{id}/ - Delete user
    - POST /api/admin/users/{id}/reset_password/ - Reset password
    - POST /api/admin/users/{id}/change_role/ - Change role
    - GET /api/admin/users/stats/ - User statistics
    """
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTenantOwnerOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'tenant', 'outlet']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering_fields = ['username', 'email', 'created_at', 'last_login', 'role']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter users based on role
        - Admin: sees all users
        - Tenant owner: sees users in their tenant
        - Others: see no users
        """
        user = self.request.user
        
        if user.role == 'admin':
            # Admin sees all users
            return User.objects.select_related('tenant', 'outlet').all()
        elif user.role == 'owner' and hasattr(user, 'tenant') and user.tenant:
            # Tenant owner sees users in their tenant
            return User.objects.filter(
                tenant=user.tenant
            ).select_related('tenant', 'outlet')
        else:
            # Others see no users
            return User.objects.none()
    
    def perform_create(self, serializer):
        """
        Create user with password hashing
        """
        password = serializer.validated_data.get('password')
        if password:
            serializer.validated_data['password'] = make_password(password)
        
        # Auto-assign tenant for non-admin creators
        user = self.request.user
        if user.role != 'admin' and hasattr(user, 'tenant') and user.tenant:
            serializer.validated_data['tenant'] = user.tenant
        
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Update user, handle password if provided
        """
        password = serializer.validated_data.get('password')
        if password:
            serializer.validated_data['password'] = make_password(password)
        else:
            # Don't update password if not provided
            serializer.validated_data.pop('password', None)
        
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Reset user password
        
        POST /api/admin/users/{id}/reset_password/
        Body: { "new_password": "newpass123" }
        """
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response(
                {'error': 'new_password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.password = make_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password reset successfully',
            'username': user.username
        })
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """
        Change user role
        
        POST /api/admin/users/{id}/change_role/
        Body: { "role": "cashier" }
        """
        user = self.get_object()
        new_role = request.data.get('role')
        
        if not new_role:
            return Response(
                {'error': 'role is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate role
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if new_role not in valid_roles:
            return Response(
                {'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_role = user.role
        user.role = new_role
        user.save()
        
        return Response({
            'message': 'Role changed successfully',
            'username': user.username,
            'old_role': old_role,
            'new_role': new_role
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        User statistics
        
        GET /api/admin/users/stats/
        """
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'inactive': queryset.filter(is_active=False).count(),
            'by_role': {}
        }
        
        # Count by role
        role_counts = queryset.values('role').annotate(count=Count('id'))
        for item in role_counts:
            role_label = dict(User.ROLE_CHOICES).get(item['role'], item['role'])
            stats['by_role'][item['role']] = {
                'count': item['count'],
                'label': role_label
            }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update users
        
        POST /api/admin/users/bulk_update/
        Body: {
            "user_ids": [1, 2, 3],
            "updates": {
                "is_active": true,
                ...
            }
        }
        """
        user_ids = request.data.get('user_ids', [])
        updates = request.data.get('updates', {})
        
        if not user_ids:
            return Response(
                {'error': 'No user IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not updates:
            return Response(
                {'error': 'No updates provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate users belong to accessible set
        users = self.get_queryset().filter(id__in=user_ids)
        
        if users.count() != len(user_ids):
            return Response(
                {'error': 'Some users not found or not accessible'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Don't allow password updates via bulk
        updates.pop('password', None)
        
        # Update users
        updated_count = users.update(**updates)
        
        return Response({
            'message': f'{updated_count} users updated successfully',
            'updated_count': updated_count
        })
