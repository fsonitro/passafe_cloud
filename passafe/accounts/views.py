import base64
import csv
import json
import logging
import pyotp
import qrcode
import random
import traceback
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import (
    AccountSettingsForm, CustomLoginForm, CustomUserCreationForm,
    EnableMFAForm, ForgotPasswordForm, ResetPasswordForm,
    VerifyResetCodeForm
)
from .models import CustomUser, LoginActivity
from password_vault.models import Folder, PasswordEntry
from password_vault.utils import decrypt_data, derive_key, encrypt_data, generate_salt
from password_vault.views import get_encryption_key

logger = logging.getLogger(__name__)

# set_theme view function
@require_POST
@csrf_exempt  # See note below on CSRF
def set_theme(request):
    data = json.loads(request.body)
    theme = data.get("theme")
    if theme in ["light", "dark"]:
        if request.user.is_authenticated:
            request.user.theme_preference = theme
            request.user.save()
            return JsonResponse({"success": True})
        else:
            # Save theme preference in session for anonymous users
            request.session['theme'] = theme
            return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid theme"}, status=400)

# user_logout view function
def user_logout(request):
    request.session.pop('encryption_key', None)  # Clear encryption key from session
    logout(request)
    return redirect('hub:hero')

# store_encryption_key function
def store_encryption_key(request, password, pin, salt):
    """Derive and store the encryption key in the session."""
    if not (password and pin and salt):
        raise ValueError("Password, PIN, and salt are required to derive the encryption key.")
    derived_key = derive_key(password, pin, salt)
    request.session['encryption_key'] = base64.urlsafe_b64encode(derived_key).decode()
    request.session.modified = True  # Mark the session as modified to ensure saving

# register view function
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            pin = form.cleaned_data.get('pin')

            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'accounts/register.html', {'form': form})

            user = form.save(commit=False)
            user.username = email
            user.pin = make_password(pin)  # Hash the PIN before saving
            salt = generate_salt()
            user.salt = base64.urlsafe_b64encode(salt).decode()
            derived_key = derive_key(password, pin, salt)  # Use the plain PIN temporarily
            user.encryption_key = base64.urlsafe_b64encode(derived_key).decode()
            user.save()

            login(request, user, backend='accounts.backends.EmailBackend')
            send_mail(
                'Welcome to PasSafe!',
                'Thank you for registering with PasSafe.',
                'passafedonotreply@yourdomain.com',
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Registration successful! Welcome to PasSafe.')
            return redirect('hub:homepage')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# get client IP address
def get_client_ip(request):
    """
    Retrieve the client IP address from the request headers.
    Adjust if you're behind a proxy and need to parse X-Forwarded-For.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# user_login view function
def user_login(request):
    theme = request.session.get('theme', 'light')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            pin = form.cleaned_data.get('pin')
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if check_password(pin, user.pin):  # Verify the entered PIN against the hashed value
                    if user.mfa_enabled:
                        # Store password and pin in the session temporarily for MFA
                        request.session['mfa_user_id'] = user.id
                        request.session['password'] = password  # Store the plain password
                        request.session['pin'] = pin  # Store the plain PIN
                        return redirect('accounts:verify_mfa')
                    else:
                        salt = base64.urlsafe_b64decode(user.salt.encode())
                        store_encryption_key(request, password, pin, salt)  # Pass the plain PIN here
                        login(request, user)

                        # Record login activity
                        ip_address = get_client_ip(request)
                        user_agent = request.META.get('HTTP_USER_AGENT', '')
                        LoginActivity.objects.create(
                            user=user,
                            ip_address=ip_address,
                            user_agent=user_agent,
                            # location=None  # Or set if using a geolocation lookup
                        )

                        return redirect('hub:homepage')
                else:
                    form.add_error('pin', "Invalid PIN.")
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'theme': theme})

# forgot_password_request view function
def forgot_password_request(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                token = f"{random.randint(100000, 999999)}"
                user.reset_token = token
                user.token_expiry = timezone.now() + timezone.timedelta(minutes=15)
                user.save()

                send_mail(
                    'Password Reset Request for PasSafe',
                    f'Use this code to reset your password: {token}',
                    'noreply@yourdomain.com',
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'A reset code has been sent to your email.', extra_tags='forgot_password')
                return redirect('accounts:verify_reset_code')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No account with that email exists.', extra_tags='forgot_password')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password_request.html', {'form': form})

# verify_reset_code view function
def verify_reset_code(request):
    if request.method == 'POST':
        form = VerifyResetCodeForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['reset_token']
            try:
                user = CustomUser.objects.get(reset_token=token, token_expiry__gte=timezone.now())
                request.session['verified_user_id'] = user.id
                return redirect('accounts:reset_password')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid or expired reset code.')
    else:
        form = VerifyResetCodeForm()
    return render(request, 'accounts/verify_reset_code.html', {'form': form})

# reset_password view function
def reset_password(request):
    user_id = request.session.get('verified_user_id')
    if not user_id:
        return redirect('accounts:forgot_password_request')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            # Get the current PIN from the form
            current_pin = form.cleaned_data.get('current_pin')
            if not current_pin:
                messages.error(request, "Current PIN is required to re-encrypt your vault entries.")
                return redirect('accounts:reset_password')
            
            user = CustomUser.objects.get(id=user_id)
            # Validate the current PIN using the helper method from the model
            if not user.check_pin(current_pin):
                messages.error(request, "The current PIN you entered is incorrect.")
                return redirect('accounts:reset_password')
            
            try:
                # Decode the stored salt
                salt = base64.urlsafe_b64decode(user.salt.encode())
            except Exception as e:
                messages.error(request, "Invalid salt format. Cannot update credentials.")
                return redirect('accounts:reset_password')
            
            try:
                # Retrieve the old encryption key from the user's stored value
                old_key = base64.urlsafe_b64decode(user.encryption_key.encode())
            except Exception as e:
                messages.error(request, "Stored encryption key is corrupted.")
                return redirect('accounts:reset_password')
            
            # Derive a new encryption key using the new password and the verified current PIN
            new_key = derive_key(new_password, current_pin, salt)
            
            try:
                with transaction.atomic():
                    entries = PasswordEntry.objects.filter(user=user)
                    for entry in entries:
                        encrypted_data = {
                            'ciphertext': entry.encrypted_password,
                            'iv': entry.iv,
                            'tag': entry.tag
                        }
                        try:
                            # Decrypt with the old key
                            decrypted_password = decrypt_data(old_key, encrypted_data)
                        except Exception as decryption_error:
                            logger.error("Failed to decrypt entry ID %s: %s", entry.id, traceback.format_exc())
                            raise Exception(f"Failed to decrypt entry ID {entry.id}: {str(decryption_error)}")
                        
                        try:
                            # Encrypt using the new key
                            new_encryption = encrypt_data(new_key, decrypted_password)
                        except Exception as encryption_error:
                            logger.error("Failed to encrypt entry ID %s: %s", entry.id, traceback.format_exc())
                            raise Exception(f"Failed to encrypt entry ID {entry.id}: {str(encryption_error)}")
                        
                        entry.encrypted_password = new_encryption['ciphertext']
                        entry.iv = new_encryption['iv']
                        entry.tag = new_encryption['tag']
                        entry.save()
                    
                    # Update the user's password and stored encryption key
                    user.password = make_password(new_password)
                    user.encryption_key = base64.urlsafe_b64encode(new_key).decode()
                    user.reset_token = None
                    user.token_expiry = None
                    user.save()
                    
                    messages.success(request, "Your credentials have been reset successfully.")
                    return redirect('accounts:login')
            except Exception as e:
                error_details = traceback.format_exc()
                logger.error("Credential reset failed:\n%s", error_details)
                messages.error(request, f"An error occurred during credential reset: {str(e)}")
                return redirect('accounts:reset_password')
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'accounts/reset_password.html', {'form': form})
    else:
        form = ResetPasswordForm()
        return render(request, 'accounts/reset_password.html', {'form': form})


# account_settings view function
@login_required
def account_settings(request):
    user = request.user
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            form.save()
            messages.success(request, 'Your account details have been updated successfully.', extra_tags='account_settings')
            return redirect('accounts:account_settings')
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags='account_settings')
    else:
        form = AccountSettingsForm(instance=user)

    # Generate QR code if MFA is not enabled
    qr_image = None
    if not user.mfa_enabled:
        if not user.mfa_secret:
            user.mfa_secret = pyotp.random_base32()
            user.save()
        
        totp = pyotp.TOTP(user.mfa_secret)
        qr_url = totp.provisioning_uri(name=user.email, issuer_name="PasSafe")
        qr = qrcode.make(qr_url)
        stream = BytesIO()
        qr.save(stream, format="PNG")
        qr_image = base64.b64encode(stream.getvalue()).decode("utf-8")

    return render(request, 'accounts/account_settings.html', {
        'form': form,
        'email': user.email,
        'qr_image': qr_image,  # Pass this to the template
        'profile_picture': user.profile_picture.url if user.profile_picture else None,  # Handle profile picture
    })

# enable_mfa view function
@login_required
def enable_mfa(request):
    user = request.user

    # Generate a TOTP secret if the user doesn’t have one
    if not user.mfa_secret:
        user.mfa_secret = pyotp.random_base32()
        user.save()

    # Generate a QR code for the TOTP secret
    totp = pyotp.TOTP(user.mfa_secret)
    qr_url = totp.provisioning_uri(name=user.email, issuer_name="PasSafe")
    qr = qrcode.make(qr_url)
    stream = BytesIO()
    qr.save(stream, format="PNG")
    qr_image = base64.b64encode(stream.getvalue()).decode("utf-8")  # Encode the image to base64

    if request.method == 'POST':
        mfa_code = request.POST.get("mfa_code")
        if totp.verify(mfa_code):
            user.mfa_enabled = True
            user.save()
            messages.success(request, "MFA has been enabled successfully.", extra_tags="account_settings")
            return redirect('accounts:account_settings')
        else:
            messages.error(request, "Invalid MFA code. Please try again.", extra_tags="account_settings")

    return render(request, 'accounts/account_settings.html', {'qr_image': qr_image})

# verify_mfa view function
def verify_mfa(request):
    user_id = request.session.get('mfa_user_id')
    if not user_id:
        return redirect('accounts:login')

    user = CustomUser.objects.get(id=user_id)
    totp = pyotp.TOTP(user.mfa_secret)

    if request.method == 'POST':
        mfa_code = request.POST.get('mfa_code')
        if totp.verify(mfa_code):
            # Retrieve password and pin from the session
            password = request.session.pop('password', None)
            pin = request.session.pop('pin', None)

            if not (password and pin):  # Handle missing values
                messages.error(request, "Session data is incomplete. Please log in again.")
                return redirect('accounts:login')

            # Derive and store encryption key
            salt = base64.urlsafe_b64decode(user.salt.encode())
            store_encryption_key(request, password, pin, salt)

            # Login user and clear MFA session key
            login(request, user, backend='accounts.backends.EmailBackend')
            del request.session['mfa_user_id']

            # Redirect to the 'next' parameter if present, otherwise the dashboard
            next_url = request.GET.get('next', 'homepage')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid MFA code. Please try again.", extra_tags="verify_mfa")

    return render(request, 'accounts/verify_mfa.html')

# disable_mfa view function
@login_required
def disable_mfa(request):
    user = request.user
    user.mfa_enabled = False
    user.mfa_secret = None  # Clear the TOTP secret
    user.save()
    messages.success(request, "MFA has been disabled.")
    return redirect('accounts:account_settings')

@login_required
def export_passwords(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="passwords.csv"'

    writer = csv.writer(response)
    writer.writerow(['Folder', 'Title', 'Username', 'Password', 'Created At', 'Last Modified'])

    # Retrieve the encryption key from the session
    derived_key = get_encryption_key(request)
    if not derived_key:
        messages.error(request, "Encryption key not found; please log in again.")
        return redirect('accounts:login')

    # Write password entries without folders
    entries = PasswordEntry.objects.filter(user=request.user, folder__isnull=True)
    for entry in entries:
        encrypted_data = {'ciphertext': entry.encrypted_password, 'iv': entry.iv, 'tag': entry.tag}
        try:
            decrypted_password = decrypt_data(derived_key, encrypted_data)
        except Exception as e:
            decrypted_password = f"Error decrypting: {str(e)}"
        writer.writerow(['Ungrouped', entry.title, entry.username, decrypted_password, entry.created_at, entry.modified_at])

    # Write password entries within folders
    folders = Folder.objects.filter(user=request.user)
    for folder in folders:
        entries = PasswordEntry.objects.filter(folder=folder)
        for entry in entries:
            encrypted_data = {'ciphertext': entry.encrypted_password, 'iv': entry.iv, 'tag': entry.tag}
            try:
                decrypted_password = decrypt_data(derived_key, encrypted_data)
            except Exception as e:
                decrypted_password = f"Error decrypting: {str(e)}"
            writer.writerow([folder.name, entry.title, entry.username, decrypted_password, entry.created_at, entry.modified_at])

    return response

# account_activities view function
@login_required
def account_activities(request):
    user = request.user
    activities = LoginActivity.objects.filter(user=user).order_by('-timestamp')
    return render(request, 'accounts/account_activities.html', {
        'activities': activities
    })
