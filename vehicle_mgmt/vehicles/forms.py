from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Vehicle,CustomUser
class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "vehicle_number",
            "vehicle_type",
            "vehicle_model",
            "vehicle_description",
            ]
        
class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")
