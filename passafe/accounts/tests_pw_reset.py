from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from accounts.models import CustomUser
from password_vault.models import PasswordEntry
from password_vault.utils import derive_key, encrypt_data, decrypt_data, generate_salt
import base64

class ResetPasswordViewTest(TestCase):
    def setUp(self):
        # Create a test user with known credentials
        self.old_password = "OldPassword123!"
        self.new_password = "NewPassword123!"
        self.current_pin_plain = "12345678"
        self.user = CustomUser.objects.create(
            username="test@example.com",
            email="test@example.com",
            name="Test",
            surname="User",
        )
        # Set the user's password and PIN using the appropriate functions
        self.user.password = make_password(self.old_password)
        self.user.set_pin(self.current_pin_plain)
        
        # Generate a salt and derive the initial encryption key using the old password and PIN
        salt = generate_salt()
        self.salt = salt  # Save for later verification
        self.user.salt = base64.urlsafe_b64encode(salt).decode()
        old_key = derive_key(self.old_password, self.current_pin_plain, salt)
        self.old_key = old_key  # Save the old key for later use in the test
        self.user.encryption_key = base64.urlsafe_b64encode(old_key).decode()
        self.user.save()

        # Create a vault entry for the user encrypted with the old key
        plaintext = "mysecret"
        encryption = encrypt_data(old_key, plaintext)
        self.vault_entry = PasswordEntry.objects.create(
            user=self.user,
            title="Test Entry",
            username="vaultuser",
            encrypted_password=encryption['ciphertext'],
            iv=encryption['iv'],
            tag=encryption['tag']
        )

        # Initialize the test client and simulate that the user has been verified
        self.client = Client()
        session = self.client.session
        session['verified_user_id'] = self.user.id
        session.save()

    def test_reset_password_success(self):
        url = reverse('accounts:reset_password')
        post_data = {
            'new_password': self.new_password,
            'confirm_password': self.new_password,
            'current_pin': self.current_pin_plain,
        }
        response = self.client.post(url, data=post_data)
        
        # Expect a redirect to the login page after successful reset
        self.assertEqual(response.status_code, 302)
        
        # Refresh the user from the database
        self.user.refresh_from_db()
        
        # Check that the user's password has been updated
        self.assertTrue(self.user.check_password(self.new_password))
        
        # Derive the new encryption key using the new password and the current PIN
        salt = base64.urlsafe_b64decode(self.user.salt.encode())
        new_key = derive_key(self.new_password, self.current_pin_plain, salt)
        stored_new_key = base64.urlsafe_b64decode(self.user.encryption_key.encode())
        self.assertEqual(new_key, stored_new_key)
        
        # Verify that the vault entry has been re-encrypted and can be decrypted using the new key
        self.vault_entry.refresh_from_db()
        decrypted = decrypt_data(new_key, {
            'ciphertext': self.vault_entry.encrypted_password,
            'iv': self.vault_entry.iv,
            'tag': self.vault_entry.tag,
        })
        self.assertEqual(decrypted, "mysecret")
