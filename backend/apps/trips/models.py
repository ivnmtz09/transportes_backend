from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from apps.drivers.models import DriverProfile

class Trip(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    class VehicleType(models.TextChoices):
        CAR = 'CAR', 'Car'
        MOTORCYCLE = 'MOTORCYCLE', 'Motorcycle'
    
    class ServiceType(models.TextChoices):
        TRIP = 'TRIP', 'Viaje'
        DELIVERY = 'DELIVERY', 'Domicilio'

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trips_as_client')
    driver = models.ForeignKey(DriverProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips_as_driver')
    
    pickup_address = models.CharField(max_length=255)
    destination_address = models.CharField(max_length=255)
    service_type = models.CharField(max_length=20, choices=ServiceType.choices, default=ServiceType.TRIP)
    
    # PostGIS fields for geolocation (SRID 4326 = WGS84, used by GPS)
    origin_location = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    destination_location = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices, default=VehicleType.CAR)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Trip {self.id} - {self.status}"


class TripOffer(models.Model):
    """
    Modelo para manejar las ofertas/subastas de los conductores para un viaje
    """
    class OfferStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='offers')
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='trip_offers')
    
    offered_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_arrival_time = models.IntegerField(help_text="Tiempo estimado de llegada en minutos")
    
    status = models.CharField(max_length=20, choices=OfferStatus.choices, default=OfferStatus.PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Un conductor solo puede hacer una oferta por viaje
        unique_together = ('trip', 'driver')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Offer by {self.driver.user.email} for Trip {self.trip.id} - ${self.offered_price}"


class Rating(models.Model):
    """
    Sistema de calificaciones al finalizar un viaje
    """
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='rating')
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_given')
    rated_driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='ratings_received')
    
    stars = models.IntegerField(default=5, help_text="Calificación de 0 a 5 estrellas")
    comment = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Rating for {self.rated_driver.user.email}: {self.stars} stars"
