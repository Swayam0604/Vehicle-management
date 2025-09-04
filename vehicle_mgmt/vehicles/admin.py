from django.contrib import admin
from .models import  Vehicle
from django.contrib.auth.admin import UserAdmin

# Register your models here.


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("vehicle_number", "vehicle_type", "vehicle_model", "created_at")
    search_fields = ("vehicle_number", "vehicle_model")
    list_filter = ("vehicle_type",)
