from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from apps.drivers.models import DriverProfile


def validate_license_plate(value):
    """
    Validador personalizado para placas de vehículos colombianas.
    - Carros: 3 letras seguidas de 3 números (Ej: ABC123)
    - Motos: 3 letras, 2 números y termina en 1 letra (Ej: ABC12D)
    """
    import re
    
    # Convertir a mayúsculas para validación
    value = value.upper().strip()
    
    # Patrón para carros: 3 letras + 3 números
    car_pattern = r'^[A-Z]{3}\d{3}$'
    # Patrón para motos: 3 letras + 2 números + 1 letra
    motorcycle_pattern = r'^[A-Z]{3}\d{2}[A-Z]$'
    
    if not (re.match(car_pattern, value) or re.match(motorcycle_pattern, value)):
        from django.core.exceptions import ValidationError
        raise ValidationError(
            'La placa debe tener el formato: ABC123 (carro) o ABC12D (moto). '
            'Exactamente 6 caracteres.'
        )


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        CAR = 'CAR', 'Car'
        MOTORCYCLE = 'MOTORCYCLE', 'Motorcycle'
    
    # Cambiado a ManyToManyField para que un vehículo tenga varios conductores
    drivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='vehicles')
    
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices, default=VehicleType.CAR)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField(null=True, blank=True)
    license_plate = models.CharField(
        max_length=6, 
        unique=True,
        validators=[validate_license_plate],
        help_text='Formato: ABC123 (carro) o ABC12D (moto)'
    )
    color = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False, help_text='Indica si este vehículo está activo para el conductor')
    
    def save(self, *args, **kwargs):
        # Asegurar que los campos se guarden en MAYÚSCULAS
        if self.make:
            self.make = self.make.upper().strip()
        if self.model:
            self.model = self.model.upper().strip()
        if self.color:
            self.color = self.color.upper().strip()
        if self.license_plate:
            self.license_plate = self.license_plate.upper().strip()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"
