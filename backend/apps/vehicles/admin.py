from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('driver', 'make', 'model', 'year', 'license_plate')
    search_fields = ('driver__user__username', 'make', 'model', 'license_plate')
