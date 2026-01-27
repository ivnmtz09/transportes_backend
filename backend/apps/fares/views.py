from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.trips.services import RouteService
from .models import Fare
from .serializers import FareSerializer

class FareViewSet(viewsets.ModelViewSet):
    queryset = Fare.objects.all()
    serializer_class = FareSerializer

    @action(detail=False, methods=['post'])
    def estimate(self, request):
        try:
            origin_lat = float(request.data.get('origin_lat'))
            origin_lng = float(request.data.get('origin_lng'))
            dest_lat = float(request.data.get('dest_lat'))
            dest_lng = float(request.data.get('dest_lng'))
        except (TypeError, ValueError, KeyError):
            return Response(
                {"error": "Se requieren coordenadas válidas: origin_lat, origin_lng, dest_lat, dest_lng"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            route_info = RouteService.get_route_from_addresses(
                origin_lat, origin_lng, dest_lat, dest_lng
            )
            
            distance_km = route_info['distance'] / 1000.0
            
            # Lógica solicitada: MOTORCYCLE $3000, CAR $7000 base + $1000 por km
            vehicle_type = request.data.get('vehicle_type', 'CAR').upper()
            base_fare = 3000 if vehicle_type == 'MOTORCYCLE' else 7000
            per_km_rate = 1000
            
            estimated_price = base_fare + (distance_km * per_km_rate)
            
            # Redondear a la centena más cercana para un precio más "comercial"
            estimated_price = round(estimated_price / 100) * 100
            
            return Response({
                "estimated_price": int(estimated_price),
                "distance_km": round(distance_km, 2),
                "duration_mins": int(route_info['duration'] / 60.0),
                "currency": "COP"
            })
            
        except Exception as e:
            return Response(
                {"error": f"Error calculando ruta: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
