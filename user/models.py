from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from utils.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """
    Custom User model extending Django's AbstractUser
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="User's full name")
    email = models.EmailField(unique=True, help_text="User's email address")
    
    # Remove username field since we're using email as the unique identifier
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'user'
        ordering = ['name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
