from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

from rest_framework import permissions
from .permissions import IsOwnerOrAdmin, IsAdmin

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action == 'list':
            return [IsAdmin()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomSocialLoginSerializer

class GoogleLogin(SocialLoginView):
    """
    Google OAuth2 Login View.
    Returns JWT tokens and user data upon successful authentication.
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    # Asegúrate de que esta URL sea exactamente la que pusiste en la consola
    callback_url = "http://127.0.0.1:8000/accounts/google/login/callback/"

    def get_response(self):
        """
        Override to return custom response with JWT tokens and user data.
        """
        serializer_class = self.get_response_serializer()
        
        # Get JWT tokens
        refresh = RefreshToken.for_user(self.user)
        
        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
        
        serializer = CustomSocialLoginSerializer(
            instance=data,
            context={'request': self.request}
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)
