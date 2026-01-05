from django.db import models
from django.conf import settings

class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile')
    # Add preferences, saved addresses later

    def __str__(self):
        return f"Client: {self.user.username}"
