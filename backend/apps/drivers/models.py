from django.db import models
from django.conf import settings

class DriverProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    # Add other fields like documents later

    def __str__(self):
        return f"Driver: {self.user.username}"
