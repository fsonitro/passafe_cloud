from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    name = forms.CharField(max_length=30, required=True, label="First Name")
    surname = forms.CharField(max_length=30, required=True, label="Last Name")
    pin = forms.CharField(max_length=8, required=True, widget=forms.PasswordInput, help_text="Enter an 8-digit PIN")

    class Meta:
        model = CustomUser
        fields = ('name', 'surname', 'email', 'password1', 'password2', 'pin')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check for existing user with this email
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

# Custom Login Form
class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email Address",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control wide-input',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    pin = forms.CharField(
        max_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control pin-input',
            'placeholder': 'PIN'
        }),
        label="8-digit PIN"
    )

    def clean_pin(self):
        pin = self.cleaned_data.get('pin')
        if len(pin) != 8 or not pin.isdigit():
            raise forms.ValidationError("The PIN must be exactly 8 digits.")
        return pin


# Forgot Password Form
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(required=True, label="Email Address")

# Verify the Reset Code Form
class VerifyResetCodeForm(forms.Form):
    reset_token = forms.CharField(max_length=100, required=True, label="Reset Code")

# Password Reset Form
class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput, 
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Confirm New Password"
    )
    current_pin = forms.CharField(
        widget=forms.PasswordInput, 
        label="Current PIN", 
        max_length=8
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        
        return cleaned_data
    
# Account Settings Form
class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'surname']  # Only include editable fields here

# Enable MFA Form
class EnableMFAForm(forms.Form):
    mfa_code = forms.CharField(max_length=6, required=True, label="Enter the code from your authenticator app")
