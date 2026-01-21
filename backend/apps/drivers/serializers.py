from rest_framework import serializers
from .models import DriverProfile

class DriverProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = DriverProfile
        fields = ['id', 'user', 'username', 'license_number', 'is_verified']
        read_only_fields = ['is_verified'] 
