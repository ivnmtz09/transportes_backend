from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DriverProfileViewSet

router = DefaultRouter()
router.register(r'drivers', DriverProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
