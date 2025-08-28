# characters/models.py

import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from books.models import Book
from chunks.models import Chunk
import json

class UnicodeJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        # ensure_ascii=False keeps Unicode characters as-is (not escaped)
        kwargs['ensure_ascii'] = False
        super().__init__(*args, **kwargs)

class Character(models.Model):
    """
    Model for storing character profiles extracted by an AI workflow. 
    Each character is unique to a specific book.
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for each character."
    )
    
    # The custom encoder is removed as Django's JSONField handles Unicode well.
    golden_profile = models.JSONField(
        help_text="Flexible JSON data for the character's profile (e.g., name, age, personality).",
        encoder=UnicodeJSONEncoder
    )
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='characters',
        help_text="The book this character belongs to."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'character'
        ordering = ['book', 'created_at']
        indexes = [
            models.Index(fields=['book']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """Returns a human-readable representation of the character."""
        name = self.golden_profile.get('name', 'Unknown Character')
        return f"{name} in '{self.book.title}'"
    
    @property
    def name(self):
        """A convenient property to access the character's name from the JSON data."""
        return self.golden_profile.get('name', '') if self.golden_profile else ''


class ChunkCharacter(models.Model):
    """
    A through model linking a Character to a Chunk where they are mentioned.
    This acts as a many-to-many relationship with extra data.
    """
    chunk = models.ForeignKey(
        Chunk,
        on_delete=models.CASCADE,
    )
    
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='chunk_mentions'
    )
    
    character_profile = models.JSONField(
        help_text="Flexible JSON data for the character's profile (e.g., name, age, personality).",
        encoder=UnicodeJSONEncoder
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chunk_character'
        # This constraint ensures a character can only be linked to a chunk once.
        unique_together = ['chunk', 'character']
        ordering = ['chunk', 'character']
        indexes = [
            # Add an index on 'character' for efficient lookups of all chunks
            # a character appears in. The unique_together above already creates
            # an index that is efficient for lookups starting with 'chunk'.
            models.Index(fields=['character']),
        ]
    
    def __str__(self):
        return f"Mention of {self.character.name} in {self.chunk}"


class CharacterRelationship(models.Model):
    """
    Defines a relationship between two characters within the context of a single book.
    """

    # Using more descriptive field names like 'from_character' and 'to_character'
    chunk = models.ForeignKey(
        Chunk,
        on_delete=models.CASCADE,
    )
    
    from_character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='relationships_from',
        help_text="The source character in the relationship."
    )
    to_character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='relationships_to',
        help_text="The target character in the relationship."
    )
    
    relationship_type = models.CharField(
        max_length=50,
        help_text="The nature of the relationship."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'character_relationship'
        unique_together = ['from_character', 'to_character', 'chunk']
        ordering = ['chunk', 'from_character', 'to_character']
        constraints = [
            # Ensures a character cannot be related to themselves.
            models.CheckConstraint(
                check=~Q(from_character=F('to_character')),
                name='prevent_self_relationship'
            ),
            # Enforces a canonical order to prevent duplicate A->B and B->A entries.
            # Note: This requires character_id to be a comparable type like UUID or Integer.
            models.CheckConstraint(
                check=Q(from_character__lt=F('to_character')),
                name='canonical_character_order'
            )
        ]

    def clean(self):
        """
        Custom validation to enforce canonical order before saving.
        This makes it user-friendly by auto-swapping if entered in non-canonical order.
        """
        if self.from_character and self.to_character:
            # Enforce that both characters belong to the same book
            if self.from_character.book != self.to_character.book:
                raise ValidationError("Both characters must belong to the same book.")
            
            # Automatically swap characters to maintain canonical order (from.id < to.id)
            # We use the string representation of UUIDs for comparison
            if str(self.from_character.pk) > str(self.to_character.pk):
                self.from_character, self.to_character = self.to_character, self.from_character
                
