from django.db import models
from apps.trips.models import Trip

class Fare(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='fare')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    def __str__(self):
        return f"{self.amount} {self.currency} for Trip {self.trip.id}"
