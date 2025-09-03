from django.contrib import admin
from .models import CustomUser, Vehicle
from django.contrib.auth.admin import UserAdmin

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role Info", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("vehicle_number", "vehicle_type", "vehicle_model", "created_at")
    search_fields = ("vehicle_number", "vehicle_model")
    list_filter = ("vehicle_type",)
