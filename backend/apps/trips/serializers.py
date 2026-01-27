from rest_framework import serializers
from .models import Trip, TripOffer, Rating

class TripSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar información del cliente y conductor
    client_email = serializers.EmailField(source='client.email', read_only=True)
    driver_email = serializers.EmailField(source='driver.user.email', read_only=True, allow_null=True)
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    
    # Campos de geolocalización como lat/lng obligatorios
    pickup_latitude = serializers.FloatField(
        write_only=True, 
        required=True,
        error_messages={'required': 'Falta la latitud de origen (pickup_latitude)'}
    )
    pickup_longitude = serializers.FloatField(
        write_only=True, 
        required=True,
        error_messages={'required': 'Falta la longitud de origen (pickup_longitude)'}
    )
    destination_latitude = serializers.FloatField(
        write_only=True, 
        required=True,
        error_messages={'required': 'Falta la latitud de destino (destination_latitude)'}
    )
    destination_longitude = serializers.FloatField(
        write_only=True, 
        required=True,
        error_messages={'required': 'Falta la longitud de destino (destination_longitude)'}
    )
    
    vehicle_type = serializers.ChoiceField(choices=Trip.VehicleType.choices, required=True)
    
    # Campo service_type con mapeo de español a inglés
    service_type = serializers.CharField(
        required=True,
        error_messages={'required': 'El campo service_type es obligatorio (VIAJE/TRIP o DOMICILIO/DELIVERY)'}
    )
    
    pickup_address = serializers.CharField(
        required=True,
        error_messages={'required': 'Falta la dirección de origen (pickup_address)'}
    )
    destination_address = serializers.CharField(
        required=True,
        error_messages={'required': 'Falta la dirección de destino (destination_address)'}
    )
    
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ('client', 'created_at', 'updated_at')
    
    def validate_service_type(self, value):
        """
        Mapea valores en español a los valores de la base de datos en inglés.
        """
        # Mapeo de español a inglés
        mapping = {
            'VIAJE': 'TRIP',
            'DOMICILIO': 'DELIVERY',
            'TRIP': 'TRIP',
            'DELIVERY': 'DELIVERY'
        }
        
        value_upper = value.upper().strip()
        
        if value_upper not in mapping:
            raise serializers.ValidationError(
                f"Valor inválido '{value}'. Debe ser: VIAJE/TRIP o DOMICILIO/DELIVERY"
            )
        
        return mapping[value_upper]
    
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
        # Usamos el estimated_price propuesto por el cliente como base
        Fare.objects.create(
            trip=trip, 
            amount=trip.estimated_price,
            base_fare=trip.estimated_price
        )
        
        return trip


    def update(self, instance, validated_data):
        from django.contrib.gis.geos import Point
        
        # Extraer coordenadas si existen
        pickup_lat = validated_data.pop('pickup_latitude', None)
        pickup_lng = validated_data.pop('pickup_longitude', None)
        dest_lat = validated_data.pop('destination_latitude', None)
        dest_lng = validated_data.pop('destination_longitude', None)
        
        # Actualizar puntos de geolocalización
        if pickup_lat is not None and pickup_lng is not None:
            instance.origin_location = Point(pickup_lng, pickup_lat, srid=4326)
        if dest_lat is not None and dest_lng is not None:
            instance.destination_location = Point(dest_lng, dest_lat, srid=4326)
            
        # Actualizar el resto de campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Sincronizar estimated_price con la Fare si ha cambiado
        if 'estimated_price' in validated_data:
            if hasattr(instance, 'fare'):
                instance.fare.amount = instance.estimated_price
                instance.fare.save()
        
        return instance

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
            'estimated_price', 'vehicle_type', 'service_type', 'service_type_display', 'status', 'created_at'
        )


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ('rater', 'created_at')
