from rest_framework import viewsets
from .models import DriverProfile
from .serializers import DriverProfileSerializer

from rest_framework import permissions
from apps.accounts.permissions import IsOwnerOrAdmin, IsAdmin, IsDriver

class DriverProfileViewSet(viewsets.ModelViewSet):
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [IsAdmin()]
        if self.action == 'create':
            # Optionally allow any auth user to become a driver, or restrict
            return [permissions.IsAuthenticated()] 
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
