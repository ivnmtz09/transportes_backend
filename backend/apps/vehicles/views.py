from rest_framework import viewsets
from .models import Vehicle
from .serializers import VehicleSerializer

from rest_framework import permissions
from apps.accounts.permissions import IsOwnerOrAdmin, IsAdmin, IsDriver

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdmin()] # Or allow drivers to see their own? Queryset filtering is better for that.
        if self.action == 'create':
            return [IsDriver()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or (hasattr(user, 'role') and user.role == 'ADMIN'):
            return Vehicle.objects.all()
        # Filtrar vehículos donde el usuario actual sea uno de los conductores
        return Vehicle.objects.filter(drivers=user)
