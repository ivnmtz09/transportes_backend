from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Vehicle
from .serializers import VehicleSerializer

from rest_framework import permissions
from apps.accounts.permissions import IsOwnerOrAdmin, IsAdmin, IsDriver

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_permissions(self):
        if self.action == 'list':
            # Use list of permission instances.
            return [permissions.IsAuthenticated(), (IsDriver | IsAdmin)()]
        if self.action in ['create', 'set_active']:
            return [(IsDriver | IsAdmin)()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or (hasattr(user, 'role') and user.role == 'ADMIN'):
            return Vehicle.objects.all()
        # Filtrar vehículos donde el usuario actual sea uno de los conductores
        return Vehicle.objects.filter(drivers=user)

    @action(detail=True, methods=['post', 'patch'], url_path='set-active')
    def set_active(self, request, pk=None):
        """
        Activa este vehículo y desactiva todos los demás del mismo conductor.
        PATCH /api/v1/vehicles/{id}/set-active/
        """
        vehicle = self.get_object()
        user = request.user
        
        # Verificar que el usuario sea uno de los conductores del vehículo
        if not vehicle.drivers.filter(id=user.id).exists():
            return Response(
                {"error": "No tienes permiso para activar este vehículo"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Desactivar todos los vehículos del conductor
        Vehicle.objects.filter(drivers=user).update(is_active=False)
        
        # Activar el vehículo seleccionado
        vehicle.is_active = True
        vehicle.save()
        
        serializer = self.get_serializer(vehicle)
        return Response(serializer.data)
