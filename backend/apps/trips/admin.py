from django.contrib import admin
from .models import Trip, TripOffer, Rating

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'driver', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__username', 'driver__user__username', 'pickup_address', 'destination_address')


@admin.register(TripOffer)
class TripOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip', 'driver', 'offered_price', 'estimated_arrival_time', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('trip__id', 'driver__user__username', 'driver__user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip', 'rater', 'rated_driver', 'stars', 'created_at')
    list_filter = ('stars', 'created_at')
    search_fields = ('trip__id', 'rater__username', 'rated_driver__user__username')
    readonly_fields = ('created_at',)
