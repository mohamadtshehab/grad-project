from django.db import models
from django.core.exceptions import ValidationError
from user.models import User
import uuid
from django.core.files.base import ContentFile
import os
import ebooklib
from ebooklib import epub

def epub_to_raw_html_string(epub_path):
    """
    Opens an EPUB and concatenates the raw, unparsed HTML/XHTML source
    code of its content documents into a single string.
    """
    book = epub.read_epub(epub_path)
    html_parts = []

    # Find all the content documents (the chapters)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        # Get the raw byte content
        content_bytes = item.get_content()
        # Decode it into a string, KEEPING ALL TAGS
        content_string = content_bytes.decode('utf-8', errors='ignore')
        html_parts.append(content_string)
    
    # Join the raw HTML of each chapter with a separator
    return "\n\n\n\n".join(html_parts)

def validate_book_file(value):
    """
    Validate that uploaded file is EPUB only
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.epub']
    
    if ext not in valid_extensions:
        raise ValidationError(
            f'Only EPUB files are allowed. '
            f'Uploaded file has extension: {ext}'
        )

def book_upload_path(instance, filename):
    """Generate upload path for book files using book_id"""
    return f'books/book_{instance.book_id}/{filename}'

def txt_file_upload_path(instance, filename):
    return f"books/book_{instance.book_id}/{filename}"

class Book(models.Model):
    book_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Book title")
    author = models.CharField(max_length=255, null=True, blank=True, help_text="Book author")
    description = models.TextField(null=True, blank=True, help_text="Book description")
    detected_language = models.CharField(max_length=10, null=True, blank=True, help_text="Detected language code (e.g., 'ar', 'en')")
    language_confidence = models.FloatField(null=True, blank=True, help_text="Confidence score for language detection (0.0-1.0)")
    quality_score = models.FloatField(null=True, blank=True, help_text="Text quality assessment score (0.0-1.0)")
    text_classification = models.JSONField(null=True, blank=True, help_text="Text classification results (genre, confidence, etc.)")
    file = models.FileField(upload_to=book_upload_path, validators=[validate_book_file], help_text="Original book file (EPUB only)")
    processing_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', help_text="Processing status of the book")
    processing_error = models.TextField(null=True, blank=True, help_text="Error message if processing failed")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books', help_text="User who uploaded the book")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    txt_file = models.FileField(upload_to=book_upload_path, help_text="Converted text file (TXT only)", null=True, blank=True)

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
    
    @classmethod
    def get_file_path_by_id(cls, book_id: str) -> str:
        """
        Get the original EPUB file path for a book by its ID.
        
        Args:
            book_id: The UUID of the book
            
        Returns:
            The full file path to the original EPUB file
            
        Raises:
            Book.DoesNotExist: If book not found
            ValueError: If book has no file
        """
        try:
            book = cls.objects.get(book_id=book_id)
            if not book.file:
                raise ValueError(f"Book {book_id} has no file attached")
            return book.file.path
        except cls.DoesNotExist:
            raise cls.DoesNotExist(f"Book with ID {book_id} not found")