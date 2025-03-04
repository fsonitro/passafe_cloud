from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

# Get the User model that's currently being used by the project
User = get_user_model()

class EmailBackend(BaseBackend):
    """
    Custom authentication backend that allows users to log in using their email address
    instead of username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user based on email address and password.
        
        Args:
            request: The HTTP request object
            username: The email address of the user (named username for compatibility)
            password: The password to verify
            **kwargs: Additional arguments that might be passed
        
        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            user = User.objects.get(email=username)  # Lookup user by email
        except User.DoesNotExist:
            return None
        
        # Verify the password and return user if valid
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        """
        Retrieve a User object by its primary key.
        
        Args:
            user_id: The primary key of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
