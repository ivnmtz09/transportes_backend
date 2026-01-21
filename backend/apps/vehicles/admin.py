from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('get_drivers', 'make', 'model', 'year', 'license_plate')
    search_fields = ('drivers__username', 'make', 'model', 'license_plate')
    
    def get_drivers(self, obj):
        return ", ".join([d.username for d in obj.drivers.all()])
    get_drivers.short_description = 'Drivers'
