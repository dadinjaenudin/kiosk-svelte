"""
Authentication views for admin panel
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from apps.users.serializers import UserProfileSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Admin login endpoint
    
    POST /api/auth/login/
    {
        "username": "admin",
        "password": "password123"
    }
    
    Returns:
    {
        "token": "...",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "...",
            "role": "owner",
            ...
        }
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'message': 'Please provide both username and password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'message': 'User account is disabled'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check if user has admin access (not kitchen staff)
    if user.role == 'kitchen':
        return Response({
            'message': 'Kitchen staff cannot access admin panel'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get or create token
    token, created = Token.objects.get_or_create(user=user)
    
    # Serialize user data
    serializer = UserProfileSerializer(user)
    
    return Response({
        'token': token.key,
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Admin logout endpoint
    
    POST /api/auth/logout/
    
    Deletes the user's auth token
    """
    try:
        # Delete user's token
        request.user.auth_token.delete()
    except Exception as e:
        pass
    
    return Response({
        'message': 'Successfully logged out'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Get current authenticated user
    
    GET /api/auth/me/
    
    Returns current user data
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token_view(request):
    """
    Refresh authentication token
    
    POST /api/auth/refresh/
    
    Generates a new token for the user
    """
    # Delete old token
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    
    # Create new token
    token = Token.objects.create(user=request.user)
    
    return Response({
        'token': token.key
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change user password
    
    POST /api/auth/change-password/
    {
        "current_password": "old",
        "new_password": "new"
    }
    """
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not current_password or not new_password:
        return Response({
            'message': 'Please provide both current and new password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check current password
    if not request.user.check_password(current_password):
        return Response({
            'message': 'Current password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate new password
    if len(new_password) < 6:
        return Response({
            'message': 'New password must be at least 6 characters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Set new password
    request.user.set_password(new_password)
    request.user.save()
    
    # Refresh token
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    
    token = Token.objects.create(user=request.user)
    
    return Response({
        'message': 'Password changed successfully',
        'token': token.key
    }, status=status.HTTP_200_OK)
