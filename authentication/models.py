from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
import string

User = get_user_model()

class PasswordResetCode(models.Model):
    """Model to store password reset codes for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_codes')
    code = models.CharField(max_length=6, help_text="6-digit reset code")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'code']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_used']),
        ]
    
    def __str__(self):
        return f"Reset code for {self.user.email} - {self.code}"
    
    @classmethod
    def generate_code(cls):
        """Generate a random 6-digit code"""
        return ''.join(random.choices(string.digits, k=6))
    
    @classmethod
    def create_for_user(cls, user, code_length=6, expiry_hours=1):
        """Create a new password reset code for a user"""
        # Invalidate any existing unused codes for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Generate new code
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(hours=expiry_hours)
        
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """Check if the code is valid (not expired and not used)"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark the code as used"""
        self.is_used = True
        self.save()
