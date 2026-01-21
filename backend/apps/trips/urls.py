from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, TripOfferViewSet, AvailableTripsView

router = DefaultRouter()
router.register(r'', TripViewSet, basename='trip')
router.register(r'offers', TripOfferViewSet)

urlpatterns = [
    path('available/', AvailableTripsView.as_view(), name='available-trips'),
    path('', include(router.urls)),
]
