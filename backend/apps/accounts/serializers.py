from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    vehicles = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'password', 'profile_picture', 'phone_number', 
            'vehicles', 'stats', 'is_admin'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'required': False},
            'phone_number': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def get_is_admin(self, obj):
        return obj.is_staff or obj.role == User.Role.ADMIN

    def get_vehicles(self, obj):
        """
        Retorna la lista de vehículos si el usuario es un conductor o admin.
        """
        if obj.role in [User.Role.DRIVER, User.Role.ADMIN]:
            from apps.vehicles.serializers import VehicleSerializer
            # Si es admin, quizás quiera ver todos? Por ahora, los asociados.
            return VehicleSerializer(obj.vehicles.all(), many=True).data
        return []

    def get_stats(self, obj):
        """
        Retorna estadísticas según el rol.
        """
        if obj.role in [User.Role.DRIVER, User.Role.ADMIN]:
            # Por ahora devolvemos los datos estáticos solicitados
            return {
                "viajes_completados": 0,
                "calificacion": 5.0
            }
        # Para CLIENT devolvemos ceros
        return {
            "viajes_completados": 0,
            "calificacion": 0.0
        }

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
