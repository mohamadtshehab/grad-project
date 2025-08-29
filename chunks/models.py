from django.db import models
from books.models import Book
import uuid


class Chunk(models.Model):
    """
    Model for storing text chunks extracted from books
    """
<<<<<<< HEAD
    chunk_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
=======
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    chunk_text = models.TextField(help_text="The actual text content of the chunk")
    chunk_number = models.IntegerField(help_text="Sequential number of the chunk within the book")
    
    # Foreign key to Book
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='chunks',
        help_text="Book this chunk belongs to"
    )
    
<<<<<<< HEAD
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
    
=======
>>>>>>> cdbf19e699fca259958993c6df6f4865ecc42e96
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chunk'
        ordering = ['book', 'chunk_number']
        unique_together = ['book', 'chunk_number']
        indexes = [
            models.Index(fields=['book']),
            models.Index(fields=['book', 'chunk_number']),
            models.Index(fields=['chunk_number']),
        ]
    
    def __str__(self):
        return f"Chunk {self.chunk_number} of {self.book.title}"
        
    def get_preview(self, length=100):
        """Get a preview of the chunk text"""
        if not self.chunk_text:
            return ""
        return self.chunk_text[:length] + "..." if len(self.chunk_text) > length else self.chunk_text
