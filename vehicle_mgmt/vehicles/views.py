from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Vehicle
from .forms import VehicleForm
from django.core.mail import send_mail
from django.contrib import messages
import random
from django.conf import settings
# Create your views here.

# CUSTOM ROLE-BASED ACCESS MIXIN
class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []
    permission_denied_message = "You don't have permission to access this page."
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in self.allowed_roles
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return redirect('vehicle_list')
        else:
            return redirect('login')
#  VEHICLE LIST VIEW (ALL ROLES CAN VIEW)
class VehicleListView(LoginRequiredMixin,RoleRequiredMixin,ListView):
    model = Vehicle
    template_name = 'vehicles/list.html'
    context_object_name = 'vehicles'
    allowed_roles = ["superadmin", "admin", "user"]

# MAPING URL TO TEMPLATE (VIEW)
def vehicle_list(request):
    vehicles = Vehicle.objects.all()

    # COUNT VEHICLES BY TYPE
    two_wheeler_count = Vehicle.objects.filter(vehicle_type='Two').count()
    three_wheeler_count = Vehicle.objects.filter(vehicle_type='Three').count()
    four_wheeler_count = Vehicle.objects.filter(vehicle_type='Four').count()

    context = {
        'vehicles' : vehicles,
        'two_wheeler_count' : two_wheeler_count,
        'three_wheeler_count' : three_wheeler_count,
        'four_wheeler_count' : four_wheeler_count
    }
    return render(request,"vehicles/list.html",context)

# VEHICLE DETAIL VIEW (ALL ROLES CAN VIEW)
class VehicleDetailView(LoginRequiredMixin,RoleRequiredMixin,DetailView):
    model = Vehicle
    template_name = 'vehicles/detail.html'
    context_object_name = 'vehicle'
    allowed_roles = ["superadmin", "admin", "user"]

# MAPING URL TO TEMPLATE (VIEW)
def vehicle_detail(request,pk):
    vehicle = get_object_or_404(Vehicle,pk=pk)
    return render(request,"vehicles/detail.html",{"vehicle":vehicle})

# VEHICLE CREATE VIEW (ONLY SUPERADMIN)
class VehicleCreateView(LoginRequiredMixin,RoleRequiredMixin,CreateView):
    model = Vehicle
    template_name = 'vehicles/form.html'
    fields = ['vehicle_number','vehicle_type','vehicle_model','vehicle_description']
    allowed_roles = ["superadmin"]
    success_url = reverse_lazy('vehicle_list')

# MAPING URL TO TEMPLATE (VIEW)
def vehicle_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request,"vehicles/form.html",{"form":form,"form_title":"Add Vehicle"})
    

# VEHICLE UPDATE VIEW (ONLY SUPERADMIN + ADMIN)
class VehicleUpdateView(LoginRequiredMixin,RoleRequiredMixin,UpdateView):
    model = Vehicle
    fields = ["vehicle_number","vehicle_type","vehicle_model","vehicle_description"]
    template_name = 'vehicles/form.html'
    allowed_roles = ["superadmin", "admin"]
    success_url = reverse_lazy('vehicle_list')

# MAPING URL TO TEMPLATE (VIEW)
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect("vehicle_list")
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, "vehicles/form.html", {"form": form, "form_title": "Edit Vehicle"})

# VEHICLE DELETE VIEW (ONLY SUPERADMIN)
class VehicleDeleteView(LoginRequiredMixin,RoleRequiredMixin,DeleteView):
    model = Vehicle
    template_name = 'vehicles/delete.html'
    allowed_roles = ["superadmin"]
    success_url = reverse_lazy('vehicle_list')

# MAPING URL TO TEMPLATE (VIEW)
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == "POST":
        vehicle.delete()
        return redirect("vehicle_list")
    return render(request, "vehicles/delete.html", {"vehicle": vehicle})

