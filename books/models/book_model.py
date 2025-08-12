from django.db import models
from django.core.exceptions import ValidationError
from user.models import User
import uuid
import os


def validate_book_file(value):
    """
    Validate that uploaded file is either epub or txt
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.epub', '.txt']
    
    if ext not in valid_extensions:
        raise ValidationError(
            f'Only {", ".join(valid_extensions)} files are allowed. '
            f'Uploaded file has extension: {ext}'
        )


def book_upload_path(instance, filename):
    """Generate upload path for book files"""
    return f'books/user_{instance.user_id.id}/{filename}'


class Book(models.Model):
    """
    Model for storing uploaded books
    """
    book_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text="Book title")
    author = models.CharField(max_length=255, null=True, blank=True, help_text="Book author")
    description = models.TextField(null=True, blank=True, help_text="Book description")
    file = models.FileField(
        upload_to=book_upload_path, 
        validators=[validate_book_file],
        help_text="Book file (epub or txt)"
    )
    
    # Foreign key to User
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='books',
        help_text="User who uploaded the book"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'book'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['title']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author or 'Unknown'}"
    
    @property
    def file_size(self):
        """Get file size in bytes"""
        try:
            return self.file.size
        except:
            return 0
    
    @property
    def file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file.name)[1].lower() if self.file else None
