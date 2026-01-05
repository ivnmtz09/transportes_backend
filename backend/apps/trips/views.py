from rest_framework import viewsets, permissions
from .models import Trip
from .serializers import TripSerializer

from apps.accounts.permissions import IsOwnerOrAdmin, IsClient, IsDriver

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsClient()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'DRIVER':
            # Drivers can see requested trips or their own accepted trips
            return Trip.objects.filter(status='REQUESTED') | Trip.objects.filter(driver__user=user)
        return Trip.objects.filter(client=user)
