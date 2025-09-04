from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login as auth_login , logout
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import random
import logging
from django.conf import settings
from .forms import CustomUserRegistrationForm, CustomLoginForm
from .models import CustomUser

logger = logging.getLogger(__name__)
# TEMPORARY STORING THE OTP'S (BETTER USE CACHE /REDIS IN REAL APPS)
otp_storage = {}

# Your existing register function...
def register(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False  # DEACTIVATE UNTIL OTP IS VERIFIED
                    user.save()

                    # GENERATE OTP 
                    otp = random.randint(100000, 999999)
                    otp_storage[user.username] = {
                        'otp': otp,
                        'attempts': 0,
                        'email': user.email  # Store email for verification
                    }

                    # SEND OTP VIA EMAIL
                    email_sent = send_otp_email(user, otp)
                    
                    if email_sent:
                        messages.success(request, f"Registration successful! OTP sent to {user.email}. Please verify to activate your account.")
                        return redirect("verify_otp", username=user.username)
                    else:
                        messages.error(request, "Registration completed, but failed to send OTP email. Please contact support.")
                        
            except Exception as e:
                logger.error(f"Registration error: {e}")
                messages.error(request, "Registration failed. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, "users/register.html", {"form": form})

# ADD THIS MISSING verify_otp FUNCTION:
def verify_otp(request, username):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        
        if username in otp_storage:
            stored_data = otp_storage[username]
            stored_otp = stored_data['otp']
            attempts = stored_data.get('attempts', 0)
            
            if attempts >= 3:
                messages.error(request, "Too many failed attempts. Please register again.")
                del otp_storage[username]
                return redirect("register")
            
            if str(stored_otp) == entered_otp:
                try:
                    user = CustomUser.objects.get(username=username)
                    user.is_active = True
                    user.save()
                    del otp_storage[username]  # REMOVE OTP FROM STORAGE
                    messages.success(request, "Your account has been activated successfully! Please login.")
                    return redirect("login")
                except CustomUser.DoesNotExist:
                    messages.error(request, "User not found.")
                    return redirect("register")
            else:
                # Increment attempts
                otp_storage[username]['attempts'] = attempts + 1
                remaining_attempts = 3 - (attempts + 1)
                messages.error(request, f"Invalid OTP. {remaining_attempts} attempts remaining.")
        else:
            messages.error(request, "OTP expired or invalid. Please register again.")
            return redirect("register")
    
    return render(request, "users/verify_otp.html", {"username": username})

# ADD THIS MISSING login FUNCTION:
def login(request):
    form = CustomLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login_input = form.cleaned_data.get("login")  # username or email
        password = form.cleaned_data.get("password")

        try:
            user_obj = CustomUser.objects.get(Q(username=login_input) | Q(email=login_input))
            user = authenticate(request, username=user_obj.username, password=password)
        except CustomUser.DoesNotExist:
            user = None

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("vehicle_list")  # Redirect after login
            else:
                messages.error(request, "Your account is not activated. Please check your email for OTP verification.")
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, "users/login.html", {"form": form})

# Your existing send_otp_email function...
def send_otp_email(user, otp):
    """Send OTP email with better formatting and error handling"""
    try:
        subject = "Vehicle Management System - Account Verification"
        message = f"""
Hello {user.username},

Welcome to Vehicle Management System!

Your account verification code is: {otp}

Please enter this code to activate your account. This code is valid for 10 minutes.

Account Details:
- Username: {user.username}
- Email: {user.email}
- Role: {user.get_role_display()}

If you didn't create this account, please ignore this email.

Best regards,
Vehicle Management Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {e}")
        return False


@login_required
def logout_view(request):
    """Custom logout view with success message"""
    username = request.user.username
    logout(request)
    messages.success(request, f"Goodbye {username}! You have been logged out successfully.")
    return redirect("login")
