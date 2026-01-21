from rest_framework import serializers
from .models import Trip, TripOffer, Rating

class TripSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar información del cliente y conductor
    client_email = serializers.EmailField(source='client.email', read_only=True)
    driver_email = serializers.EmailField(source='driver.user.email', read_only=True, allow_null=True)
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    
    # Campos de geolocalización como lat/lng
    pickup_latitude = serializers.FloatField(write_only=True, required=False)
    pickup_longitude = serializers.FloatField(write_only=True, required=False)
    destination_latitude = serializers.FloatField(write_only=True, required=False)
    destination_longitude = serializers.FloatField(write_only=True, required=False)
    
    vehicle_type = serializers.ChoiceField(choices=Trip.VehicleType.choices, required=True)
    
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ('client', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        from django.contrib.gis.geos import Point
        from apps.fares.models import Fare
        
        # Extraer coordenadas si existen
        pickup_lat = validated_data.pop('pickup_latitude', None)
        pickup_lng = validated_data.pop('pickup_longitude', None)
        dest_lat = validated_data.pop('destination_latitude', None)
        dest_lng = validated_data.pop('destination_longitude', None)
        
        # Crear el trip
        trip = Trip.objects.create(**validated_data)
        
        # Asignar puntos de geolocalización si se proporcionaron
        if pickup_lat and pickup_lng:
            trip.origin_location = Point(pickup_lng, pickup_lat, srid=4326)
        if dest_lat and dest_lng:
            trip.destination_location = Point(dest_lng, dest_lat, srid=4326)
        
        trip.save()
        
        # Crear automáticamente la tarifa inicial para el viaje
        # La distancia se asume 0 por ahora o se puede calcular si se desea
        Fare.objects.create(trip=trip)
        
        return trip


class TripOfferSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.user.get_full_name', read_only=True)
    driver_email = serializers.EmailField(source='driver.user.email', read_only=True)
    
    class Meta:
        model = TripOffer
        fields = '__all__'
        read_only_fields = ('driver', 'status', 'created_at', 'updated_at')
    
    def validate(self, data):
        trip = data.get('trip')
        request = self.context.get('request')
        
        if trip and trip.status != Trip.Status.REQUESTED:
            raise serializers.ValidationError("Solo se pueden hacer ofertas en viajes con estado REQUESTED")
        
        if request and request.user:
            try:
                driver_profile = request.user.driver_profile
                # Verificar si ya existe una oferta de este conductor para este viaje
                if TripOffer.objects.filter(trip=trip, driver=driver_profile).exists():
                    raise serializers.ValidationError("Ya has hecho una oferta para este viaje")
            except:
                pass # Will be handled by perform_create in ViewSet if profile is missing

        # Validar que el precio sea positivo
        if data.get('offered_price') and data['offered_price'] <= 0:
            raise serializers.ValidationError({"offered_price": "El precio ofrecido debe ser mayor a 0"})
        
        # Validar que el tiempo estimado sea positivo
        if data.get('estimated_arrival_time') and data['estimated_arrival_time'] <= 0:
            raise serializers.ValidationError({"estimated_arrival_time": "El tiempo estimado debe ser mayor a 0"})
        
        return data


class TripOfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer específico para crear ofertas
    """
    class Meta:
        model = TripOffer
        fields = ('offered_price', 'estimated_arrival_time')
    
    def validate(self, data):
        if data['offered_price'] <= 0:
            raise serializers.ValidationError("El precio ofrecido debe ser mayor a 0")
        
        if data['estimated_arrival_time'] <= 0:
            raise serializers.ValidationError("El tiempo estimado debe ser mayor a 0")
        
        return data


class TripAvailableSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    fare_amount = serializers.DecimalField(source='fare.amount', max_digits=10, decimal_places=2, read_only=True)
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    
    class Meta:
        model = Trip
        fields = (
            'id', 'client_name', 'pickup_address', 'destination_address', 
            'fare_amount', 'vehicle_type', 'service_type', 'service_type_display', 'status', 'created_at'
        )


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ('rater', 'created_at')
