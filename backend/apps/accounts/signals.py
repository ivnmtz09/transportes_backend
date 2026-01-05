from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically assign CLIENT role and create ClientProfile
    when a user registers (including via Google OAuth).
    """
    if created:
        # Ensure user has a role (default to CLIENT if not set)
        if not instance.role:
            instance.role = User.Role.CLIENT
            instance.save(update_fields=['role'])
        
        # Create ClientProfile for CLIENT users
        if instance.role == User.Role.CLIENT:
            from apps.clients.models import ClientProfile
            ClientProfile.objects.get_or_create(user=instance)
        
        # Create DriverProfile for DRIVER users
        elif instance.role == User.Role.DRIVER:
            from apps.drivers.models import DriverProfile
            DriverProfile.objects.get_or_create(
                user=instance,
                defaults={'license_number': '', 'is_verified': False}
            )
