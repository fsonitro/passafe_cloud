from django.shortcuts import render, redirect
from password_vault.models import Folder, PasswordEntry
from password_vault.utils import check_password_strength, find_reused_passwords, decrypt_data
from django.contrib.auth.decorators import login_required
from collections import Counter
from django.contrib import messages
import base64
import datetime
from django.views.generic import TemplateView

# Helper function to retrieve the encryption key
def get_encryption_key(request):
    encoded_key = request.session.get('encryption_key')
    if not encoded_key:
        messages.error(request, "Your session has expired. Please log in again.")
        return None
    return base64.urlsafe_b64decode(encoded_key)

@login_required
def homepage(request):
    user = request.user
    theme = user.theme_preference  # Get the user's theme preference

    # Total Password Entries
    total_entries = PasswordEntry.objects.filter(user=user).count()

    # Folders Overview
    folders = Folder.objects.filter(user=user).prefetch_related('entries')
    folder_data = [
        {
            'name': folder.name,
            'entry_count': folder.entries.count(),
        }
        for folder in folders
    ]

    # Recent Activity
    recent_entries = PasswordEntry.objects.filter(user=user).order_by('-modified_at')[:5]

    # Retrieve encryption key
    derived_key = get_encryption_key(request)
    if not derived_key:
        return redirect('accounts:login')

    # Decrypt passwords
    decrypted_passwords = []
    for entry in PasswordEntry.objects.filter(user=user):
        try:
            encrypted_data = {
                'ciphertext': entry.encrypted_password,
                'iv': entry.iv,
                'tag': entry.tag,
            }
            decrypted_password = decrypt_data(derived_key, encrypted_data)
            decrypted_passwords.append(decrypted_password)
        except Exception:
            # Handle decryption errors gracefully
            continue

    # Weak Passwords
    weak_passwords = [pwd for pwd in decrypted_passwords if check_password_strength(pwd) == 'weak']

    # Reused Passwords
    reused_passwords = find_reused_passwords(decrypted_passwords)

    # Strength Distribution
    strength_distribution = Counter([check_password_strength(pwd) for pwd in decrypted_passwords])

    # Security Tips (general advice)
    general_tips = [
        "Use unique passwords for each account.",
        "Enable two-factor authentication for added security.",
        "Update your passwords regularly.",
        "Avoid using personal information in your passwords.",
        "Monitor your accounts for unusual activity.",
    ]

    # Rotate the tip based on the current day
    current_day = datetime.datetime.now().day  # Get the day of the month
    security_tip = general_tips[current_day % len(general_tips)]

 # Suggestions (actionable insights based on user's data)
    suggestions = []
    if weak_passwords:
        suggestions.append("You have weak passwords. Update them to improve security.")
    if reused_passwords:
        suggestions.append("You have reused passwords. Use unique passwords for each account.")
    if not user.mfa_enabled:
        suggestions.append("Enable two-factor authentication (2FA) for added security.")

    context = {
        'first_name': user.first_name,
        'theme': theme,
        'security_tip': security_tip,
        'suggestions': suggestions,
        'total_entries': total_entries,
        'folder_data': folder_data,
        'recent_entries': recent_entries,
        'weak_count': len(weak_passwords),
        'reused_count': len(reused_passwords),
        'strength_distribution': strength_distribution,
    }

    return render(request, 'hub/homepage.html', context)

class HeroView(TemplateView):
    template_name = 'hub/hero.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('hub:homepage')
        return super().dispatch(request, *args, **kwargs)
