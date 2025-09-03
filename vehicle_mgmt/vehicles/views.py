from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Vehicle, CustomUser
from .forms import VehicleForm, CustomUserRegistrationForm
from django.core.mail import send_mail
from django.contrib import messages
import random
from django.conf import settings
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

# MAPING URL TO TEMPLATE (VIEW)
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    return render(request,"vehicles/list.html",{"vehicles":vehicles})

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


#  TEMPORARY STORING THE OTP'S (BETTER USE CACHE /REDIS IN REAL APPS)
otp_storage = {}

def register(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False   # DEACTIVATE UNTIL OTP IS VERIFIED
            user.save()

            # GENERATE OTP 
            otp = random.randint(100000, 999999)
            otp_storage[user.username] = otp

            # SEND OTP VIA EMAIL
            send_mail(
                subject="Your OTP for Vehicle Management System",
                message=f"Hello {user.username}, your OTP is {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect("verify_otp", username=user.username)
    else:
        form = CustomUserRegistrationForm()
    return render(request, "users/register.html", {"form": form})

def verify_otp(request, username):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        if username in otp_storage and str(otp_storage[username]) == entered_otp:
            user = CustomUser.objects.get(username=username)
            user.is_active = True
            user.save()
            del otp_storage[username]  # REMOVE OTP FROM STORAGE CLEANUP
            messages.success(request, "Your account has been activated. Please login.")
            return redirect("login")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    return render(request, "users/verify_otp.html", {"username": username})