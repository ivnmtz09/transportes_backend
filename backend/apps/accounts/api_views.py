from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint to verify server is running.
    Useful for testing connectivity from mobile devices.
    """
    return Response({
        'status': 'ok',
        'message': 'Backend is running successfully',
        'server': 'Django REST Framework',
        'endpoints': {
            'health': '/api/health/',
            'google_login': '/api/accounts/google/login/',
            'users': '/api/accounts/users/',
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_connection(request):
    """
    Test endpoint to verify CORS and network connectivity.
    Returns client IP and request headers.
    """
    client_ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    return Response({
        'status': 'success',
        'message': 'Connection successful from mobile device',
        'client_ip': client_ip,
        'user_agent': user_agent,
        'cors_enabled': True,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_profile(request):
    """
    Get current user profile with role information.
    Requires authentication.
    """
    user = request.user
    
    profile_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'phone_number': user.phone_number,
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
    }
    
    # Add profile-specific data
    if user.role == User.Role.CLIENT and hasattr(user, 'client_profile'):
        profile_data['profile_type'] = 'client'
        profile_data['profile_id'] = user.client_profile.id
    elif user.role == User.Role.DRIVER and hasattr(user, 'driver_profile'):
        profile_data['profile_type'] = 'driver'
        profile_data['profile_id'] = user.driver_profile.id
        profile_data['is_verified'] = user.driver_profile.is_verified
    
    return Response(profile_data, status=status.HTTP_200_OK)
