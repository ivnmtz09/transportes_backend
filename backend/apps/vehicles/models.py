from django.db import models
from apps.drivers.models import DriverProfile

class Vehicle(models.Model):
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='vehicles')
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"
