from django.db import models
from django.conf import settings

class Folder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PasswordEntry(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)  # New title field
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries')
    username = models.CharField(max_length=255)
    url = models.URLField(max_length=2048, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Fields for encrypted password data
    encrypted_password = models.TextField()  # Stores encrypted password data
    iv = models.CharField(max_length=24)   # Stores the IV (initialization vector) for AES-GCM
    tag = models.CharField(max_length=24)  # Stores the GCM tag for encryption validation

    def __str__(self):
        return f"{self.username} ({self.url})"

    class Meta:
        ordering = ['-modified_at']  # Orders entries by most recently modified
