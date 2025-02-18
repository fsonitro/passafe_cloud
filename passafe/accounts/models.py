from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.conf import settings
from django.utils import timezone

# Custom User Model
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=254)  # Ensure max_length is adequate
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    pin = models.CharField(max_length=128, help_text="8-digit PIN for multi-factor authentication")
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light',
    )

    # Encryption Key and Salt
    encryption_key = models.TextField(null=True, blank=True)  # To store the derived encryption key if required
    salt = models.TextField(null=True, blank=True)  # To store the unique salt for each user

    # Email Token Password Reset
    reset_token = models.CharField(max_length=6, blank=True, null=True)  # Adjusted for 6-digit tokens
    token_expiry = models.DateTimeField(blank=True, null=True)

    # MFA Fields 
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)

    def set_pin(self, raw_pin): 
        self.pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)
    
    def __str__(self):
        return self.email  # Display email as a string representation of the user

# Login Activity Model
class LoginActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    # location = models.CharField(max_length=255, null=True, blank=True)  # optional
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Login by {self.user.email} at {self.timestamp}"
