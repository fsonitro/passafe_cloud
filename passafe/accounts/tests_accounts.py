from django.test import TestCase, Client
from .models import CustomUser
import base64
import pyotp

# Create a new test case called CustomUserPinTest that extends the TestCase class
class CustomUserPinTest(TestCase):
    def setUp(self):
        # Create a test user with a raw PIN
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword"
        )
        self.raw_pin = "12345678"  # Raw PIN to be hashed
        self.user.set_pin(self.raw_pin)
        self.user.mfa_enabled = True
        self.user.mfa_secret = pyotp.random_base32()
        self.user.salt = base64.urlsafe_b64encode(b"testsalt").decode()
        self.user.save()

        self.client = Client()

    def test_pin_is_hashed(self):
        """Test that the PIN is hashed and not stored as plaintext."""
        self.assertNotEqual(self.user.pin, self.raw_pin)
        self.assertTrue(self.user.pin.startswith("pbkdf2_sha256$"))  # Check if it's using Django's default hashing

    # Define a test method called test_pin_validation_success
    def test_pin_validation_success(self):
        """Test that the hashed PIN can be successfully validated."""
        self.assertTrue(self.user.check_pin(self.raw_pin))

    # Define a test method called test_pin_validation_failure
    def test_pin_validation_failure(self):
        """Test that an incorrect PIN fails validation."""
        self.assertFalse(self.user.check_pin("87654321"))

    # Define a test method called test_pin_update
    def test_pin_update(self):
        """Test that updating the PIN works correctly."""
        new_pin = "87654321"
        self.user.set_pin(new_pin)
        self.user.save()

        self.assertTrue(self.user.check_pin(new_pin))
        self.assertFalse(self.user.check_pin(self.raw_pin))

    # Define a test method called test_register_with_pin
    def test_register_with_pin(self):
        """Test user registration with a PIN."""
        user = CustomUser.objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="anotherpassword"
        )
        user.set_pin("88888888")
        user.save()

        self.assertTrue(user.check_pin("88888888"))
        self.assertFalse(user.check_pin("12345678"))

    # Define a test method called test_login_with_pin
    def test_session_data_after_login(self):
        """Test that session data is set correctly after login."""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser@example.com',
            'password': 'securepassword',
            'pin': self.raw_pin
        })

        # Check redirection to MFA
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/verify-mfa/')

        # Verify session data
        session = self.client.session
        self.assertIn('mfa_user_id', session)
        self.assertIn('password', session)
        self.assertIn('pin', session)
        self.assertEqual(session['mfa_user_id'], self.user.id)

    # Define a test method called test_mfa_verification
    def test_session_data_after_mfa_verification(self):
        """Test that session data is cleared after successful MFA verification."""
        # Simulate login and session setup
        self.client.post('/accounts/login/', {
            'username': 'testuser@example.com',
            'password': 'securepassword',
            'pin': self.raw_pin
        })

        # Generate a valid MFA code
        totp = pyotp.TOTP(self.user.mfa_secret)
        valid_mfa_code = totp.now()

        # Verify MFA
        response = self.client.post('/accounts/verify-mfa/', {
            'mfa_code': valid_mfa_code
        })

        # Check redirection to the homepage
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

        # Verify session data is cleared
        session = self.client.session
        self.assertNotIn('mfa_user_id', session)
        self.assertNotIn('password', session)
        self.assertNotIn('pin', session)
