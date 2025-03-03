from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import PasswordEntry
from .utils import encrypt_data, decrypt_data

class PasswordEntryEncryptionTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass",
            pin="1234"
        )

        # Define a fixed 32-byte key for AES-256
        self.derived_key = b'12345678901234567890123456789012'  # Exactly 32 bytes

        # Confirm the length of the derived key for debugging purposes
        assert len(self.derived_key) == 32, f"Key length is {len(self.derived_key)} bytes, expected 32 bytes."

    def test_password_encryption_on_save(self):
        # Test data
        password_entry = PasswordEntry(
            user=self.user,
            username="test_entry",
            url="http://example.com",
            notes="Sample note"
        )

        # Encrypt password and save entry
        encrypted_data = encrypt_data(self.derived_key, "sample_password")
        password_entry.encrypted_password = encrypted_data['ciphertext']
        password_entry.iv = encrypted_data['iv']
        password_entry.tag = encrypted_data['tag']
        password_entry.save()

        # Retrieve and decrypt
        saved_entry = PasswordEntry.objects.get(id=password_entry.id)
        decrypted_password = decrypt_data(self.derived_key, {
            'ciphertext': saved_entry.encrypted_password,
            'iv': saved_entry.iv,
            'tag': saved_entry.tag
        })
        self.assertEqual(decrypted_password, "sample_password")

    def test_edit_password_entry(self):
        # Initial save with encryption
        password_entry = PasswordEntry(
            user=self.user,
            username="test_edit",
            url="http://example-edit.com",
            notes="Editable note"
        )
        encrypted_data = encrypt_data(self.derived_key, "original_password")
        password_entry.encrypted_password = encrypted_data['ciphertext']
        password_entry.iv = encrypted_data['iv']
        password_entry.tag = encrypted_data['tag']
        password_entry.save()

        # Retrieve and update
        saved_entry = PasswordEntry.objects.get(id=password_entry.id)
        new_encrypted_data = encrypt_data(self.derived_key, "updated_password")
        saved_entry.encrypted_password = new_encrypted_data['ciphertext']
        saved_entry.iv = new_encrypted_data['iv']
        saved_entry.tag = new_encrypted_data['tag']
        saved_entry.save()

        # Verify the updated password
        updated_entry = PasswordEntry.objects.get(id=password_entry.id)
        decrypted_password = decrypt_data(self.derived_key, {
            'ciphertext': updated_entry.encrypted_password,
            'iv': updated_entry.iv,
            'tag': updated_entry.tag
        })
        self.assertEqual(decrypted_password, "updated_password")
