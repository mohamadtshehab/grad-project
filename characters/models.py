from django.db import models
from django.core.exceptions import ValidationError
from books.models import Book
from chunks.models import Chunk
import uuid
import json

class UnicodeJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        # ensure_ascii=False keeps Unicode characters as-is (not escaped)
        kwargs['ensure_ascii'] = False
        super().__init__(*args, **kwargs)
        
class Character(models.Model):
    """
    Model for storing character profiles extracted by AI workflow
    """
    character_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Character data stored as JSON for flexibility
    character_data = models.JSONField(
        help_text="Character profile data including name, age, role, physical_characteristics, personality, events, relationships, aliases",
        encoder=UnicodeJSONEncoder
    )
    
    # Foreign key to Book
    book_id = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='characters',
        help_text="Book this character appears in"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'character'
        ordering = ['book_id', 'created_at']
        indexes = [
            models.Index(fields=['book_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        name = self.character_data.get('name', 'Unknown') if self.character_data else 'Unknown'
        return f"{name} in {self.book_id.title}"
    
    @property
    def name(self):
        """Get character name from JSON data"""
        return self.character_data.get('name', '') if self.character_data else ''
    
    @property
    def role(self):
        """Get character role from JSON data"""
        return self.character_data.get('role', '') if self.character_data else ''
    
    @property
    def age(self):
        """Get character age from JSON data"""
        return self.character_data.get('age', '') if self.character_data else ''
    
    def to_dict(self):
        """Convert character to dictionary format for AI workflow"""
        return {
            'id': str(self.character_id),
            'profile': self.character_data or {}
        }
    
    @classmethod
    def from_ai_workflow(cls, book, character_data):
        """Create character from AI workflow data"""
        return cls.objects.create(
            book_id=book,
            character_data=character_data
        )
    
    def update_from_ai_workflow(self, character_data):
        """Update character from AI workflow data"""
        self.character_data = character_data
        self.save()
        return self


class ChunkCharacter(models.Model):
    """
    Junction table linking characters to chunks with mention details
    """
    # Composite primary key using chunk_id and character_id
    chunk_id = models.ForeignKey(
        Chunk,
        on_delete=models.CASCADE,
        related_name='character_mentions',
        help_text="Chunk where character is mentioned"
    )
    character_id = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='chunk_mentions',
        help_text="Character being mentioned"
    )
    
    mention_count = models.PositiveIntegerField(
        default=1,
        help_text="Number of times character is mentioned in this chunk"
    )
    position_info = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON data containing position information of mentions within the chunk"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chunk_character'
        unique_together = ['chunk_id', 'character_id']
        ordering = ['chunk_id', 'character_id']
        indexes = [
            models.Index(fields=['chunk_id']),
            models.Index(fields=['character_id']),
            models.Index(fields=['chunk_id', 'character_id']),
        ]
    
    def __str__(self):
        return f"{self.character_id.name} in {self.chunk_id}"
    
    @property
    def character_name(self):
        """Get character name"""
        return self.character_id.name
    
    @property
    def chunk_number(self):
        """Get chunk number"""
        return self.chunk_id.chunk_number


class CharacterRelationship(models.Model):
    """
    Model for storing relationships between characters
    """
    RELATIONSHIP_TYPES = [
        ('family', 'Family'),
        ('friend', 'Friend'),
        ('enemy', 'Enemy'),
        ('romantic', 'Romantic'),
        ('colleague', 'Colleague'),
        ('mentor', 'Mentor'),
        ('student', 'Student'),
        ('ally', 'Ally'),
        ('rival', 'Rival'),
        ('other', 'Other'),
    ]
    
    character_id_1 = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='relationships_as_character_1',
        help_text="First character in the relationship"
    )
    character_id_2 = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='relationships_as_character_2',
        help_text="Second character in the relationship"
    )
    
    relationship_type = models.CharField(
        max_length=50,
        choices=RELATIONSHIP_TYPES,
        help_text="Type of relationship between characters"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the relationship"
    )
    
    # Foreign key to Book (relationships are book-specific)
    book_id = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='character_relationships',
        help_text="Book where this relationship exists"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'character_relationship'
        unique_together = ['character_id_1', 'character_id_2', 'book_id']
        ordering = ['book_id', 'character_id_1', 'character_id_2']
        indexes = [
            models.Index(fields=['character_id_1']),
            models.Index(fields=['character_id_2']),
            models.Index(fields=['book_id']),
            models.Index(fields=['relationship_type']),
        ]
    
    def __str__(self):
        return f"{self.character_id_1.name} - {self.relationship_type} - {self.character_id_2.name}"
    
    def clean(self):
        """Validate that a character cannot have a relationship with itself"""
        if self.character_id_1 == self.character_id_2:
            raise ValidationError("A character cannot have a relationship with itself")
    
    @property
    def character_1_name(self):
        """Get first character name"""
        return self.character_id_1.name
    
    @property
    def character_2_name(self):
        """Get second character name"""
        return self.character_id_2.name
