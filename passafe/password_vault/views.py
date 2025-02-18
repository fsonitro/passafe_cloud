import logging
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Folder, PasswordEntry
from .forms import FolderForm, PasswordEntryForm
from .utils import encrypt_data, decrypt_data
import base64
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


# Helper function to retrieve and decode encryption key from the session
def get_encryption_key(request):
    encoded_key = request.session.get('encryption_key')
    if not encoded_key:
        return None
    return base64.urlsafe_b64decode(encoded_key)

# View to create a new folder
@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user
            folder.save()
            messages.success(request, "Folder created successfully!", extra_tags="dashboard")
            return redirect('password_vault:vault_dashboard')
    else:
        form = FolderForm()
    return render(request, 'password_vault/create_folder.html', {'form': form})

# View to edit an existing folder
@login_required
def edit_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder)
        if form.is_valid():
            form.save()
            messages.success(request, "Folder edited successfully!", extra_tags="dashboard")
            return redirect('password_vault:vault_dashboard')
    else:
        form = FolderForm(instance=folder)
    return render(request, 'password_vault/edit_folder.html', {'form': form, 'folder': folder})

# View to delete an existing folder
@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    if request.method == 'POST':
        folder.delete()
        messages.success(request, "Folder deleted successfully!", extra_tags="dashboard")
        return redirect('password_vault:vault_dashboard')
    return render(request, 'password_vault/delete_folder.html', {'folder': folder})

# View to create a new password entry without a folder
@login_required
def create_entry_no_folder(request):
    return create_entry(request, folder_id=None)

# View to create a new password entry
@login_required
def create_entry(request, folder_id=None):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user) if folder_id else None
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.folder = folder

            # Retrieve the derived encryption key from the session
            derived_key = get_encryption_key(request)
            if not derived_key:
                messages.error(request, "Encryption key not found; please log in again.")
                return redirect('accounts:login')

            # Encrypt the `password_entry` from the form
            password_to_encrypt = form.cleaned_data['password_entry']
            encrypted_data = encrypt_data(derived_key, password_to_encrypt)
            
            # Store encrypted data in `encrypted_password` field and related fields
            entry.encrypted_password = encrypted_data['ciphertext']
            entry.iv = encrypted_data['iv']
            entry.tag = encrypted_data['tag']
            entry.save()

            messages.success(request, "Password entry created successfully!", extra_tags="dashboard")
            return redirect('password_vault:vault_dashboard')
    else:
        form = PasswordEntryForm()

    return render(request, 'password_vault/create_entry.html', {'form': form, 'folder': folder, 'is_grouped': bool(folder)})

# View to edit an existing password entry
@login_required
def edit_entry(request, entry_id):
    # Retrieve the password entry instance
    entry = get_object_or_404(PasswordEntry, id=entry_id, user=request.user)

    # Retrieve the encryption key from the session
    encoded_key = request.session.get('encryption_key')
    if not encoded_key:
        messages.error(request, "Your session has expired. Please log in again.")
        return redirect('accounts:login')
    
    # Decode the key from base64
    derived_key = base64.urlsafe_b64decode(encoded_key)
    
    # Initialize the form with the derived key for decryption
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST, instance=entry, derived_key=derived_key)
        if form.is_valid():
            form.save(derived_key=derived_key)  # Save with encryption
            messages.success(request, "Password entry updated successfully!", extra_tags="dashboard")
            return redirect('password_vault:vault_dashboard')
    else:
        form = PasswordEntryForm(instance=entry, derived_key=derived_key)  # Decrypt for display

    return render(request, 'password_vault/edit_entry.html', {'form': form})

# View to delete an existing password entry
@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(PasswordEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, "Password entry deleted successfully!", extra_tags="dashboard")
        return redirect('password_vault:vault_dashboard')
    return render(request, 'password_vault/delete_entry.html', {'entry': entry})

# View to display the vault dashboard with folders and entries
@login_required
def vault_dashboard(request):
    folders = Folder.objects.filter(user=request.user)
    entries = PasswordEntry.objects.filter(user=request.user, folder__isnull=True)

    derived_key = get_encryption_key(request)
    if not derived_key:
        return redirect('accounts:login')

    # Decrypt each entry's password
    for entry in entries:
        encrypted_data = {'ciphertext': entry.encrypted_password, 'iv': entry.iv, 'tag': entry.tag}
        try:
            entry.decrypted_password = decrypt_data(derived_key, encrypted_data)
        except Exception as e:
            entry.decrypted_password = None

    return render(request, 'password_vault/vault_dashboard.html', {'folders': folders, 'entries': entries})

from django.utils.dateformat import format as format_date

# View to retrieve entries for a specific folder
@login_required
def folder_entries(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    entries = PasswordEntry.objects.filter(folder=folder)
    
    entries_data = [
        {
            "id": entry.id,
            "title": entry.title or entry.username,  # Use title if available
            "username": entry.username,
            "created_at": format_date(entry.created_at, "Y-m-d H:i"),
            "modified_at": format_date(entry.modified_at, "Y-m-d H:i"),
        }
        for entry in entries
    ]

    return JsonResponse({"entries": entries_data})

# View to decrypt and return the password for a specific entry
@csrf_exempt
@require_POST
def view_password(request, entry_id):
    logger.info(f"Request to view password for entry ID {entry_id}")

    # Retrieve and decrypt the password
    try:
        entry = get_object_or_404(PasswordEntry, id=entry_id, user=request.user)
        derived_key = get_encryption_key(request)
        encrypted_data = {
            'ciphertext': entry.encrypted_password,
            'iv': entry.iv,
            'tag': entry.tag,
        }
        password = decrypt_data(derived_key, encrypted_data)
        return JsonResponse({'password': password})

    except Exception as e:
        logger.error(f"Error decrypting password for entry ID {entry_id}: {e}")
        return JsonResponse({'error': 'Unable to retrieve password.'}, status=500)

from django.http import JsonResponse