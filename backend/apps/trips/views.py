from rest_framework import viewsets, permissions, status, generics, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from .models import Trip, TripOffer
from .serializers import (
    TripSerializer, TripOfferSerializer, TripOfferCreateSerializer,
    TripAvailableSerializer
)
from .services import RouteService
from apps.accounts.permissions import IsOwnerOrAdmin, IsClient, IsDriver, IsAdmin


class AvailableTripsView(generics.ListAPIView):
    """
    Vista para que los conductores vean viajes disponibles (REQUESTED y sin conductor)
    """
    queryset = Trip.objects.filter(status='REQUESTED', driver__isnull=True)
    serializer_class = TripAvailableSerializer
    permission_classes = [permissions.IsAuthenticated, (IsDriver | IsAdmin)]


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
        queryset = Trip.objects.all()
        
        if hasattr(user, 'role') and user.role in ['DRIVER', 'ADMIN']:
            # Para conductores: mostrar viajes dentro de 5km de radio
            # Obtener la ubicación actual del conductor desde los parámetros
            driver_lat = self.request.query_params.get('lat')
            driver_lng = self.request.query_params.get('lng')
            
            if driver_lat and driver_lng:
                try:
                    driver_location = Point(float(driver_lng), float(driver_lat), srid=4326)
                    
                    # Filtrar viajes REQUESTED dentro de 5km usando DWithin
                    queryset = Trip.objects.filter(
                        status='REQUESTED',
                        origin_location__dwithin=(driver_location, D(km=5))
                    ).annotate(
                        distance=Distance('origin_location', driver_location)
                    ).order_by('distance')
                except (ValueError, TypeError):
                    # Si las coordenadas son inválidas, mostrar todos los REQUESTED
                    queryset = Trip.objects.filter(status='REQUESTED')
            else:
                # Si no se proporcionan coordenadas, mostrar todos los REQUESTED
                queryset = Trip.objects.filter(status='REQUESTED')
            
            # También incluir los viajes que el conductor ha aceptado
            queryset = queryset | Trip.objects.filter(driver__user=user)
        else:
            # Para clientes: solo sus propios viajes
            queryset = Trip.objects.filter(client=user)
        
        return queryset.distinct()
    
    @action(detail=True, methods=['post'], permission_classes=[(IsDriver | IsAdmin)])
    def offer(self, request, pk=None):
        """
        Endpoint para que un conductor haga una oferta en un viaje
        POST /trips/{id}/offer/
        Body: {
            "offered_price": 15000,
            "estimated_arrival_time": 10
        }
        """
        trip = self.get_object()
        
        # Verificar que el viaje esté en estado REQUESTED
        if trip.status != Trip.Status.REQUESTED:
            return Response(
                {'error': 'Solo se pueden hacer ofertas en viajes con estado REQUESTED'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener el perfil del conductor
        try:
            driver_profile = request.user.driver_profile
        except:
            return Response(
                {'error': 'El usuario no tiene un perfil de conductor'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya existe una oferta de este conductor para este viaje
        existing_offer = TripOffer.objects.filter(trip=trip, driver=driver_profile).first()
        if existing_offer:
            return Response(
                {'error': 'Ya has hecho una oferta para este viaje'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear la oferta
        serializer = TripOfferCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(trip=trip, driver=driver_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[IsClient])
    def offers(self, request, pk=None):
        """
        Endpoint para que un cliente vea todas las ofertas de un viaje
        GET /trips/{id}/offers/
        """
        trip = self.get_object()
        
        # Verificar que el cliente sea el dueño del viaje
        if trip.client != request.user:
            return Response(
                {'error': 'No tienes permiso para ver las ofertas de este viaje'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        offers = trip.offers.all()
        serializer = TripOfferSerializer(offers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def get_route(self, request):
        """
        Endpoint para obtener la ruta entre origen y destino
        POST /trips/get_route/
        Body: {
            "origin_lat": 11.5444,
            "origin_lng": -72.9072,
            "dest_lat": 11.5500,
            "dest_lng": -72.9100
        }
        """
        origin_lat = request.data.get('origin_lat')
        origin_lng = request.data.get('origin_lng')
        dest_lat = request.data.get('dest_lat')
        dest_lng = request.data.get('dest_lng')
        
        if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
            return Response(
                {'error': 'Se requieren origin_lat, origin_lng, dest_lat y dest_lng'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            route_data = RouteService.get_route_from_addresses(
                float(origin_lat), float(origin_lng),
                float(dest_lat), float(dest_lng)
            )
            return Response(route_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TripOfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las ofertas
    """
    queryset = TripOffer.objects.all()
    serializer_class = TripOfferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Al crear una oferta, asociamos automáticamente al conductor actual
        user = self.request.user
        if hasattr(user, 'driver_profile'):
            serializer.save(driver=user.driver_profile)
        elif user.role == 'ADMIN':
            # Si es admin pero no tiene perfil, quizás deberíamos crearlo o error
            # Por consistencia con la DB, necesita un DriverProfile
            from apps.drivers.models import DriverProfile
            profile, _ = DriverProfile.objects.get_or_create(
                user=user,
                defaults={'license_number': 'ADMIN', 'is_verified': True}
            )
            serializer.save(driver=profile)
        else:
            raise serializers.ValidationError({"error": "El usuario no tiene un perfil de conductor"})
    
    @action(detail=True, methods=['post'], permission_classes=[IsClient])
    def accept(self, request, pk=None):
        """
        Endpoint para que un cliente acepte una oferta
        POST /offers/{id}/accept/
        """
        offer = self.get_object()
        trip = offer.trip
        
        # Verificar que el cliente sea el dueño del viaje
        if trip.client != request.user:
            return Response(
                {'error': 'No tienes permiso para aceptar ofertas de este viaje'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que el viaje esté en estado REQUESTED
        if trip.status != Trip.Status.REQUESTED:
            return Response(
                {'error': 'Solo se pueden aceptar ofertas en viajes con estado REQUESTED'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que la oferta esté en estado PENDING
        if offer.status != TripOffer.OfferStatus.PENDING:
            return Response(
                {'error': 'Esta oferta ya ha sido procesada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Aceptar la oferta
        offer.status = TripOffer.OfferStatus.ACCEPTED
        offer.save()
        
        # Actualizar el viaje
        trip.driver = offer.driver
        trip.status = Trip.Status.ACCEPTED
        trip.save()
        
        # Rechazar todas las demás ofertas
        TripOffer.objects.filter(trip=trip).exclude(id=offer.id).update(
            status=TripOffer.OfferStatus.REJECTED
        )
        
        return Response({
            'message': 'Oferta aceptada exitosamente',
            'offer': TripOfferSerializer(offer).data,
            'trip': TripSerializer(trip).data
        })
