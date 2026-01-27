from rest_framework import viewsets
from .models import DriverProfile
from .serializers import DriverProfileSerializer

from rest_framework import permissions
from apps.accounts.permissions import IsOwnerOrAdmin, IsAdmin, IsDriver

from rest_framework.decorators import action
from rest_framework.response import Response

class DriverProfileViewSet(viewsets.ModelViewSet):
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [IsAdmin()]
        if self.action in ['create', 'stats']:
            # Optionally allow any auth user to become a driver, or restrict
            return [permissions.IsAuthenticated()] 
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        return Response({
            "viajes_completados": 0,
            "calificacion": 5.0
        })
