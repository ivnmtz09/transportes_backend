from django.contrib import admin
from .models import Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'driver', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__username', 'driver__user__username', 'origin_address', 'destination_address')
