from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

#  CUSTOM USER MODEL WITH ROLES
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("superadmin", "SuperAdmin"),
        ("admin","Admin"),
        ("user","user"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return f"{self.username} ({self.role})"
