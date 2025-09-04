from django.urls import path
from . import views

urlpatterns = [
    path("",views.vehicle_list,name="vehicle_list"),
    path("add/",views.VehicleCreateView.as_view(),name="vehicle_add"),
    path("<int:pk>/",views.VehicleDetailView.as_view(),name="vehicle_detail"),
    path("<int:pk>/edit",views.VehicleUpdateView.as_view(),name="vehicle_edit"),
    path("<int:pk>/delete/",views.VehicleDeleteView.as_view(),name="vehicle_delete"),
]
