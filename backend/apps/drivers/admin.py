from django.contrib import admin
from .models import DriverProfile

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'user__email', 'license_number')
