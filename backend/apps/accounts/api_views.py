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


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user profile with role information.
    Requires authentication.
    Supports GET and PATCH methods.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """
        Return the authenticated user's profile.
        """
        return self.request.user
