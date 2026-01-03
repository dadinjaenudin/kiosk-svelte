"""
Views for User API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from apps.users.serializers import UserSerializer, UserProfileSerializer
from apps.core.context import get_current_tenant
from apps.core.permissions import (
    CanManageUsers,
    is_admin_user
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management
    
    list: List users in current tenant
    create: Create new user
    retrieve: Get user details
    update: Update user
    delete: Delete user
    me: Get current user info
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, CanManageUsers]
    
    def get_queryset(self):
        """
        Filter users by current tenant.
        Admin can see all users.
        """
        user = self.request.user
        
        # Admin can see all users
        if is_admin_user(user):
            return User.objects.all()
        
        tenant = get_current_tenant()
        
        if not tenant:
            return User.objects.none()
        
        return User.objects.filter(tenant=tenant, is_active=True)
    
    def get_serializer_class(self):
        """
        Use profile serializer for 'me' action
        """
        if self.action == 'me' or self.action == 'update_profile':
            return UserProfileSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        Get or update current user profile
        
        GET /api/users/me/
        PATCH /api/users/me/
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """
        List users (admin/manager only)
        """
        if not has_permission(request.user, 'user.view'):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        Create user (admin/owner only)
        """
        if not has_permission(request.user, 'user.create'):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Auto-set tenant
        tenant = get_current_tenant()
        if tenant:
            request.data['tenant'] = tenant.id
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Update user (admin/owner only)
        """
        if not has_permission(request.user, 'user.edit'):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete user (owner only)
        """
        if not has_permission(request.user, 'user.delete'):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Soft delete - set is_active to False
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
