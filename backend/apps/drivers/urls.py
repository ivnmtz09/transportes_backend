from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DriverProfileViewSet

router = DefaultRouter()
router.register(r'', DriverProfileViewSet, basename='driverprofile')

urlpatterns = [
    path('', include(router.urls)),
]
