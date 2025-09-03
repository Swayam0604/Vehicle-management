from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Vehicle

# Create your views here.

# CUSTOM ROLE-BASED ACCESS MIXIN
class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles
    
#  VEHICLE LIST VIEW (ALL ROLES CAN VIEW)
class VehicleListView(LoginRequiredMixin,RoleRequiredMixin,ListView):
    model = Vehicle
    template_name = 'vehicles/list.html'
    context_object_name = 'vehicles'
    allowed_roles = ["superadmin", "admin", "user"]


# VEHICLE DETAIL VIEW (ALL ROLES CAN VIEW)
class VehicleDetailView(LoginRequiredMixin,RoleRequiredMixin,DetailView):
    model = Vehicle
    template_name = 'vehicles/detail.html'
    context_object_name = 'vehicle'
    allowed_roles = ["superadmin", "admin", "user"]

# VEHICLE CREATE VIEW (ONLY SUPERADMIN)
class VehicleCreateView(LoginRequiredMixin,RoleRequiredMixin,CreateView):
    model = Vehicle
    template_name = 'vehicles/form.html'
    fields = ['vehicle_number','vehicle_type','vehicle_model','vehicle_description']
    allowed_roles = ["superadmin"]
    success_url = reverse_lazy('vehicles_list')

# VEHICLE UPDATE VIEW (ONLY SUPERADMIN + ADMIN)
class VehicleUpdateView(LoginRequiredMixin,RoleRequiredMixin,UpdateView):
    model = Vehicle
    fields = ["vehicle_number","vehicle_type","vehicle_model","vehicle_description"]
    template_name = 'vehicles/form.html'
    allowed_roles = ["superadmin", "admin"]
    success_url = reverse_lazy('vehicles_list')


# VEHICLE DELETE VIEW (ONLY SUPERADMIN)
class VehicleDeleteView(LoginRequiredMixin,RoleRequiredMixin,DeleteView):
    model = Vehicle
    template_name = 'vehicles/delete.html'
    allowed_roles = ["superadmin"]
    success_url = reverse_lazy('vehicles_list')
