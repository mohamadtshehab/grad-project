from django.db import models
from books.models import Book
import uuid


class Chunk(models.Model):
    """
    Model for storing text chunks extracted from books
    """
    chunk_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chunk_text = models.TextField(help_text="The actual text content of the chunk")
    chunk_number = models.PositiveIntegerField(help_text="Sequential number of the chunk within the book")
    
    # Foreign key to Book
    book_id = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='chunks',
        help_text="Book this chunk belongs to"
    )
    
    # Additional metadata
    start_position = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Starting character position in the original text"
    )
    end_position = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Ending character position in the original text"
    )
    word_count = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Number of words in this chunk"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chunk'
        ordering = ['book_id', 'chunk_number']
        unique_together = ['book_id', 'chunk_number']
        indexes = [
            models.Index(fields=['book_id']),
            models.Index(fields=['book_id', 'chunk_number']),
            models.Index(fields=['chunk_number']),
        ]
    
    def __str__(self):
        return f"Chunk {self.chunk_number} of {self.book_id.title}"
    
    @property
    def character_count(self):
        """Get character count of the chunk"""
        return len(self.chunk_text) if self.chunk_text else 0
    
    def get_preview(self, length=100):
        """Get a preview of the chunk text"""
        if not self.chunk_text:
            return ""
        return self.chunk_text[:length] + "..." if len(self.chunk_text) > length else self.chunk_text
