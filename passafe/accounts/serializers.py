from rest_framework import serializers
from django.contrib.auth import get_user_model
import bcrypt
# Import the User model from Django

User = get_user_model()
# Create a new class called RegisterSerializer that extends the ModelSerializer class
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        
    # Define a create method that takes in validated data
    def create(self, validated_data):
        password = validated_data.pop('password')
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = User(**validated_data)
        user.password = hashed_password.decode()
        user.save()
        return user
