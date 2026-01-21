from django.contrib import admin
from .models import Fare

@admin.register(Fare)
class FareAdmin(admin.ModelAdmin):
    list_display = ('trip', 'amount', 'currency')
    search_fields = ('trip__id',)
