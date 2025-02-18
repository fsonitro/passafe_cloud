from django import forms
from .models import Folder, PasswordEntry
from .utils import decrypt_data, encrypt_data
import base64

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter folder name'
            }),
        }

class PasswordEntryForm(forms.ModelForm):
    # Field to display and edit the decrypted password
    password_entry = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),  # Display the password as plain text for editing
        required=True,
        label="Password"
    )

    class Meta:
        model = PasswordEntry
        fields = ['title','username', 'password_entry', 'url', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter title (e.g., My Email Account)'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter URL'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notes',
                'rows': 3
            }),
        }

    def __init__(self, *args, derived_key=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Decrypt the password only for the `password_entry` field
        if self.instance and self.instance.pk and derived_key:
            try:
                encrypted_data = {
                    'ciphertext': self.instance.encrypted_password,
                    'iv': self.instance.iv,
                    'tag': self.instance.tag
                }
                decrypted_password = decrypt_data(derived_key, encrypted_data)
                self.fields['password_entry'].initial = decrypted_password
            except Exception as e:
                print(f"Error decrypting password for editing: {e}")
                self.fields['password_entry'].initial = ""  # Show blank if decryption fails

    def save(self, commit=True, derived_key=None):
        entry = super().save(commit=False)
        
        # Encrypt only `password_entry` and save to `encrypted_password` field
        if derived_key and 'password_entry' in self.cleaned_data:
            encrypted_data = encrypt_data(derived_key, self.cleaned_data['password_entry'])
            entry.encrypted_password = encrypted_data['ciphertext']
            entry.iv = encrypted_data['iv']
            entry.tag = encrypted_data['tag']
        
        if commit:
            entry.save()
        return entry
