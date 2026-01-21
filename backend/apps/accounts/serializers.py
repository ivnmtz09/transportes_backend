from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    vehicles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'password', 'profile_picture', 'phone_number', 'vehicles']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'required': False}  # Allow role to be editable
        }

    def get_vehicles(self, obj):
        """
        Retorna la lista de vehículos si el usuario es un conductor.
        """
        if obj.role == User.Role.DRIVER:
            from apps.vehicles.serializers import VehicleSerializer
            return VehicleSerializer(obj.vehicles.all(), many=True).data
        return []

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        """
        Update user instance and handle role changes.
        If role changes to DRIVER, automatically create DriverProfile if it doesn't exist.
        """
        # Check if role is being changed to DRIVER
        new_role = validated_data.get('role', instance.role)
        
        # Update user fields
        for attr, value in validated_data.items():
            if attr != 'password':
                setattr(instance, attr, value)
        
        # Handle password update separately if provided
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        instance.save()
        
        # If role is DRIVER, ensure DriverProfile exists
        if new_role == User.Role.DRIVER:
            from apps.drivers.models import DriverProfile
            
            # Check if DriverProfile already exists
            if not hasattr(instance, 'driver_profile'):
                # Create DriverProfile with PENDING status
                DriverProfile.objects.create(
                    user=instance,
                    license_number='',  # Empty initially, to be filled later
                    is_verified=False  # PENDING status
                )
        
        return instance


class CustomSocialLoginSerializer(serializers.Serializer):
    """
    Custom serializer for social login response.
    Returns JWT tokens along with user data.
    """
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        """
        Return user data including role.
        """
        user = self.context.get('request').user
        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'phone_number': user.phone_number,
        }
