from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, GoogleLogin
from .api_views import health_check, test_connection, UserProfileView

router = DefaultRouter()
router.register(r'users', UserViewSet)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', include(router.urls)),
    
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Google OAuth
    path('google/', GoogleLogin.as_view(), name='google_login'),
    
    # Testing endpoints
    path('health/', health_check, name='health_check'),
    path('test/', test_connection, name='test_connection'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]
