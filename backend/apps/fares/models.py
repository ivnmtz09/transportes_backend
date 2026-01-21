from django.db import models
from apps.trips.models import Trip

class Fare(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='fare')
    
    # Tarifas Base según el tipo de vehículo (en COP)
    BASE_FARES = {
        'MOTORCYCLE': 3000,
        'CAR': 7000
    }
    
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    surcharge_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=2000) # Ejemplo: $2000 por KM
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio final calculado")
    currency = models.CharField(max_length=3, default='COP')
    
    def save(self, *args, **kwargs):
        # Si no se ha definido la tarifa base, la asignamos según el tipo de vehículo del viaje
        if self.base_fare == 0:
            v_type = self.trip.vehicle_type
            self.base_fare = self.BASE_FARES.get(v_type, 7000)
            
        # Cálculo del precio final: Base + (distancia * recargo)
        self.amount = self.base_fare + (self.distance_km * self.surcharge_per_km)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.amount} {self.currency} for Trip {self.trip.id} ({self.trip.vehicle_type})"
