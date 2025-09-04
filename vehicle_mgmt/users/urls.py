from django.urls import path,include 
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("verify-otp/<str:username>/", views.verify_otp, name="verify_otp"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
