from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Vehicle
import re

User = get_user_model()

class VehicleSerializer(serializers.ModelSerializer):
    # Permitir asignar conductores por ID, pero opcional
    drivers = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(),
        required=False
    )
    
    class Meta:
        model = Vehicle
        fields = '__all__'
        extra_kwargs = {
            'license_plate': {'validators': []}  # Remove default UniqueValidator
        }
    
    def create(self, validated_data):
        license_plate = validated_data.get('license_plate', '').upper().strip()
        user = self.context['request'].user
        
        # Intentar obtener el vehículo si ya existe
        vehicle = Vehicle.objects.filter(license_plate=license_plate).first()
        
        if vehicle:
            # Si el vehículo ya existe, agregamos al usuario actual como conductor
            if user.is_authenticated:
                vehicle.drivers.add(user)
            return vehicle
        
        # Si no existe, lo creamos normalmente
        # Extraemos drivers si vienen en el POST para manejarlos después
        drivers_data = validated_data.pop('drivers', [])
        vehicle = Vehicle.objects.create(**validated_data)
        
        # Agregar al usuario actual por defecto
        if user.is_authenticated:
            vehicle.drivers.add(user)
            
        # Agregar otros conductores si se especificaron
        if drivers_data:
            vehicle.drivers.add(*drivers_data)
            
        return vehicle

    def validate(self, data):
        """
        Validar que el formato de la placa coincida con el tipo de vehículo
        """
        license_plate = data.get('license_plate', '').upper().strip()
        vehicle_type = data.get('vehicle_type')
        
        if license_plate and vehicle_type:
            # Patrón para carros: 3 letras + 3 números
            car_pattern = r'^[A-Z]{3}\d{3}$'
            # Patrón para motos: 3 letras + 2 números + 1 letra
            motorcycle_pattern = r'^[A-Z]{3}\d{2}[A-Z]$'
            
            if vehicle_type == 'CAR':
                if not re.match(car_pattern, license_plate):
                    raise serializers.ValidationError({
                        'license_plate': 'Para un carro, la placa debe tener el formato ABC123 (3 letras + 3 números)'
                    })
            elif vehicle_type == 'MOTORCYCLE':
                if not re.match(motorcycle_pattern, license_plate):
                    raise serializers.ValidationError({
                        'license_plate': 'Para una moto, la placa debe tener el formato ABC12D (3 letras + 2 números + 1 letra)'
                    })
            
            # Normalizar la placa a mayúsculas
            data['license_plate'] = license_plate
        
        return data
